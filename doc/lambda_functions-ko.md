# Lambda 함수 문서

## 개요

이 프로젝트는 Strands 프레임워크와 직접 AWS 서비스 통합을 사용하여 향상된 검색 기능을 제공하는 여러 AWS Lambda 함수를 포함합니다.

## Lambda 함수

### 1. lambda_function.py (메인 Strands 도구)

**위치**: `lambda_package/lambda_function.py`

**목적**: 고급 검색 기능을 위한 Strands ReAct 패턴을 구현하는 주요 Lambda 함수입니다.

#### 기능
- **Strands Agent 통합**: ReAct(추론 및 행동) 패턴을 위한 Strands 프레임워크 사용
- **Knowledge Base 도구**: AWS Bedrock Knowledge Base와 통합
- **한국어 지원**: 한국어로 응답
- **세션 관리**: 세션 기반 대화 처리

#### 구현 세부사항
```python
# 주요 구성 요소:
- KnowledgeBaseTool: Knowledge Base (ZGBA1R5CS0)에 연결
- Agent: 특정 지침으로 ReAct 패턴 구현
- Model: 추론을 위해 Claude 3.5 Sonnet 사용
```

#### 입력 매개변수
- `inputText`: 사용자 질의 텍스트
- `sessionId`: 세션 식별자 (선택사항, 기본값 'default')

#### 응답 형식
```json
{
    "statusCode": 200,
    "body": {
        "result": "한국어 검색 결과",
        "session_id": "세션_식별자",
        "search_method": "strands_react"
    }
}
```

### 2. strands_tool_lambda.py (대체 구현)

**위치**: `strands_tool_lambda.py`

**목적**: 메인 Lambda 함수와 동일한 기능을 가진 Strands ReAct 검색 도구의 대체 구현입니다.

#### 주요 차이점
- 독립 실행형 파일 (패키지 디렉토리에 없음)
- 메인 Lambda 함수와 동일한 핵심 기능
- 테스트 및 백업 배포용

### 3. simple_lambda.py (테스트 함수)

**위치**: `simple_lambda.py`

**목적**: 기본 Bedrock Agent Action Group 테스트를 위한 간단한 테스트 Lambda 함수입니다.

#### 기능
- **기본 응답**: 간단한 한국어 응답 반환
- **이벤트 로깅**: 디버깅을 위한 수신 이벤트 로깅
- **매개변수 추출**: 여러 입력 매개변수 형식 처리

#### 사용 사례
- Bedrock Agent 통합 테스트
- 이벤트 구조 디버깅
- 기본 기능 확인

### 4. strands_simple_lambda.py (향상된 테스트 함수)

**위치**: `strands_simple_lambda.py`

**목적**: 직접 AWS 서비스를 사용하여 Strands와 유사한 동작을 시뮬레이션하는 향상된 테스트 함수입니다.

#### 기능
- **직접 Knowledge Base 액세스**: KB 쿼리를 위해 Bedrock Agent Runtime 사용
- **향상된 검색**: 여러 결과로 고급 검색 수행
- **결과 처리**: 검색 결과 형식화 및 점수 매기기
- **오류 처리**: 기본 응답으로 우아한 폴백

#### 검색 구성
- **Knowledge Base ID**: ZGBA1R5CS0
- **결과 수**: 최대 10개 결과
- **콘텐츠 제한**: 결과당 500자
- **점수 표시**: 관련성 점수 표시

## 배포 구성

### 요구사항
**파일**: `lambda_package/requirements.txt`
```
strands-agents
boto3
```

### 신뢰 정책
**파일**: `lambda_trust_policy.json`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### OpenAPI 스키마
**파일**: `strands_tool_schema.json`

Bedrock Agent 통합을 위한 API 스키마 정의:
- **엔드포인트**: `/search` (POST)
- **Operation ID**: `strandsReactSearch`
- **입력**: `query` 매개변수가 있는 JSON
- **출력**: `result` 필드가 있는 JSON

## Lambda 레이어

### 레이어 구조
프로젝트에는 의존성이 포함된 사전 구축된 Lambda 레이어가 포함됩니다:

#### layer/python/
- **핵심 의존성**: boto3, strands-agents 및 관련 패키지
- **크기 최적화**: 필요한 패키지만 포함
- **Python 버전**: Python 3.11과 호환

#### lambda_layer/python/
- **대체 레이어**: 추가 레이어 구성
- **Strands 프레임워크**: Strands agents 프레임워크 포함
- **NumPy 지원**: 데이터 처리를 위한 NumPy 포함

## 오류 처리

### 예외 관리
모든 Lambda 함수는 포괄적인 오류 처리를 구현합니다:

```python
try:
    # 메인 로직
    result = strands_agent.run(input_text)
    return success_response
except Exception as e:
    return {
        'statusCode': 500,
        'body': {
            'error': str(e),
            'result': f"검색 중 오류가 발생했습니다: {str(e)}"
        }
    }
```

### 일반적인 오류 시나리오
1. **Strands 프레임워크 오류**: 모델 액세스 또는 도구 초기화 문제
2. **AWS 서비스 오류**: Knowledge Base 또는 Bedrock 액세스 문제
3. **입력 검증**: 누락되거나 잘못된 형식의 입력 매개변수
4. **타임아웃 문제**: 장시간 실행되는 검색 작업

## 성능 고려사항

### 콜드 스타트 최적화
- **레이어 사용**: 레이어의 의존성으로 콜드 스타트 시간 단축
- **임포트 최적화**: 핸들러 함수에서 최소한의 임포트
- **연결 재사용**: 핸들러 외부에서 AWS 클라이언트 초기화

### 메모리 및 타임아웃 설정
- **권장 메모리**: 512MB - 1GB
- **타임아웃**: 복잡한 검색의 경우 30-60초
- **동시 실행**: 예상 부하에 따라 구성

## Bedrock Agent와의 통합

### Action Group 구성
1. **스키마 업로드**: `strands_tool_schema.json` 사용
2. **Lambda ARN**: 배포된 함수를 가리킴
3. **권한**: Bedrock이 Lambda를 호출할 수 있도록 보장

### 통합 테스트
테스트 함수를 사용하여 다음을 확인:
- Bedrock Agent의 이벤트 구조
- 매개변수 전달
- 응답 형식 호환성

## 모니터링 및 로깅

### CloudWatch 로그
- **함수 로그**: 함수 실행의 자동 로깅
- **오류 추적**: 예외 세부사항 및 스택 추적
- **성능 메트릭**: 지속 시간 및 메모리 사용량

### 사용자 정의 로깅
```python
print(f"Received event: {json.dumps(event)}")
print(f"Processing query: {input_text}")
```

## 배포 모범 사례

### 패키징
1. **의존성**: 큰 의존성에 레이어 사용
2. **코드 크기**: 함수 코드를 최소한으로 유지
3. **환경 변수**: 구성에 사용

### 보안
1. **IAM 역할**: 최소 필요 권한
2. **VPC 구성**: 프라이빗 리소스 액세스 시
3. **환경 변수**: 민감한 데이터 암호화

### 버전 관리
1. **별칭**: 다른 환경에 별칭 사용
2. **버전 관리**: 롤백 기능을 위한 버전 태그
3. **테스트**: 프로덕션 배포 전 스테이징에서 테스트