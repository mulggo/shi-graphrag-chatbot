# GraphRAG Agent 단순화 계획 v2.0
## AWS IDP 패턴 기반 재설계

## 🎯 목표

AWS IDP 프로젝트의 검증된 **Plan-Execute-Respond** 패턴을 참고하여 현재 500+ 줄의 복잡한 GraphRAG Agent를 단순화

### 핵심 요구사항
1. **지능적 문서 선택**: 필요한 문서를 LLM이 판단 (편향 방지)
2. **관계 기반 추론**: Neptune GraphRAG의 문서 간 연결점 발견 및 종합
3. **검색 정확도**: Cohere Reranking으로 품질 보장
4. **다국어 처리**: 영어로 검색하되 한국어로 답변

## 🏗️ AWS IDP 참고 아키텍처 분석

### AWS IDP의 멀티 에이전트 구조
```
SearchAgent (메인 에이전트)
├── PlannerAgent      # 실행 계획 수립
├── ExecutorAgent     # 도구 실행 및 검색
├── ResponderAgent    # 응답 생성 및 합성
└── ImageAnalyzerAgent # 멀티모달 분석 (참고용)
```

### 핵심 워크플로우: Plan-Execute-Respond
```python
# AWS IDP 패턴
async def astream(self, message: str):
    # Phase 1: Planning - 실행 계획 수립
    async for event in self.planner.astream(query):
        yield event
    
    # Phase 2: Execution - 도구 실행
    async for event in self.executor.astream(plan):
        yield event
        
    # Phase 3: Response - 응답 생성
    async for event in self.responder.astream(query, plan, results):
        yield event
```

## 📊 현재 vs AWS IDP vs 제안 구조 비교

### 현재 구조 (복잡)
```
GraphRAG Agent (500+ 줄)
├── Strands Framework 오버헤드
├── QueryAnalysisAgent (Lambda: classify_query)
├── RetrievalAgent (Lambda: kb_retrieve) 
├── SynthesisAgent (LLM 합성)
└── 복잡한 메트릭/로깅 시스템
```

### AWS IDP 구조 (참고)
```
SearchAgent (300줄)
├── PlannerAgent (계획 수립)
├── ExecutorAgent (도구 실행)
├── ResponderAgent (응답 생성)
└── 스트리밍 기반 워크플로우
```

### 제안 구조 (단순화)
```
PlanExecuteAgent (150줄)
├── DocumentPlannerAgent (문서 분석 + 검색 계획)
├── GraphRAGSearchTool (Neptune 기반 검색 실행)
└── ResponseSynthesizer (Cohere Reranking + 답변 합성)
```

## 🚀 AWS IDP 기반 단순화 전략

### **핵심 아이디어**: 3단계 → 2단계 통합

**AWS IDP 3단계**:
1. Planning (계획)
2. Execution (실행) 
3. Response (응답)

**GraphRAG 2단계 적용**:
1. **Plan + Execute**: 문서 분석 + Neptune 검색 실행
2. **Rerank + Respond**: Cohere 정제 + 한국어 답변 합성

## 🔧 AWS IDP 참고 구현 포인트

### 1. **스트리밍 워크플로우 패턴**

**참고 파일**: `/packages/backend/src/agent/search_agent/agent.py`

```python
# AWS IDP 스트리밍 패턴
async def astream(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
    yield {"type": "workflow_start", "message": "Starting search workflow..."}
    
    # Phase 1: Planning
    yield {"type": "phase_start", "phase": "planning"}
    async for event in self.planner.astream(query):
        yield event
    
    # Phase 2: Execution  
    yield {"type": "phase_start", "phase": "execution"}
    async for event in self.executor.astream(plan):
        yield event
        
    # Phase 3: Response
    yield {"type": "phase_start", "phase": "response"}
    async for event in self.responder.astream(query, plan, results):
        yield event
        
    yield {"type": "workflow_complete"}
```

**GraphRAG 적용**:
```python
class PlanExecuteAgent(BaseAgent):
    async def astream(self, message: str, session_id: str):
        yield {"type": "workflow_start", "message": "Plan-Execute 워크플로우 시작..."}
        
        # Stage 1: Document Planning + Neptune Search
        yield {"type": "stage_start", "stage": "planning_search"}
        plan_result = await self._plan_and_search(message)
        yield {"type": "search_complete", "results": plan_result}
        
        # Stage 2: Reranking + Response Synthesis  
        yield {"type": "stage_start", "stage": "synthesis"}
        response = await self._rerank_and_synthesize(message, plan_result)
        yield {"type": "workflow_complete", "response": response}
```

### 2. **도구 기반 실행 패턴**

