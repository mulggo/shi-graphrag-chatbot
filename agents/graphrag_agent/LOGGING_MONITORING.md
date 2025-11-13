# GraphRAG 로깅 및 모니터링 가이드

## 개요

GraphRAG 멀티 에이전트 시스템은 포괄적인 로깅 및 모니터링 기능을 제공합니다. 이 문서는 로깅 구조, 메트릭 수집, 에러 추적 방법을 설명합니다.

**Requirements**: 8.1-8.6 (Logging and Monitoring)

## 로깅 아키텍처

### 1. 구조화된 로깅

모든 로그는 JSON 형식의 구조화된 로깅을 사용합니다:

```python
logger.info(json.dumps({
    "event": "workflow_start",
    "session_id": session_id,
    "message_length": len(message),
    "timestamp": datetime.now().isoformat()
}))
```

### 2. 로깅 레벨

- **INFO**: 정상적인 워크플로우 실행 정보
- **WARNING**: 재시도 가능한 에러, 품질 저하
- **ERROR**: 실패한 작업, 복구 불가능한 에러
- **DEBUG**: 상세한 디버깅 정보 (메트릭 전송 등)

### 3. 로깅 컴포넌트

#### 3.1 워크플로우 로깅 (agent.py)

**워크플로우 시작**:
```python
logger.info(f"워크플로우 시작: session={session_id}, message='{message[:50]}...'")
```

**단계별 로깅**:
```python
logger.info(f"Step 1 완료: duration={duration:.2f}s, type={question_type}")
logger.info(f"Step 2 완료: duration={duration:.2f}s, chunks={total_retrieved}, quality={search_quality}")
logger.info(f"Step 3 완료: duration={duration:.2f}s, confidence={confidence}")
```

**워크플로우 완료**:
```python
logger.info(f"워크플로우 완료: total_duration={total_duration:.2f}s, success={result['success']}")
```

**워크플로우 실패**:
```python
logger.error(f"워크플로우 실패: {str(e)}", exc_info=True)
```

#### 3.2 Lambda 도구 로깅 (tools.py)

**도구 호출**:
```python
logger.info(f"classify_query 호출: question='{question[:50]}...'")
logger.info(f"extract_entities 호출: question='{question[:50]}...'")
logger.info(f"kb_retrieve 호출: query='{query[:50]}...', num_results={num_results}, rerank={rerank}")
```

**도구 성공**:
```python
logger.info(f"classify_query 성공: type={result.get('question_type')}, duration={duration:.2f}s")
logger.info(f"extract_entities 성공: entities={len(entities)}, keywords={len(keywords)}, duration={duration:.2f}s")
logger.info(f"kb_retrieve 성공: retrieved={total_retrieved}, reranked={reranked}, duration={duration:.2f}s")
```

**도구 실패**:
```python
logger.error(f"classify_query 실패: {str(e)}, duration={duration:.2f}s")
```

#### 3.3 Lambda 함수 로깅

**Lambda 호출 시작**:
```python
logger.info(json.dumps({
    "event": "lambda_invocation",
    "function": context.function_name,
    "request_id": context.request_id,
    "input": event
}))
```

**Lambda 성공**:
```python
logger.info(json.dumps({
    "event": "lambda_success",
    "function": context.function_name,
    "total_retrieved": result['total_retrieved'],
    "duration": result['duration']
}))
```

**Lambda 실패**:
```python
logger.error(json.dumps({
    "event": "lambda_error",
    "function": context.function_name,
    "error": str(e),
    "error_type": type(e).__name__
}))
```

#### 3.4 상호작용 로깅 (agent.py)

```python
def log_interaction(self, message: str, response: Dict, session_id: str):
    """상호작용 로깅"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "agent": self.name,
        "session_id": session_id,
        "message_length": len(message),
        "response_success": response.get("success", False),
        "response_length": len(response.get("content", "")),
        "references_count": len(response.get("references", [])),
        "metadata": response.get("metadata", {})
    }
    
    if response.get("success"):
        logger.info(f"Interaction logged: {json.dumps(log_data)}")
    else:
        logger.error(f"Failed interaction logged: {json.dumps(log_data)}")
```

