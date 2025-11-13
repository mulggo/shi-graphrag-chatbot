# GraphRAG Agent Implementation

## 개요

GraphRAG Agent는 Strands Agents 프레임워크를 사용하여 구현된 멀티 에이전트 워크플로우 오케스트레이터입니다. 이 에이전트는 기존 Bedrock Agent를 사용하지 않고, 세 개의 전문 에이전트를 조율하여 지능형 GraphRAG 검색을 수행합니다.

## 아키텍처

### 워크플로우 구조

```
사용자 질문
    ↓
GraphRAG Agent (agent.py)
    ↓
┌─────────────────────────────────────┐
│  Step 1: Query Analysis             │
│  - QueryAnalysisAgent               │
│  - Tools: classify_query,           │
│           extract_entities          │
│  - Output: search_strategy          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 2: KB Retrieval               │
│  - RetrievalAgent                   │
│  - Tools: kb_retrieve               │
│  - Output: retrieval_results        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 3: Response Synthesis         │
│  - SynthesisAgent                   │
│  - Tools: Bedrock Claude            │
│  - Output: synthesis_results        │
└─────────────────────────────────────┘
    ↓
포맷팅된 응답 (ReferenceDisplay 호환)
```

## 주요 컴포넌트

### 1. Agent 클래스 (agent.py)

메인 오케스트레이터 클래스로, BaseAgent를 상속합니다.

**주요 메서드:**

- `__init__(config)`: 에이전트 초기화 및 워크플로우 에이전트 설정
- `process_message(message, session_id)`: 메시지 처리 메인 진입점
- `_initialize_workflow_agents()`: 세 개의 전문 에이전트 초기화
- `_format_response()`: 워크플로우 결과를 UI 호환 형식으로 변환
- `_handle_workflow_failure()`: 에러 처리 및 사용자 친화적 메시지 생성
- `log_interaction()`: 구조화된 로깅

**초기화 과정:**

1. BaseAgent 초기화 (AWS 클라이언트, KB ID 등)
2. Lambda 함수 ARN 설정
3. ToolContext 생성 (invocation_state에 ARN 및 KB ID 전달)
4. 프롬프트 로드 (prompts.py)
5. 세 개의 워크플로우 에이전트 초기화

### 2. 워크플로우 실행

`process_message()` 메서드는 다음 순서로 워크플로우를 실행합니다:

```python
# Step 1: Query Analysis
search_strategy = self.query_analysis_agent.analyze(message)
# Returns: {
#     "question_type": str,
#     "entities": List[str],
#     "keywords": List[str],
#     "search_params": Dict
# }

# Step 2: KB Retrieval
retrieval_results = self.retrieval_agent.retrieve(search_strategy)
# Returns: {
#     "chunks": List[Dict],
#     "total_retrieved": int,
#     "search_quality": str
# }

# Step 3: Response Synthesis
synthesis_results = self.synthesis_agent.synthesize(retrieval_results, message)
# Returns: {
#     "content": str,
#     "references": List[Dict],
#     "confidence": str
# }
```

### 3. 에러 처리

에러 처리는 다층 구조로 구현되어 있습니다:

**에러 분류:**
- `lambda_error`: Lambda 함수 관련 에러
- `timeout`: 타임아웃 에러
- `bedrock_error`: Bedrock KB 관련 에러
- `config_error`: 설정 관련 에러
- `unknown`: 기타 에러

**사용자 친화적 메시지:**
각 에러 유형에 대해 사용자가 이해하기 쉬운 한국어 메시지를 생성합니다.

### 4. 응답 포맷팅

`_format_response()` 메서드는 워크플로우 결과를 다음 형식으로 변환합니다:

```python
{
    "success": True,
    "content": "한국어 답변 텍스트",
    "references": [
        {
            "source_file": "SOLAS_Chapter_II-2.pdf",
            "page_number": 45,
            "ocr_text": "The minimum capacity shall be...",
            "image_uri": "s3://bucket/path/to/image.png"
        }
    ],
    "agent_name": "graphrag",
    "metadata": {
        "question_type": "factual",
        "document_categories": ["규정"],
        "total_chunks_retrieved": 10,
        "search_quality": "excellent",
        "confidence": "high",
        "coverage": "complete",
        "reranked": True,
        "durations": {
            "query_analysis": 1.5,
            "retrieval": 2.3,
            "synthesis": 3.1,
            "total": 6.9
        }
    }
}
```

이 형식은 기존 ReferenceDisplay UI 컴포넌트와 완전히 호환됩니다.