**참고 파일**: `/packages/backend/src/agent/search_agent/workflow/executor.py`

```python
# AWS IDP 도구 실행 패턴
class ExecutorAgent:
    def __init__(self, tools: Dict[str, BaseTool]):
        self.tools = tools
    
    async def astream(self, plan: Plan):
        for task in plan.tasks:
            tool = self.tools.get(task.tool_name)
            result = await tool.execute(**task.tool_args)
            yield {"type": "task_complete", "result": result}
```

**GraphRAG 적용**:
```python
class GraphRAGSearchTool:
    async def execute(self, query: str, document_filters: List[str]):
        # Neptune GraphRAG 검색 (OpenSearch 대신)
        results = []
        for doc_filter in document_filters:
            result = await self._search_neptune_kb(query, doc_filter)
            results.extend(result)
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
```

### 3. **계획 수립 패턴**

**참고 파일**: `/packages/backend/src/agent/search_agent/workflow/planner.py`

```python
# AWS IDP 계획 수립 패턴
class PlannerAgent:
    async def astream(self, query: str):
        # LLM을 통한 계획 수립
        instruction = self._format_planning_prompt(query)
        
        planning_text = ""
        async for event in self.agent.stream_async(instruction):
            planning_text += event["data"]
            yield {"type": "planning_token", "token": event["data"]}
        
        plan = self._parse_plan(planning_text)
        yield {"type": "plan_complete", "plan": plan}
```

**GraphRAG 적용**:
```python
class DocumentPlannerAgent:
    async def create_plan(self, query: str) -> Dict:
        prompt = f"""
        한국어 질문: "{query}"
        
        11개 선박 규정 문서:
        {self.SHIP_DOCUMENTS}
        
        작업:
        1. 필요한 문서들을 식별하고 이유를 설명하세요
        2. 각 문서별 영어 검색 키워드를 생성하세요
        
        JSON 형식으로 응답하세요.
        """
        
        result = await self.llm.invoke(prompt)
        return self._parse_document_plan(result)
```

### 4. **응답 포맷팅 패턴**

**참고 파일**: `/packages/backend/src/mcp_client/server/tools/response_formatter.py`

```python
# AWS IDP 응답 포맷팅
def format_api_response(api_response: Dict, tool_name: str, session_id: str):
    return {
        'success': api_response.get('success', False),
        'llm_text': api_response.get('summary', ''),
        'references': api_response.get('documents', []),
        'count': len(api_response.get('documents', [])),
        'tool_name': tool_name,
        'session_id': session_id
    }
```

**GraphRAG 적용**:
```python
def format_graphrag_response(neptune_results: List, cohere_reranked: List):
    return {
        'success': True,
        'llm_text': '검색 결과 요약',
        'references': [
            {
                'id': ref['id'],
                'content': ref['content'],
                'source': ref['source_document'],
                'score': ref['relevance_score']
            } for ref in cohere_reranked
        ],
        'count': len(cohere_reranked),
        'graph_relationships': neptune_results.get('relationships', [])
    }
```

## 💡 Neptune GraphRAG vs OpenSearch 차이점 고려

### AWS IDP (OpenSearch 기반)
```python
# 하이브리드 검색 (의미론적 + 키워드)
async def hybrid_search(index_id: str, query: str):
    url = f"{API_BASE_URL}/api/opensearch/search/hybrid"
    payload = {"index_id": index_id, "query": query, "size": 3}
    response = requests.post(url, json=payload)
```

### GraphRAG (Neptune 기반)
```python
# GraphRAG 검색 (관계 기반 + 의미론적)
async def graphrag_search(kb_id: str, query: str, document_filter: str = None):
    # Neptune Analytics GraphRAG 검색
    response = await bedrock_agent_runtime.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={'text': query},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 10,
                'filter': {'equals': {'key': 'source', 'value': document_filter}}
            }
        }
    )
    return response['retrievalResults']
```

### 핵심 차이점
1. **검색 방식**: OpenSearch 하이브리드 → Neptune GraphRAG 관계 기반
2. **필터링**: index_id → document source 필터
3. **결과 구조**: 평면적 결과 → 그래프 관계 포함
4. **API 호출**: REST API → AWS SDK (bedrock-agent-runtime)

## 🔧 구체적 구현 계획

### Phase 1: 기존 코드 분석 및 AWS IDP 패턴 적용

**참고할 AWS IDP 파일들**:
```
/packages/backend/src/agent/search_agent/
├── agent.py                    # 메인 에이전트 구조
├── workflow/
│   ├── planner.py             # 계획 수립 패턴
│   ├── executor.py            # 도구 실행 패턴
│   └── responder.py           # 응답 생성 패턴
└── tools/
    ├── base.py                # 도구 인터페이스
    └── hybrid_search.py       # 검색 도구 구현
```