## CloudWatch 메트릭

### 1. 메트릭 수집기 (metrics.py)

GraphRAG 시스템은 `GraphRAGMetrics` 클래스를 통해 CloudWatch 메트릭을 수집합니다.

#### 초기화

```python
from agents.graphrag_agent.metrics import get_metrics

# 메트릭 수집기 가져오기
metrics = get_metrics(namespace='GraphRAG', enabled=True)
```

#### 환경 변수 설정

```bash
# .env 파일
GRAPHRAG_METRICS_ENABLED=true  # 메트릭 수집 활성화/비활성화
```

### 2. 수집되는 메트릭

#### 2.1 워크플로우 메트릭

**WorkflowDuration** (Seconds):
- 전체 워크플로우 실행 시간
- Dimension: Status (Success/Failure)

```python
metrics.record_workflow_duration(duration, success=True)
```

#### 2.2 단계별 메트릭

**QueryAnalysisTime** (Seconds):
- 쿼리 분석 단계 실행 시간

```python
metrics.record_query_analysis_time(duration)
```

**RetrievalTime** (Seconds):
- KB 검색 단계 실행 시간

**RetrievalCount** (Count):
- 검색된 문서 청크 수

```python
metrics.record_retrieval_time(duration, chunks_retrieved)
```

**SynthesisTime** (Seconds):
- 응답 합성 단계 실행 시간
- Dimension: Confidence (High/Medium/Low)

```python
metrics.record_synthesis_time(duration, confidence)
```

#### 2.3 검색 품질 메트릭

**SearchQuality** (None):
- 검색 품질 점수 (1-4: poor, fair, good, excellent)
- Dimension: QuestionType (Factual/Relational/Multi_doc/Comparative)

```python
metrics.record_search_quality(quality, question_type)
```

**RerankingScore** (None):
- Reranking 평균 점수 (0.0-1.0)

```python
metrics.record_reranking_score(score)
```

#### 2.4 Lambda 메트릭

**LambdaInvocationCount** (Count):
- Lambda 함수 호출 횟수
- Dimensions: FunctionName, Status (Success/Failure)

**LambdaDuration** (Seconds):
- Lambda 함수 실행 시간
- Dimension: FunctionName

```python
metrics.record_lambda_invocation(function_name, duration, success)
```

#### 2.5 에러 메트릭

**ErrorCount** (Count):
- 에러 발생 횟수
- Dimensions: ErrorType, Component

```python
metrics.record_error(error_type, component)
```

**에러 유형**:
- `lambda_error`: Lambda 함수 에러
- `timeout`: 타임아웃 에러
- `bedrock_error`: Bedrock API 에러
- `config_error`: 설정 에러
- `analysis_error`: 쿼리 분석 에러
- `retrieval_error`: 검색 에러
- `synthesis_error`: 응답 합성 에러
- `unknown`: 알 수 없는 에러

**컴포넌트**:
- `workflow`: 전체 워크플로우
- `query_analysis`: 쿼리 분석 단계
- `retrieval`: 검색 단계
- `synthesis`: 응답 합성 단계

### 3. 메트릭 조회

```python
from datetime import datetime, timedelta

# 메트릭 통계 조회
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=1)

stats = metrics.get_metric_statistics(
    metric_name='WorkflowDuration',
    start_time=start_time,
    end_time=end_time,
    period=300,  # 5분 단위
    statistics=['Average', 'Sum', 'Maximum', 'Minimum']
)
```

### 4. CloudWatch 대시보드

#### 주요 메트릭 대시보드

**성능 메트릭**:
- 평균 워크플로우 실행 시간
- 단계별 평균 실행 시간
- Lambda 함수 평균 실행 시간

**품질 메트릭**:
- 검색 품질 분포
- Reranking 평균 점수
- 신뢰도 분포

