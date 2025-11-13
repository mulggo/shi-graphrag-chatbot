# Task 8: 로깅 및 모니터링 구현 완료

## 구현 개요

GraphRAG 멀티 에이전트 시스템에 포괄적인 로깅 및 모니터링 기능을 구현했습니다.

**Requirements**: 8.1-8.6 (Logging and Monitoring)

## 구현된 기능

### 1. CloudWatch 메트릭 수집 모듈 (metrics.py)

**파일**: `agents/graphrag_agent/metrics.py`

**주요 클래스**:
- `GraphRAGMetrics`: CloudWatch 메트릭 수집 및 전송

**수집 메트릭**:
- WorkflowDuration: 전체 워크플로우 실행 시간
- QueryAnalysisTime: 쿼리 분석 시간
- RetrievalTime: KB 검색 시간
- RetrievalCount: 검색된 청크 수
- SynthesisTime: 응답 합성 시간
- SearchQuality: 검색 품질 점수
- RerankingScore: Reranking 평균 점수
- LambdaInvocationCount: Lambda 함수 호출 횟수
- LambdaDuration: Lambda 함수 실행 시간
- ErrorCount: 에러 발생 횟수 (유형별, 컴포넌트별)

**주요 메서드**:
- `record_workflow_duration()`: 워크플로우 실행 시간 기록
- `record_query_analysis_time()`: 쿼리 분석 시간 기록
- `record_retrieval_time()`: 검색 시간 및 청크 수 기록
- `record_synthesis_time()`: 응답 합성 시간 기록
- `record_search_quality()`: 검색 품질 기록
- `record_reranking_score()`: Reranking 점수 기록
- `record_lambda_invocation()`: Lambda 함수 호출 기록
- `record_error()`: 에러 발생 기록
- `get_metric_statistics()`: 메트릭 통계 조회

### 2. 워크플로우 로깅 강화 (agent.py)

**추가된 기능**:
- 메트릭 수집기 초기화
- 단계별 실행 시간 메트릭 기록
- 검색 품질 및 Reranking 점수 메트릭 기록
- 에러 발생 시 메트릭 기록
- 구조화된 상호작용 로깅

**로그 예시**:
```
워크플로우 시작: session=abc123, message='고정식 CO2 소화 시스템의...'
Step 1 완료: duration=2.34s, type=factual
Step 2 완료: duration=3.45s, chunks=10, quality=good
Step 3 완료: duration=4.56s, confidence=high
워크플로우 완료: total_duration=10.35s, success=True
```

### 3. Lambda 도구 로깅 강화 (tools.py)

**추가된 기능**:
- 각 Lambda 함수 호출 시간 측정
- Lambda 함수 성공/실패 메트릭 기록
- 에러 발생 시 메트릭 기록
- 상세한 실행 시간 로깅

**로그 예시**:
```
classify_query 호출: question='고정식 CO2...'
classify_query 성공: type=factual, duration=1.23s
```

### 4. 워크플로우 에이전트 로깅 강화 (workflow_agents.py)

**추가된 기능**:
- 각 에이전트 에러 발생 시 메트릭 기록
- 상세한 에러 스택 트레이스 로깅
- 컴포넌트별 에러 분류

### 5. Lambda 함수 구조화된 로깅

**이미 구현된 기능** (확인 완료):
- classify_query Lambda: 구조화된 JSON 로깅
- extract_entities Lambda: 구조화된 JSON 로깅
- kb_retrieve Lambda: 구조화된 JSON 로깅

**로그 형식**:
```json
{
  "event": "lambda_invocation",
  "function": "graphrag-kb-retrieve",
  "request_id": "abc-123",
  "input": {...}
}
```

### 6. 포괄적인 문서화

**파일**: `agents/graphrag_agent/LOGGING_MONITORING.md`