### Phase 2: GraphRAG 특화 구현

```python
class PlanExecuteAgent(BaseAgent):
    """
    Plan-Execute 패턴 기반 GraphRAG 에이전트
    
    AWS IDP의 검증된 Plan-Execute-Respond 패턴을 GraphRAG에 최적화하여 적용.
    2단계 워크플로우로 단순화하면서 핵심 기능 유지.
    
    Features:
    - Plan + Execute: 문서 분석 + Neptune GraphRAG 검색
    - Rerank + Respond: Cohere 정제 + 한국어 답변 합성
    - 스트리밍 지원: 실시간 진행 상황 표시
    - 도구 기반: 표준화된 도구 인터페이스
    """
    
    def __init__(self):
        self.tools = {
            "neptune_search": NeptuneGraphRAGTool(),
            "cohere_rerank": CohereRerankingTool()
        }
        
        self.document_planner = DocumentPlannerAgent()
        self.tool_executor = ToolExecutor(tools=self.tools)
        self.response_synthesizer = ResponseSynthesizer()
    
    async def process_message(self, message: str, session_id: str) -> Dict:
        # Stage 1: Document Planning + Neptune Search
        search_plan = await self.document_planner.create_plan(message)
        search_results = await self.tools["neptune_search"].execute(
            query=search_plan["english_query"],
            document_filters=search_plan["target_documents"]
        )
        
        # Stage 2: Cohere Reranking + Response Synthesis
        reranked_results = await self.tools["cohere_rerank"].execute(
            query=message,
            documents=search_results["results"]
        )
        
        response = await self.response_synthesizer.synthesize(
            query=message,
            documents=reranked_results["results"],
            relationships=search_results.get("relationships", [])
        )
        
        return {
            "response": response["text"],
            "references": response["references"],
            "metadata": {
                "documents_searched": len(search_plan["target_documents"]),
                "results_found": len(search_results["results"]),
                "results_reranked": len(reranked_results["results"])
            }
        }
```

## 🎯 핵심 단순화 포인트

### 1. **Strands Framework 제거**
- 500+ 줄 → 150줄로 축소
- 복잡한 메트릭/로깅 시스템 제거
- 직접적인 AWS SDK 호출

### 2. **Lambda 함수 통합**
```python
# 기존: 3개 Lambda 함수
classify_query()  # 쿼리 분석
kb_retrieve()     # 검색 실행
synthesize()      # 응답 합성

# 단순화: 2개 메서드
plan_and_search()     # 계획 + 검색
rerank_and_respond()  # 정제 + 응답
```

### 3. **도구 기반 아키텍처**
```python
tools = {
    "neptune_search": NeptuneGraphRAGTool(),
    "cohere_rerank": CohereRerankingTool()
}
```

## 🚀 실행 계획

### Step 1: 기존 코드 백업 및 분석
```bash
cp agents/firefighting_agent/agent.py agents/firefighting_agent/agent_backup.py
```

### Step 2: 새로운 PlanExecuteAgent 구현
```python
# agents/firefighting_agent/plan_execute_agent.py
class PlanExecuteAgent(BaseAgent):
    # AWS IDP 패턴 기반 구현
    pass
```

### Step 3: 도구 클래스 구현
```python
# agents/firefighting_agent/tools/
├── neptune_search_tool.py
├── cohere_rerank_tool.py
└── response_synthesizer.py
```

### Step 4: 기존 agent.py 교체
```python
# agents/firefighting_agent/agent.py
from .plan_execute_agent import PlanExecuteAgent

class Agent(PlanExecuteAgent):
    pass
```

### Step 5: 테스트 및 검증
```bash
streamlit run app.py
# 기존 기능 동일성 확인
```

## 📊 예상 효과

### 코드 복잡도
- **라인 수**: 500+ → 150줄 (70% 감소)
- **파일 수**: 1개 거대 파일 → 4개 모듈화된 파일
- **의존성**: Strands Framework 제거

### 성능 개선
- **응답 속도**: Lambda 호출 오버헤드 제거
- **메모리 사용량**: 불필요한 프레임워크 로딩 제거
- **유지보수성**: 명확한 책임 분리

### 기능 유지
- ✅ 지능적 문서 선택
- ✅ Neptune GraphRAG 검색
- ✅ Cohere Reranking
- ✅ 한국어 응답 생성
- ✅ 참조 문서 제공

## 🔄 마이그레이션 전략