**안정성 메트릭**:
- 워크플로우 성공률
- 에러율 (유형별, 컴포넌트별)
- Lambda 함수 성공률

**사용량 메트릭**:
- 시간당 요청 수
- Lambda 함수 호출 횟수
- 검색된 총 청크 수

## 에러 추적

### 1. 에러 분류

시스템은 에러를 자동으로 분류합니다:

```python
def _classify_error(self, error: str) -> str:
    """에러 유형 분류"""
    error_lower = error.lower()
    
    if 'lambda' in error_lower or 'function' in error_lower:
        return 'lambda_error'
    elif 'timeout' in error_lower:
        return 'timeout'
    elif 'bedrock' in error_lower or 'kb' in error_lower:
        return 'bedrock_error'
    elif 'invocation_state' in error_lower or 'arn' in error_lower:
        return 'config_error'
    else:
        return 'unknown'
```

### 2. 에러 로깅

모든 에러는 다음 정보와 함께 로깅됩니다:

```python
logger.error(json.dumps({
    "event": "lambda_error",
    "function": context.function_name,
    "error": str(e),
    "error_type": type(e).__name__,
    "traceback": traceback.format_exc()
}))
```

### 3. 에러 복구

**재시도 로직**:
- Lambda 함수 호출: 최대 3회 재시도 (exponential backoff)
- KB 검색: 품질 낮을 시 쿼리 단순화 후 재시도

**Fallback 전략**:
- 쿼리 분석 실패: 기본 검색 전략 사용
- 엔티티 추출 실패: 질문에서 단어 추출
- KB 검색 실패: 빈 결과 반환
- 응답 합성 실패: 에러 메시지 반환

## 로그 분석

### 1. CloudWatch Logs Insights 쿼리

#### 워크플로우 성공률

```sql
fields @timestamp, @message
| filter @message like /워크플로우 완료/ or @message like /워크플로우 실패/
| stats count(*) as total,
        sum(success = true) as successful,
        sum(success = false) as failed
by bin(5m)
```

#### 평균 실행 시간

```sql
fields @timestamp, total_duration
| filter @message like /워크플로우 완료/
| stats avg(total_duration) as avg_duration,
        max(total_duration) as max_duration,
        min(total_duration) as min_duration
by bin(5m)
```

#### Lambda 함수 에러율

```sql
fields @timestamp, function, error_type
| filter event = "lambda_error"
| stats count(*) as error_count by function, error_type
```

#### 검색 품질 분포

```sql
fields @timestamp, search_quality, question_type
| filter @message like /검색 완료/
| stats count(*) by search_quality, question_type
```

### 2. 로그 필터 패턴

**에러 로그만 보기**:
```
[ERROR]
```

**특정 세션 추적**:
```
{ $.session_id = "session-123" }
```

**느린 요청 찾기** (30초 이상):
```
{ $.total_duration > 30 }
```

**Lambda 타임아웃**:
```
{ $.error_type = "timeout" }
```

## 모니터링 알람

### 1. CloudWatch 알람 설정

#### 높은 에러율 알람

```python
alarm = cloudwatch.put_metric_alarm(
    AlarmName='GraphRAG-HighErrorRate',
    MetricName='ErrorCount',
    Namespace='GraphRAG',
    Statistic='Sum',
    Period=300,  # 5분
    EvaluationPeriods=2,
    Threshold=10,  # 5분에 10개 이상 에러
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=['arn:aws:sns:us-west-2:123456789012:graphrag-alerts']
)
```

#### 느린 응답 시간 알람

```python
alarm = cloudwatch.put_metric_alarm(
    AlarmName='GraphRAG-SlowResponse',
    MetricName='WorkflowDuration',
    Namespace='GraphRAG',
    Statistic='Average',
    Period=300,
    EvaluationPeriods=2,
    Threshold=30,  # 평균 30초 이상
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=['arn:aws:sns:us-west-2:123456789012:graphrag-alerts']
)
```

#### Lambda 함수 실패 알람

