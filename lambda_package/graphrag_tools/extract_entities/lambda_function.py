"""
extract_entities Lambda Function

질문에서 주요 엔티티, 개념, 관계를 추출하는 Lambda 함수
"""

import json
import boto3
import os
import logging
from typing import Dict, Any, List

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrock 클라이언트 초기화
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-west-2'))

# 엔티티 추출 프롬프트
ENTITY_EXTRACTION_PROMPT = """당신은 선박 소방 규정 전문가입니다. 사용자 질문에서 다음 정보를 추출하세요:

1. **entities**: 주요 엔티티 (시스템, 장비, 구조물 등)
2. **concepts**: 핵심 개념 (용량, 요구사항, 절차 등)
3. **keywords_ko**: 한국어 검색 키워드
4. **keywords_en**: 영어 검색 키워드
5. **related_docs**: 관련 가능성이 높은 문서 유형

<context>
Knowledge Base 문서:
- SOLAS Chapter II-2 (국제 해상 안전 규정)
- FSS 합본 (Fire Safety Systems Code)
- IGC Code (International Code for Gas Carriers)
- DNV-RU-SHIP Pt4 Ch6, Pt6 Ch5 Sec4 (선급 규칙)
- Design guidance (설계 지침: Support, Spoolcutting, hull penetration)
- Piping practice (실무 문서: Support, hull penetration)
- SOLAS 2017 Insulation penetration
</context>

<question>
{question}
</question>

다음 JSON 형식으로만 응답하세요:
{{
  "entities": ["엔티티1", "엔티티2", ...],
  "concepts": ["개념1", "개념2", ...],
  "keywords_ko": ["키워드1", "키워드2", ...],
  "keywords_en": ["keyword1", "keyword2", ...],
  "related_docs": ["문서유형1", "문서유형2", ...]
}}

예시:
질문: "고정식 CO2 소화 시스템의 최소 용량은?"
응답:
{{
  "entities": ["고정식 CO2 소화 시스템", "CO2 system", "fixed installation"],
  "concepts": ["최소 용량", "minimum capacity", "요구사항"],
  "keywords_ko": ["고정식 CO2", "이산화탄소", "용량", "소화 시스템"],
  "keywords_en": ["fixed CO2 system", "minimum capacity", "fire fighting"],
  "related_docs": ["FSS Code", "SOLAS Chapter II-2"]
}}"""


def extract_entities(question: str, model_id: str) -> Dict[str, Any]:
    """
    Bedrock을 사용하여 엔티티 추출
    
    Args:
        question: 사용자 질문
        model_id: Bedrock 모델 ID
        
    Returns:
        추출된 엔티티 정보
    """
    prompt = ENTITY_EXTRACTION_PROMPT.format(question=question)
    
    # Claude 3.5 Sonnet 요청 페이로드
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.0,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # JSON 파싱
        result = json.loads(content)
        
        return {
            "entities": result.get("entities", []),
            "concepts": result.get("concepts", []),
            "keywords_ko": result.get("keywords_ko", []),
            "keywords_en": result.get("keywords_en", []),
            "related_docs": result.get("related_docs", [])
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 실패: {str(e)}, content: {content}")
        # 기본값 반환 - 질문에서 단어 추출
        words = question.split()
        return {
            "entities": words[:3] if len(words) >= 3 else words,
            "concepts": [],
            "keywords_ko": words,
            "keywords_en": [],
            "related_docs": []
        }
    except Exception as e:
        logger.error(f"엔티티 추출 실패: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Lambda 핸들러
    
    Input event:
        {
            "question": str - 사용자 질문
        }
    
    Output:
        {
            "entities": List[str],
            "concepts": List[str],
            "keywords_ko": List[str],
            "keywords_en": List[str],
            "related_docs": List[str]
        }
    """
    # 요청 로깅
    logger.info(json.dumps({
        "event": "lambda_invocation",
        "function": context.function_name if context else "unknown",
        "request_id": context.aws_request_id if context else "unknown",
        "input": event
    }))
    
    try:
        # 입력 검증
        if 'question' not in event:
            raise ValueError("'question' 필드가 필요합니다")
        
        question = event['question']
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        
        # 엔티티 추출
        result = extract_entities(question, model_id)
        
        # 성공 로깅
        logger.info(json.dumps({
            "event": "lambda_success",
            "function": context.function_name,
            "entities_count": len(result['entities']),
            "keywords_count": len(result['keywords_ko']) + len(result['keywords_en'])
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
            "errorType": type(e).__name__
        }