**내용**:
- 로깅 아키텍처 설명
- CloudWatch 메트릭 상세 설명
- 에러 추적 방법
- 로그 분석 쿼리 예시
- 모니터링 알람 설정 가이드
- 디버깅 가이드
- 베스트 프랙티스
- 문제 해결 가이드

## 사용 방법

### 메트릭 수집 활성화

```python
# config/agents.yaml
graphrag:
  metrics_enabled: true  # 메트릭 수집 활성화
```

### 메트릭 조회

```python
from agents.graphrag_agent.metrics import get_metrics
from datetime import datetime, timedelta

metrics = get_metrics()

# 최근 1시간 워크플로우 실행 시간 통계
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=1)

stats = metrics.get_metric_statistics(
    metric_name='WorkflowDuration',
    start_time=start_time,
    end_time=end_time,
    period=300,
    statistics=['Average', 'Maximum', 'Minimum']
)
```

### CloudWatch Logs Insights 쿼리

```sql
-- 워크플로우 성공률
fields @timestamp, @message
| filter @message like /워크플로우 완료/ or @message like /워크플로우 실패/
| stats count(*) as total by bin(5m)

-- 평균 실행 시간
fields @timestamp, total_duration
| filter @message like /워크플로우 완료/
| stats avg(total_duration) as avg_duration by bin(5m)
```

## 테스트 방법

### 1. 메트릭 수집 테스트

```python
from agents.graphrag_agent.metrics import GraphRAGMetrics

# 메트릭 수집기 초기화
metrics = GraphRAGMetrics(namespace='GraphRAG-Test', enabled=True)

# 테스트 메트릭 전송
metrics.record_workflow_duration(10.5, success=True)
metrics.record_query_analysis_time(2.3)
metrics.record_retrieval_time(3.4, 10)
metrics.record_synthesis_time(4.5, 'high')
```

### 2. 로깅 테스트

```bash
# 로그 확인
aws logs tail /aws/lambda/graphrag-agent --follow

# 특정 세션 로그 검색
aws logs filter-log-events \
  --log-group-name /aws/lambda/graphrag-agent \
  --filter-pattern '{ $.session_id = "test-session" }'
```

## 주요 개선 사항

1. **포괄적인 메트릭 수집**: 워크플로우 전체 및 각 단계별 성능 메트릭
2. **구조화된 로깅**: JSON 형식으로 쉽게 파싱 및 분석 가능
3. **에러 추적**: 에러 유형 및 컴포넌트별 분류
4. **Lambda 모니터링**: 각 Lambda 함수 호출 및 성능 추적
5. **검색 품질 추적**: 검색 품질 및 Reranking 점수 모니터링
6. **상세한 문서화**: 사용 방법, 디버깅, 베스트 프랙티스 가이드

## 다음 단계

Task 8 (로깅 및 모니터링) 구현이 완료되었습니다.

다음 작업:
- Task 9: Lambda 함수 배포
- Task 10: 통합 및 테스트
- Task 11: UI 통합
- Task 12: 문서화
- Task 13: 최종 검증 및 배포

## 파일 목록

**새로 생성된 파일**:
- `agents/graphrag_agent/metrics.py` - CloudWatch 메트릭 수집 모듈
- `agents/graphrag_agent/LOGGING_MONITORING.md` - 로깅 및 모니터링 가이드
- `agents/graphrag_agent/TASK_8_SUMMARY.md` - Task 8 구현 요약

**수정된 파일**:
- `agents/graphrag_agent/agent.py` - 메트릭 수집 통합
- `agents/graphrag_agent/tools.py` - Lambda 도구 메트릭 추가
- `agents/graphrag_agent/workflow_agents.py` - 에이전트 에러 메트릭 추가

**확인된 파일** (이미 구조화된 로깅 구현됨):
- `lambda_package/graphrag_tools/classify_query/lambda_function.py`
- `lambda_package/graphrag_tools/extract_entities/lambda_function.py`
- `lambda_package/graphrag_tools/kb_retrieve/lambda_function.py`
