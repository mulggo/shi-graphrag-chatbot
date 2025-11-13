# GraphRAG Tools Implementation

## 개요

Task 4에서 구현된 도구 래퍼 모듈입니다. 이 모듈은 Lambda 함수를 Strands @tool 데코레이터를 사용하여 에이전트 도구로 래핑합니다.

## 구현된 도구

### 1. classify_query
- **목적**: 질문 유형 분류 (factual, relational, multi_doc, comparative)
- **Lambda 함수**: `lambda_classify_query_arn`
- **입력**: 사용자 질문
- **출력**: 질문 유형, 신뢰도, 분류 이유

### 2. extract_entities
- **목적**: 질문에서 엔티티, 개념, 키워드 추출
- **Lambda 함수**: `lambda_extract_entities_arn`
- **입력**: 사용자 질문
- **출력**: 엔티티, 개념, 한국어/영어 키워드, 관련 문서

### 3. kb_retrieve
- **목적**: Bedrock KB 검색 및 reranking
- **Lambda 함수**: `lambda_kb_retrieve_arn`
- **입력**: 검색 쿼리, 결과 수
- **출력**: 문서 청크, 관련성 점수, 메타데이터

## 주요 기능

### ToolContext 사용
모든 도구는 `@tool(context=True)` 데코레이터를 사용하여 ToolContext를 자동으로 주입받습니다:
```python
@tool(context=True)
def classify_query(question: str, tool_context: ToolContext) -> Dict[str, Any]:
    lambda_arn = tool_context.invocation_state.get('lambda_classify_query_arn')
    # ...
```

### invocation_state 전달
각 도구는 ToolContext를 통해 invocation_state에서 필요한 설정을 가져옵니다:
- `lambda_classify_query_arn`: classify_query Lambda 함수 ARN
- `lambda_extract_entities_arn`: extract_entities Lambda 함수 ARN
- `lambda_kb_retrieve_arn`: kb_retrieve Lambda 함수 ARN
- `kb_id`: Bedrock Knowledge Base ID
- `reranker_model_arn`: Reranker 모델 ARN (선택)

### 에러 처리 및 재시도
`_invoke_lambda_with_retry()` 헬퍼 함수를 통해:
- Exponential backoff를 사용한 재시도 (최대 3회)
- TooManyRequestsException, ThrottlingException 등 일시적 에러 처리
- Lambda 함수 내부 에러 감지 및 처리
- 구조화된 로깅

### 에러 복구
각 도구는 에러 발생 시 기본값을 반환하여 워크플로우가 중단되지 않도록 합니다:
- `classify_query`: "factual" 유형으로 기본 설정
- `extract_entities`: 질문에서 단어 추출
- `kb_retrieve`: 빈 결과 반환

## Requirements 충족

이 구현은 다음 요구사항을 충족합니다:

- **7.5**: Strands @tool 데코레이터 사용
- **7.6**: 명확한 docstring (Anthropic 문서화 원칙)
- **7.7**: ToolContext를 통한 invocation_state 전달
- **7.8**: AWS 자격 증명, KB ID, Lambda ARN 접근
- **7.9**: 상태 비저장(stateless) Lambda 함수 호출
- **7.10**: 적절한 에러 처리 및 재시도 로직

## 사용 예시

```python
from agents.graphrag_agent.tools import classify_query, extract_entities, kb_retrieve

# 에이전트에서 도구 등록
agent = Agent(
    tools=[classify_query, extract_entities, kb_retrieve],
    invocation_state={
        'lambda_classify_query_arn': 'arn:aws:lambda:...',
        'lambda_extract_entities_arn': 'arn:aws:lambda:...',
        'lambda_kb_retrieve_arn': 'arn:aws:lambda:...',
        'kb_id': 'ZGBA1R5CS0',
        'reranker_model_arn': 'arn:aws:bedrock:...'
    }
)

# 도구 호출 (Strands가 자동으로 ToolContext 주입)
result = agent.classify_query(question="고정식 CO2 소화 시스템의 최소 용량은?")
```

## 다음 단계

Task 5: Workflow Agents 구현에서 이 도구들을 사용하여 쿼리 분석, 검색 실행, 응답 합성 에이전트를 구현합니다.