## 설정

### config/agents.yaml

```yaml
graphrag:
  display_name: "GraphRAG 검색"
  description: "지능형 그래프 기반 문서 검색 전문가"
  module_path: "agents.graphrag_agent.agent"
  bedrock_agent_id: ""  # 사용 안 함
  bedrock_alias_id: ""  # 사용 안 함
  bedrock_model_id: "anthropic.claude-3-5-sonnet-20240620-v1:0"
  knowledge_base_id: "ZGBA1R5CS0"
  lambda_function_names:
    classify_query: "graphrag-classify-query"
    extract_entities: "graphrag-extract-entities"
    kb_retrieve: "graphrag-kb-retrieve"
  reranker_model_arn: ""  # Optional
  enabled: false  # 구현 완료 후 true로 변경
  ui_config:
    icon: "🕸️"
    color: "#9B59B6"
    topics:
      - "복잡한 규정 질의"
      - "다중 문서 추론"
      - "관계 기반 검색"
```

### 환경 변수 (.env)

```bash
# Bedrock 설정
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0

# Lambda 함수 ARN
LAMBDA_CLASSIFY_QUERY_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-classify-query
LAMBDA_EXTRACT_ENTITIES_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-extract-entities
LAMBDA_KB_RETRIEVE_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-kb-retrieve

# Feature Flag
GRAPHRAG_ENABLED=false
```

## 통합

### AgentManager와의 통합

GraphRAG Agent는 기존 AgentManager와 완전히 호환됩니다:

1. `config/agents.yaml`에 설정 추가
2. AgentManager가 자동으로 에이전트 로드
3. UI에서 에이전트 선택 가능
4. `process_message()` 인터페이스를 통해 메시지 처리

### BaseAgent 인터페이스 준수

GraphRAG Agent는 BaseAgent의 모든 메서드를 구현합니다:

- `process_message(message, session_id)`: 필수 메서드
- `log_interaction(message, response, session_id)`: 로깅
- `get_capabilities()`: 기능 목록 반환
- `ui_config`: UI 설정 프로퍼티

추가로 GraphRAG 전용 메서드를 제공합니다:

- `get_workflow_status()`: 워크플로우 상태 정보 반환

## 로깅

구조화된 로깅을 사용하여 워크플로우 실행을 추적합니다:

```python
{
    "timestamp": "2024-01-15T10:30:00",
    "agent": "graphrag",
    "session_id": "abc123",
    "message_length": 50,
    "response_success": True,
    "response_length": 500,
    "references_count": 3,
    "metadata": {
        "question_type": "factual",
        "total_chunks_retrieved": 10,
        "durations": {...}
    }
}
```

## 성능 메트릭

각 단계의 소요 시간을 추적합니다:

- `query_analysis`: 쿼리 분석 시간
- `retrieval`: KB 검색 시간
- `synthesis`: 응답 합성 시간
- `total`: 전체 워크플로우 시간

목표: 평균 30초 이내 응답

## 테스트

`test_agent.py`를 사용하여 다음을 테스트할 수 있습니다:

1. **초기화 테스트**: 에이전트 및 워크플로우 에이전트 초기화
2. **에러 처리 테스트**: 에러 분류 및 사용자 친화적 메시지 생성
3. **응답 포맷팅 테스트**: UI 호환 형식 변환

```bash
python agents/graphrag_agent/test_agent.py
```

## 다음 단계

1. Lambda 함수 배포 (task 9)
2. 통합 테스트 (task 10)
3. UI 통합 확인 (task 11)
4. 에이전트 활성화 (`enabled: true`)

## 요구사항 충족

이 구현은 다음 요구사항을 충족합니다:

- **1.1-1.5**: 멀티 에이전트 워크플로우 아키텍처
- **10.1**: BaseAgent 상속
- **10.2**: AgentManager 통합
- **10.3**: process_message 인터페이스 구현
- **10.4**: 독립적 작동 (Bedrock Agent 미사용)
- **10.9**: ReferenceDisplay 호환 응답 형식
- **10.10**: agents/graphrag_agent/ 디렉토리 구조

## 참고 자료

- [BaseAgent](../base_agent.py): 기본 에이전트 클래스
- [WorkflowAgents](./workflow_agents.py): 전문 에이전트 구현
- [Tools](./tools.py): Lambda 도구 래퍼
- [Prompts](./prompts.py): 프롬프트 로더
- [Design Document](../../.kiro/specs/graphrag-multi-agent/design.md): 전체 설계 문서