```python
alarm = cloudwatch.put_metric_alarm(
    AlarmName='GraphRAG-LambdaFailures',
    MetricName='LambdaInvocationCount',
    Namespace='GraphRAG',
    Dimensions=[
        {'Name': 'Status', 'Value': 'Failure'}
    ],
    Statistic='Sum',
    Period=300,
    EvaluationPeriods=1,
    Threshold=5,  # 5분에 5개 이상 실패
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=['arn:aws:sns:us-west-2:123456789012:graphrag-alerts']
)
```

## 디버깅 가이드

### 1. 워크플로우 실패 디버깅

**단계**:
1. CloudWatch Logs에서 세션 ID로 로그 검색
2. 실패한 단계 확인 (Step 1, 2, 3)
3. 에러 메시지 및 스택 트레이스 확인
4. 메트릭에서 에러 유형 및 빈도 확인

**예시**:
```bash
# 세션 로그 검색
aws logs filter-log-events \
  --log-group-name /aws/lambda/graphrag-agent \
  --filter-pattern '{ $.session_id = "session-123" }' \
  --start-time 1234567890000
```

### 2. Lambda 함수 디버깅

**단계**:
1. Lambda 함수 로그 확인
2. 입력 페이로드 검증
3. Bedrock API 응답 확인
4. 재시도 로직 확인

**예시**:
```bash
# Lambda 함수 로그 검색
aws logs tail /aws/lambda/graphrag-kb-retrieve --follow
```

### 3. 성능 문제 디버깅

**단계**:
1. CloudWatch 메트릭에서 느린 단계 식별
2. 해당 단계의 로그 상세 분석
3. Lambda 함수 메모리/타임아웃 설정 확인
4. KB 검색 매개변수 최적화

## 베스트 프랙티스

### 1. 로깅

- **구조화된 로깅 사용**: JSON 형식으로 로깅하여 쉽게 파싱 및 분석
- **적절한 로그 레벨**: INFO는 정상 흐름, ERROR는 실패만
- **민감 정보 제외**: API 키, ARN 등은 로그에서 제외
- **컨텍스트 포함**: session_id, request_id 등 추적 정보 포함

### 2. 메트릭

- **핵심 메트릭 집중**: 성능, 품질, 안정성 메트릭에 집중
- **적절한 Dimension 사용**: 에러 유형, 컴포넌트별로 분류
- **배치 전송**: 여러 메트릭을 한 번에 전송하여 API 호출 최소화

### 3. 알람

- **임계값 조정**: 실제 사용 패턴에 맞게 임계값 설정
- **알람 피로 방지**: 중요한 알람만 설정
- **자동 복구**: 가능한 경우 자동 복구 액션 설정

### 4. 비용 최적화

- **로그 보존 기간**: 필요한 기간만 보존 (예: 30일)
- **메트릭 선택적 활성화**: 프로덕션에서만 활성화
- **로그 필터링**: 불필요한 DEBUG 로그 제외

## 문제 해결

### 메트릭이 CloudWatch에 나타나지 않음

**원인**:
- CloudWatch 클라이언트 초기화 실패
- IAM 권한 부족
- 메트릭 수집 비활성화

**해결**:
```python
# 메트릭 활성화 확인
metrics = get_metrics(enabled=True)

# IAM 권한 확인
{
  "Effect": "Allow",
  "Action": [
    "cloudwatch:PutMetricData"
  ],
  "Resource": "*"
}
```

### 로그가 너무 많음

**해결**:
- DEBUG 로그 비활성화
- 로그 레벨을 INFO 이상으로 설정
- 불필요한 로그 제거

```python
logger.setLevel(logging.INFO)  # DEBUG 제외
```

### Lambda 함수 타임아웃

**해결**:
- 타임아웃 설정 증가 (60초 → 90초)
- 메모리 증가 (1024MB → 2048MB)
- 재시도 로직 확인

## 참고 자료

- [AWS CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)
- [AWS CloudWatch Metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Structured Logging](https://www.structlog.org/)
