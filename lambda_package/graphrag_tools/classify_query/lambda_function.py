"""
classify_query Lambda Function

질문 유형을 분류하는 Lambda 함수
- 사실 확인 (factual)
- 관계 탐색 (relational)
- 다중 문서 추론 (multi_doc)
- 비교 분석 (comparative)
"""

import json
import boto3
import os
import logging
from typing import Dict, Any

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrock 클라이언트 초기화
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-west-2'))

# 질문 분류 프롬프트
CLASSIFICATION_PROMPT = """당신은 선박 소방 규정 전문가입니다. 사용자 질문을 다음 4가지 유형 중 하나로 분류하세요:

1. **factual**: 특정 사실이나 요구사항을 묻는 질문
   예: "고정식 CO2 소화 시스템의 최소 용량은?"

2. **relational**: 개념 간 관계나 연결을 묻는 질문
   예: "스프링클러 시스템과 화재 감지 시스템의 관계는?"

3. **multi_doc**: 여러 문서나 규정을 참조해야 하는 질문
   예: "DNV 규정과 SOLAS 규정의 차이점은?"

4. **comparative**: 두 가지 이상을 비교하는 질문
   예: "배관 지지대 설계 가이드와 실제 시공 방법을 비교해줘"

<question>
{question}
</question>

다음 JSON 형식으로만 응답하세요:
{{
  "question_type": "factual|relational|multi_doc|comparative",
  "confidence": 0.0-1.0,
  "reasoning": "분류 이유를 한 문장으로"
}}"""


def classify_question(question: str, model_id: str) -> Dict[str, Any]:
    """
    Bedrock을 사용하여 질문 유형 분류
    
    Args:
        question: 사용자 질문
        model_id: Bedrock 모델 ID
        
    Returns:
        분류 결과 딕셔너리
    """
    prompt = CLASSIFICATION_PROMPT.format(question=question)
    
    # Claude 3.5 Sonnet 요청 페이로드
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
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
            "question_type": result.get("question_type", "factual"),
            "confidence": result.get("confidence", 0.5),
            "reasoning": result.get("reasoning", "")
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 실패: {str(e)}, content: {content}")
        # 기본값 반환
        return {
            "question_type": "factual",
            "confidence": 0.5,
            "reasoning": "분류 실패 - 기본값 사용"
        }
    except Exception as e:
        logger.error(f"질문 분류 실패: {str(e)}")
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
            "question_type": str,
            "confidence": float,
            "reasoning": str
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
        
        # 질문 분류
        result = classify_question(question, model_id)
        
        # 성공 로깅
        logger.info(json.dumps({
            "event": "lambda_success",
            "function": context.function_name,
            "question_type": result['question_type'],
            "confidence": result['confidence']
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
