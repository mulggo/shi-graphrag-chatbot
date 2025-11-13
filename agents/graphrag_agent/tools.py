"""
GraphRAG Tools - Lambda function wrappers using Strands @tool decorator

이 모듈은 Lambda 함수를 Strands 도구로 래핑합니다.
각 도구는 @tool 데코레이터를 사용하여 정의되며, ToolContext를 통해 invocation_state에 접근합니다.

Requirements: 7.5-7.10
"""
import boto3
import json
import logging
from typing import Dict, List, Any
from botocore.exceptions import ClientError
import time

from strands import tool
from strands.types.tools import ToolContext

from .metrics import get_metrics

# 로깅 설정
logger = logging.getLogger(__name__)

# 메트릭 수집기
metrics = get_metrics()


@tool(context=True)
def extract_entities(question: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    질문에서 주요 엔티티, 개념, 키워드를 추출합니다.
    
    이 도구는 Lambda 함수를 호출하여 Bedrock Claude 모델을 사용해 질문을 분석하고
    검색에 유용한 엔티티, 개념, 한국어/영어 키워드를 추출합니다.
    
    Args:
        question: 분석할 사용자 질문
        tool_context: Strands ToolContext (자동 주입)
        
    Returns:
        Dict: {
            "entities": List[str],      # 주요 엔티티 (시스템, 장비 등)
            "concepts": List[str],       # 핵심 개념 (용량, 요구사항 등)
            "keywords_ko": List[str],    # 한국어 검색 키워드
            "keywords_en": List[str],    # 영어 검색 키워드
            "related_docs": List[str]    # 관련 문서 유형
        }
    """
    start_time = time.time()
    success = False
    
    try:
        # invocation_state에서 Lambda 함수 ARN 가져오기
        lambda_arn = tool_context.invocation_state.get('lambda_extract_entities_arn')
        if not lambda_arn:
            raise ValueError("lambda_extract_entities_arn이 invocation_state에 없습니다")
        
        # Lambda 클라이언트 초기화
        lambda_client = boto3.client('lambda')
        
        # Lambda 페이로드 구성
        payload = {
            'question': question
        }
        
        logger.info(f"extract_entities 호출: question='{question[:50]}...'")
        
        # Lambda 함수 호출 (재시도 포함)
        result = _invoke_lambda_with_retry(
            lambda_client=lambda_client,
            function_name=lambda_arn,
            payload=payload,
            max_retries=3
        )
        
        success = True
        duration = time.time() - start_time
        
        # 메트릭 기록
        metrics.record_lambda_invocation('extract_entities', duration, success)
        
        logger.info(f"extract_entities 성공: entities={len(result.get('entities', []))}, keywords={len(result.get('keywords_ko', []))+len(result.get('keywords_en', []))}, duration={duration:.2f}s")
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        
        # 메트릭 기록 (실패)
        metrics.record_lambda_invocation('extract_entities', duration, success)
        metrics.record_error('lambda_error', 'query_analysis')
        
        logger.error(f"extract_entities 실패: {str(e)}, duration={duration:.2f}s")
        
        # 에러 발생 시 기본값 반환 - 질문에서 단어 추출
        words = question.split()
        return {
            "entities": words[:3] if len(words) >= 3 else words,
            "concepts": [],
            "keywords_ko": words,
            "keywords_en": [],
            "related_docs": []
        }


@tool(context=True)
def kb_retrieve(query: str, tool_context: ToolContext, num_results: int = 10) -> Dict[str, Any]:
    """
    Bedrock Knowledge Base에서 문서를 검색하고 reranking을 수행합니다.
    
    이 도구는 Lambda 함수를 호출하여 Bedrock KB Retrieve API를 사용해
    관련 문서 청크를 검색하고, reranker 모델로 관련성을 재평가합니다.
    
    Args:
        query: 검색 쿼리 (한국어 또는 영어)
        num_results: 검색할 청크 수 (기본값: 10)
        tool_context: Strands ToolContext (자동 주입)
        
    Returns:
        Dict: {
            "chunks": List[Dict],       # 검색된 문서 청크
            "total_retrieved": int,     # 검색된 총 청크 수
            "reranked": bool,           # reranking 수행 여부
            "query": str,               # 검색 쿼리
            "duration": float           # 검색 소요 시간 (초)
        }
        
        각 chunk는 다음 구조를 가집니다:
        {
            "text": str,        # 청크 텍스트
            "score": float,     # 관련성 점수
            "source": str,      # S3 URI
            "page": int         # 페이지 번호
        }
    """
    start_time = time.time()
    success = False
    
    try:
        # invocation_state에서 필요한 정보 가져오기
        lambda_arn = tool_context.invocation_state.get('lambda_kb_retrieve_arn')
        kb_id = tool_context.invocation_state.get('kb_id')
        reranker_model_arn = tool_context.invocation_state.get('reranker_model_arn')
        
        if not lambda_arn:
            raise ValueError("lambda_kb_retrieve_arn이 invocation_state에 없습니다")
        if not kb_id:
            raise ValueError("kb_id가 invocation_state에 없습니다")
        
        # Lambda 클라이언트 초기화
        lambda_client = boto3.client('lambda')
        
        # Lambda 페이로드 구성
        payload = {
            'query': query,
            'num_results': num_results,
            'rerank': True if reranker_model_arn else False,
            'kb_id': kb_id
        }
        
        # reranker_model_arn이 있으면 추가
        if reranker_model_arn:
            payload['reranker_model_arn'] = reranker_model_arn
        
        logger.info(f"kb_retrieve 호출: query='{query[:50]}...', num_results={num_results}, rerank={payload['rerank']}")
        
        # Lambda 함수 호출 (재시도 포함)
        result = _invoke_lambda_with_retry(
            lambda_client=lambda_client,
            function_name=lambda_arn,
            payload=payload,
            max_retries=3
        )
        
        success = True
        duration = time.time() - start_time
        
        # 메트릭 기록
        metrics.record_lambda_invocation('kb_retrieve', duration, success)
        
        logger.info(f"kb_retrieve 성공: retrieved={result.get('total_retrieved')}, reranked={result.get('reranked')}, duration={result.get('duration', 0):.2f}s")
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        
        # 메트릭 기록 (실패)
        metrics.record_lambda_invocation('kb_retrieve', duration, success)
        metrics.record_error('lambda_error', 'retrieval')
        
        logger.error(f"kb_retrieve 실패: {str(e)}, duration={duration:.2f}s")
        
        # 에러 발생 시 빈 결과 반환
        return {
            "chunks": [],
            "total_retrieved": 0,
            "reranked": False,
            "query": query,
            "duration": 0.0,
            "error": str(e)
        }


def _invoke_lambda_with_retry(
    lambda_client,
    function_name: str,
    payload: Dict,
    max_retries: int = 3
) -> Dict:
    """
    Exponential backoff를 사용한 Lambda 함수 호출 재시도 로직
    
    이 함수는 Lambda 함수를 호출하고, 실패 시 지수 백오프를 사용하여 재시도합니다.
    TooManyRequestsException, ThrottlingException 등의 일시적 에러에 대해 재시도합니다.
    
    Args:
        lambda_client: Boto3 Lambda 클라이언트
        function_name: Lambda 함수 이름 또는 ARN
        payload: Lambda 함수에 전달할 페이로드
        max_retries: 최대 재시도 횟수 (기본값: 3)
        
    Returns:
        Dict: Lambda 함수 응답
        
    Raises:
        Exception: 모든 재시도 실패 시
    """
    delay = 1.0  # 초기 대기 시간 (초)
    
    for attempt in range(max_retries):
        try:
            # Lambda 함수 호출
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # 응답 파싱
            result = json.loads(response['Payload'].read())
            
            # Lambda 함수 내부 에러 확인
            if 'errorMessage' in result:
                error_type = result.get('errorType', 'Unknown')
                error_message = result['errorMessage']
                logger.warning(f"Lambda 함수 에러 (시도 {attempt + 1}/{max_retries}): {error_type}: {error_message}")
                
                # 재시도 가능한 에러인지 확인
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                else:
                    raise Exception(f"Lambda 함수 에러: {error_type}: {error_message}")
            
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.warning(f"AWS 클라이언트 에러 (시도 {attempt + 1}/{max_retries}): {error_code}")
            
            # 재시도 가능한 에러 확인
            if error_code in ['TooManyRequestsException', 'ThrottlingException', 'ServiceUnavailable']:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
            
            # 재시도 불가능한 에러 또는 마지막 시도
            raise
        
        except Exception as e:
            logger.warning(f"일반 에러 (시도 {attempt + 1}/{max_retries}): {str(e)}")
            
            # 마지막 시도가 아니면 재시도
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            
            raise
    
    raise Exception(f"Lambda 호출이 {max_retries}번의 재시도 후 실패했습니다: {function_name}")
