"""
kb_retrieve Lambda Function

Bedrock Knowledge Base에서 문서를 검색하고 reranking을 수행하는 Lambda 함수
"""

import json
import boto3
import os
import logging
import time
from typing import Dict, Any, List, Optional

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrock Agent Runtime 클라이언트 초기화
bedrock_agent_runtime = boto3.client(
    'bedrock-agent-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-west-2')
)


def retrieve_from_kb(
    query: str,
    kb_id: str,
    num_results: int = 5,
    rerank: bool = True,
    reranker_model_arn: Optional[str] = None
) -> Dict[str, Any]:
    """
    Bedrock KB Retrieve API를 호출하여 문서 검색 및 reranking
    
    Args:
        query: 검색 쿼리
        kb_id: Knowledge Base ID
        num_results: 검색할 청크 수
        rerank: reranking 활성화 여부
        reranker_model_arn: Reranker 모델 ARN
        
    Returns:
        검색 결과 딕셔너리
    """
    try:
        # Retrieve API 구성
        retrieval_config = {
            'vectorSearchConfiguration': {
                'numberOfResults': num_results
            }
        }
        
        # Reranking 설정 추가 (항상 5개로 고정)
        if rerank and reranker_model_arn:
            retrieval_config['vectorSearchConfiguration']['rerankingConfiguration'] = {
                'type': 'BEDROCK_RERANKING_MODEL',
                'bedrockRerankingConfiguration': {
                    'numberOfRerankedResults': 5,  # 항상 5개로 고정
                    'modelConfiguration': {
                        'modelArn': reranker_model_arn
                    }
                }
            }
        
        # Bedrock KB Retrieve API 호출
        logger.info(f"KB 검색 시작: query='{query[:50]}...', num_results={num_results}, rerank={rerank}")
        
        start_time = time.time()
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': query},
            retrievalConfiguration=retrieval_config
        )
        duration = time.time() - start_time
        
        logger.info(f"KB 검색 완료: duration={duration:.2f}s")
        
        # 결과 처리
        chunks = []
        for idx, result in enumerate(response.get('retrievalResults', [])):
            # 디버깅: 전체 result 구조 로깅
            logger.info(f"Result {idx}: {json.dumps(result, default=str)[:500]}")
            
            # 메타데이터 추출
            metadata = result.get('metadata', {})
            location = result.get('location', {})
            s3_location = location.get('s3Location', {})
            
            # content 구조 확인
            content = result.get('content', {})
            logger.info(f"Content structure for result {idx}: type={content.get('type')}, keys={list(content.keys())}")
            
            # text 추출 (여러 가능성 고려)
            text = ''
            if 'text' in content:
                text = content['text']
            elif 'byteContent' in content:
                # byteContent가 있는 경우 디코딩 시도
                try:
                    import base64
                    text = base64.b64decode(content['byteContent']).decode('utf-8')
                except Exception as e:
                    logger.warning(f"Failed to decode byteContent: {e}")
                    text = ''
            
            chunk = {
                'text': text,
                'score': result.get('score', 0.0),
                'source': s3_location.get('uri', ''),
                'page': int(metadata.get('x-amz-bedrock-kb-document-page-number', 0))
            }
            
            # 추가 메타데이터
            if 'x-amz-bedrock-kb-source-uri' in metadata:
                chunk['source_uri'] = metadata['x-amz-bedrock-kb-source-uri']
            
            chunks.append(chunk)
        
        # 점수 기준 정렬 (높은 점수 우선)
        chunks.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'chunks': chunks,
            'total_retrieved': len(chunks),
            'reranked': rerank,
            'query': query,
            'duration': duration
        }
        
    except Exception as e:
        logger.error(f"KB 검색 실패: {str(e)}")
        raise


def retry_with_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """
    Exponential backoff를 사용한 재시도 로직
    
    Args:
        func: 실행할 함수
        max_retries: 최대 재시도 횟수
        initial_delay: 초기 대기 시간 (초)
        backoff_factor: 백오프 배수
        
    Returns:
        함수 실행 결과
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # TooManyRequestsException 등 재시도 가능한 에러 확인
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', '')
            if error_code in ['TooManyRequestsException', 'ThrottlingException', 'ServiceUnavailable']:
                logger.warning(f"재시도 {attempt + 1}/{max_retries}: {error_code}, {delay}초 대기")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                raise


def lambda_handler(event, context):
    """
    Lambda 핸들러
    
    Input event:
        {
            "query": str - 검색 쿼리,
            "num_results": int - 검색할 청크 수 (기본값: 10),
            "rerank": bool - reranking 활성화 (기본값: true),
            "kb_id": str - Knowledge Base ID (선택, 환경변수 사용 가능),
            "reranker_model_arn": str - Reranker 모델 ARN (선택, 환경변수 사용 가능)
        }
    
    Output:
        {
            "chunks": List[Dict],
            "total_retrieved": int,
            "reranked": bool,
            "query": str,
            "duration": float
        }
        
    Error Output:
        {
            "errorMessage": str,
            "errorType": str
        }
    """
    # 요청 로깅
    logger.info(json.dumps({
        "event": "lambda_invocation",
        "function": context.function_name if context else "unknown",
        "request_id": context.aws_request_id if context else "unknown",
        "input": {k: v for k, v in event.items() if k != 'reranker_model_arn'}  # ARN 제외
    }))
    
    try:
        # 입력 검증
        if 'query' not in event:
            raise ValueError("'query' 필드가 필요합니다")
        
        query = event['query']
        num_results = event.get('num_results', 5)
        rerank = event.get('rerank', True)
        kb_id = event.get('kb_id', os.environ.get('BEDROCK_KB_ID'))
        reranker_model_arn = event.get('reranker_model_arn', os.environ.get('RERANKER_MODEL_ARN'))
        
        # KB ID 검증
        if not kb_id:
            raise ValueError("Knowledge Base ID가 필요합니다 (event 또는 환경변수)")
        
        # Reranking 사용 시 모델 ARN 검증
        if rerank and not reranker_model_arn:
            logger.warning("Reranker 모델 ARN이 없어 reranking을 비활성화합니다")
            rerank = False
        
        # KB 검색 (재시도 로직 포함)
        result = retry_with_backoff(
            lambda: retrieve_from_kb(
                query=query,
                kb_id=kb_id,
                num_results=num_results,
                rerank=rerank,
                reranker_model_arn=reranker_model_arn
            )
        )
        
        # 성공 로깅
        logger.info(json.dumps({
            "event": "lambda_success",
            "function": context.function_name,
            "total_retrieved": result['total_retrieved'],
            "reranked": result['reranked'],
            "duration": result['duration']
        }))
        
        return result
        
    except Exception as e:
        # 에러 로깅
        logger.error(json.dumps({
            "event": "lambda_error",
            "function": context.function_name,
            "error": str(e),
            "error_type": type(e).__name__
        }))
        
        return {
            "errorMessage": str(e),
            "errorType": type(e).__name__,
            "chunks": [],
            "total_retrieved": 0,
            "reranked": False
        }