### 점진적 교체
1. **Phase 1**: 새 에이전트 구현 (기존 코드 유지)
2. **Phase 2**: A/B 테스트로 검증
3. **Phase 3**: 완전 교체 후 기존 코드 제거

### 롤백 계획
```python
# 문제 발생 시 즉시 롤백
if use_legacy_agent:
    from .legacy_agent import LegacyAgent as Agent
else:
    from .plan_execute_agent import PlanExecuteAgent as Agent
```

---

**결론**: AWS IDP의 검증된 Plan-Execute 패턴을 Neptune GraphRAG에 최적화하여 적용함으로써, 복잡성은 70% 감소시키면서 핵심 기능은 모두 유지하는 단순화된 에이전트 구현이 가능합니다.search"].execute(
            query=message, document_filters=search_plan["required_documents"]
        )
        
        # Stage 2: Cohere Reranking + Response Synthesis
        reranked_results = await self.tools["cohere_rerank"].execute(
            query=message, documents=search_results["results"]
        )
        final_response = await self.response_synthesizer.synthesize(
            message, reranked_results["results"]
        )
        
        return self._format_response(final_response)
```

### Phase 3: 스트리밍 지원 (AWS IDP 패턴 적용)

```python
async def astream(self, message: str, session_id: str):
    # AWS IDP 스트리밍 패턴 적용
    yield {"type": "workflow_start", "message": "GraphRAG 분석 시작..."}
    
    # Stage 1: Planning + Search
    yield {"type": "stage_start", "stage": "document_analysis"}
    plan = await self.document_planner.create_plan(message)
    yield {"type": "plan_complete", "documents": plan['required_documents']}
    
    yield {"type": "stage_start", "stage": "neptune_search"}
    results = await self.graphrag_searcher.execute_searches(plan)
    yield {"type": "search_complete", "count": len(results)}
    
    # Stage 2: Reranking + Synthesis
    yield {"type": "stage_start", "stage": "reranking"}
    reranked = await self._rerank_with_cohere(results, message)
    yield {"type": "rerank_complete", "top_results": len(reranked)}
    
    yield {"type": "stage_start", "stage": "synthesis"}
    response = await self.response_synthesizer.synthesize(message, reranked)
    yield {"type": "workflow_complete", "response": response}
```

## 📋 구현 체크리스트

### AWS IDP 패턴 적용
- [ ] **스트리밍 워크플로우**: `agent.py` 패턴 적용
- [ ] **계획 수립**: `planner.py` 패턴으로 문서 분석
- [ ] **도구 실행**: `executor.py` 패턴으로 Neptune 검색
- [ ] **응답 생성**: `responder.py` 패턴으로 합성
- [ ] **응답 포맷팅**: `response_formatter.py` 패턴 적용

### Neptune GraphRAG 특화
- [ ] **문서 필터링**: 11개 선박 문서별 검색
- [ ] **관계 기반 검색**: Neptune Analytics GraphRAG 활용
- [ ] **Cohere Reranking**: 검색 결과 품질 향상
- [ ] **다국어 처리**: 영어 검색 → 한국어 답변

### 기존 인터페이스 호환성
- [ ] **BaseAgent 준수**: 기존 UI 호환성 유지
- [ ] **응답 형식**: 기존 references 구조 유지
- [ ] **에러 처리**: 기존 에러 핸들링 패턴 유지
- [ ] **설정 호환성**: agents.yaml 설정 유지

## 🎯 성공 기준

### 정량적 목표
- **코드 라인 수**: 500+ → 150 이하 (70% 감소)
- **의존성 제거**: Lambda 3개 → 0개, Strands Framework 제거
- **LLM 호출**: 3개 에이전트 → 2단계 호출
- **응답 시간**: 기존 대비 유지 또는 개선

### 정성적 목표
- **AWS IDP 패턴 적용**: 검증된 Plan-Execute-Respond 구조
- **Neptune GraphRAG 최적화**: 관계 기반 검색 활용
- **스트리밍 지원**: 실시간 진행 상황 표시
- **유지보수성**: 명확한 2단계 구조로 디버깅 용이

## 🚀 다음 단계

1. **AWS IDP 코드 상세 분석**: 핵심 패턴 추출
2. **Neptune GraphRAG 검색 도구 구현**: OpenSearch → Neptune 변환
3. **2단계 워크플로우 구현**: Plan+Execute, Rerank+Respond
4. **스트리밍 인터페이스 적용**: AWS IDP 패턴 기반
5. **기존 UI 호환성 테스트**: BaseAgent 인터페이스 준수

**AWS IDP의 검증된 패턴을 활용하여 GraphRAG Agent를 효과적으로 단순화할 수 있습니다.**