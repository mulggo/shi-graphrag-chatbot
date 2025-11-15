# PlanExecuteAgent 구현 가이드
## 단계별 점검 및 테스트 문서

## 🎯 전체 구현 로드맵

### **Phase 1: 기반 구조 (1-2일)**
- [ ] 도구 인터페이스 구현
- [ ] 기본 설정 및 구조
- [ ] **테스트**: 인터페이스 호환성

### **Phase 2: 핵심 도구 (2-3일)**  
- [ ] Neptune GraphRAG 검색 도구
- [ ] Cohere Reranking 도구
- [ ] **테스트**: 개별 도구 기능

### **Phase 3: 워크플로우 컴포넌트 (2-3일)**
- [ ] 문서 계획 수립 에이전트
- [ ] 응답 합성기
- [ ] **테스트**: 컴포넌트 통합

### **Phase 4: 메인 에이전트 (2-3일)**
- [ ] PlanExecuteAgent 기본 구조
- [ ] 비스트리밍 구현
- [ ] **테스트**: 전체 워크플로우

### **Phase 5: 스트리밍 지원 (1-2일)**
- [ ] 스트리밍 워크플로우
- [ ] **테스트**: UI 호환성

### **Phase 6: 통합 및 검증 (2-3일)**
- [ ] 기존 시스템 통합
- [ ] 성능 비교 테스트
- [ ] **테스트**: 품질 검증

---

## 📋 Phase 1: 기반 구조 구현

### **구현 목표**
- AWS IDP 스타일 도구 인터페이스 구축
- 기본 프로젝트 구조 설정

### **구현 체크리스트**

#### 1.1 도구 인터페이스
```python
# agents/plan_execute_agent/tools/base.py
class BaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass
    
    def create_reference(self, ref_type: str, value: str, **kwargs) -> Reference:
        pass

# agents/plan_execute_agent/tools/types.py
class ToolResult(TypedDict):
    success: bool
    count: int
    results: List[Dict[str, Any]]
    references: List[Reference]
    llm_text: str
    error: Optional[str]
```

- [ ] `BaseTool` 추상 클래스 구현
- [ ] `ToolResult` 타입 정의
- [ ] `Reference` 타입 정의
- [ ] `create_reference` 헬퍼 메서드

#### 1.2 기본 구조
```
agents/plan_execute_agent/
├── __init__.py
├── agent.py                 # 메인 에이전트
├── config.py               # 설정
├── constants.py            # 11개 문서 정의
├── tools/
│   ├── __init__.py
│   ├── base.py            # 도구 인터페이스
│   └── types.py           # 타입 정의
└── tests/
    └── test_base_tools.py
```

- [ ] 디렉토리 구조 생성
- [ ] 기본 파일들 생성
- [ ] 11개 선박 문서 상수 정의

### **Phase 1 테스트**

#### 테스트 1.1: 인터페이스 호환성
```python
# tests/test_phase1.py
def test_base_tool_interface():
    """BaseTool 인터페이스가 올바르게 정의되었는지 확인"""
    
def test_tool_result_structure():
    """ToolResult 구조가 AWS IDP 패턴과 일치하는지 확인"""
    
def test_reference_creation():
    """Reference 생성이 올바르게 작동하는지 확인"""
```

#### 테스트 실행
```bash
cd agents/plan_execute_agent
python -m pytest tests/test_phase1.py -v
```

#### **Phase 1 완료 기준**
- [ ] 모든 인터페이스 테스트 통과
- [ ] 기존 BaseAgent와 호환성 확인
- [ ] 11개 문서 상수 정의 완료

---

## 📋 Phase 2: 핵심 도구 구현

### **구현 목표**
- Neptune GraphRAG 검색 도구 구현
- Cohere Reranking 도구 구현

### **구현 체크리스트**

#### 2.1 Neptune GraphRAG 검색 도구
```python
# agents/plan_execute_agent/tools/neptune_search_tool.py
class NeptuneGraphRAGTool(BaseTool):
    async def execute(self, query: str, document_filters: List[str]) -> ToolResult:
        # 기존 Lambda kb_retrieve 로직 이식
        pass
```

- [ ] 기존 Lambda 함수 로직 분석
- [ ] `bedrock_agent_runtime.retrieve()` 호출 구현
- [ ] 문서 필터링 로직 구현
- [ ] 결과를 ToolResult 형식으로 변환
- [ ] 에러 처리 및 로깅

#### 2.2 Cohere Reranking 도구
```python
# agents/plan_execute_agent/tools/cohere_rerank_tool.py
class CohereRerankingTool(BaseTool):
    async def execute(self, query: str, documents: List[Dict]) -> ToolResult:
        # Cohere API 호출
        pass
```

- [ ] Cohere API 클라이언트 설정
- [ ] 문서 리랭킹 로직 구현
- [ ] 상위 결과 선택 (top-k)
- [ ] 스코어 정규화
- [ ] 결과를 ToolResult 형식으로 변환

### **Phase 2 테스트**

#### 테스트 2.1: Neptune 검색 도구
```python
# tests/test_phase2.py
async def test_neptune_search_basic():
    """기본 Neptune 검색이 작동하는지 확인"""
    tool = NeptuneGraphRAGTool()
    result = await tool.execute(
        query="fire safety systems",
        document_filters=["SOLAS_II2", "FSS_Code"]
    )
    assert result["success"] == True
    assert result["count"] > 0

async def test_neptune_search_filtering():
    """문서 필터링이 올바르게 작동하는지 확인"""
    
async def test_neptune_search_error_handling():
    """에러 상황에서 적절히 처리되는지 확인"""
```

#### 테스트 2.2: Cohere Reranking 도구
```python
async def test_cohere_rerank_basic():
    """기본 리랭킹이 작동하는지 확인"""
    
async def test_cohere_rerank_scoring():
    """스코어링이 올바르게 작동하는지 확인"""
```

#### 성능 테스트
```python
async def test_neptune_search_performance():
    """Neptune 검색 응답 시간 측정 (< 3초)"""
    
async def test_cohere_rerank_performance():
    """Cohere 리랭킹 응답 시간 측정 (< 1초)"""
```

#### **Phase 2 완료 기준**
- [ ] Neptune 검색 도구 테스트 통과
- [ ] Cohere 리랭킹 도구 테스트 통과
- [ ] 성능 기준 만족 (Neptune < 3초, Cohere < 1초)
- [ ] 기존 Lambda 함수와 동일한 결과 출력

---

## 📋 Phase 3: 워크플로우 컴포넌트

### **구현 목표**
- 문서 계획 수립 에이전트 구현
- 응답 합성기 구현

### **구현 체크리스트**

#### 3.1 문서 계획 수립 에이전트
```python
# agents/plan_execute_agent/planner.py
class DocumentPlannerAgent:
    async def create_plan(self, query: str) -> Dict:
        # LLM으로 필요한 문서 식별
        pass
```

- [ ] 11개 문서 분석 프롬프트 작성
- [ ] LLM 호출 및 응답 파싱
- [ ] JSON 형식 검증
- [ ] 영어 키워드 생성 로직
- [ ] 에러 처리 (파싱 실패 시 기본값)

#### 3.2 응답 합성기
```python
# agents/plan_execute_agent/synthesizer.py
class ResponseSynthesizer:
    async def synthesize(self, query: str, reranked_results: List[Dict]) -> str:
        # 최종 한국어 답변 생성
        pass
```

- [ ] 문서 간 관계 분석 프롬프트
- [ ] 한국어 답변 생성 프롬프트
- [ ] 참조 정보 포함 로직
- [ ] 답변 품질 검증

### **Phase 3 테스트**

#### 테스트 3.1: 문서 계획 수립
```python
async def test_document_planning_basic():
    """기본 문서 계획 수립이 작동하는지 확인"""
    planner = DocumentPlannerAgent()
    plan = await planner.create_plan("선박의 화재 감지 시스템 요구사항")
    
    assert "required_documents" in plan
    assert len(plan["required_documents"]) > 0
    assert "SOLAS_II2" in [doc["name"] for doc in plan["required_documents"]]

async def test_document_planning_edge_cases():
    """엣지 케이스 처리 확인"""
    # 빈 질문, 영어 질문, 관련 없는 질문 등
```

#### 테스트 3.2: 응답 합성
```python
async def test_response_synthesis_basic():
    """기본 응답 합성이 작동하는지 확인"""
    
async def test_response_synthesis_quality():
    """응답 품질 확인 (한국어, 완성도, 참조 포함)"""
```

#### 통합 테스트
```python
async def test_planner_to_synthesizer_integration():
    """계획 수립 → 검색 → 합성 전체 플로우 테스트"""
```

#### **Phase 3 완료 기준**
- [ ] 문서 계획 수립 정확도 > 90%
- [ ] 응답 합성 품질 검증 통과
- [ ] 통합 테스트 통과
- [ ] 한국어 답변 자연스러움 확인

---

## 📋 Phase 4: 메인 에이전트 구현

### **구현 목표**
- PlanExecuteAgent 메인 클래스 구현
- BaseAgent 인터페이스 준수

### **구현 체크리스트**

#### 4.1 기본 구조
```python
# agents/plan_execute_agent/agent.py
class PlanExecuteAgent(BaseAgent):
    def __init__(self):
        self.tools = {
            "neptune_search": NeptuneGraphRAGTool(),
            "cohere_rerank": CohereRerankingTool()
        }
        self.document_planner = DocumentPlannerAgent()
        self.response_synthesizer = ResponseSynthesizer()
```

- [ ] BaseAgent 상속 및 인터페이스 구현
- [ ] 도구 초기화 및 등록
- [ ] 컴포넌트 초기화
- [ ] 설정 로딩

#### 4.2 비스트리밍 구현
```python
async def process_message(self, message: str, session_id: str) -> Dict:
    # Stage 1: Plan + Execute
    search_plan = await self.document_planner.create_plan(message)
    search_results = await self.tools["neptune_search"].execute(
        query=message, document_filters=search_plan["required_documents"]
    )
    
    # Stage 2: Rerank + Respond
    reranked_results = await self.tools["cohere_rerank"].execute(
        query=message, documents=search_results["results"]
    )
    final_response = await self.response_synthesizer.synthesize(
        message, reranked_results["results"]
    )
    
    return self._format_response(final_response)
```

- [ ] 2단계 워크플로우 구현
- [ ] 에러 처리 및 복구
- [ ] 로깅 및 메트릭
- [ ] 응답 포맷팅

### **Phase 4 테스트**

#### 테스트 4.1: 전체 워크플로우
```python
async def test_plan_execute_agent_basic():
    """기본 워크플로우가 작동하는지 확인"""
    agent = PlanExecuteAgent()
    result = await agent.process_message(
        "선박의 고정식 소화 시스템 요구사항을 알려주세요",
        "test_session"
    )
    
    assert result["response"]
    assert result["references"]
    assert len(result["references"]) > 0

async def test_plan_execute_agent_edge_cases():
    """엣지 케이스 처리 확인"""
    # 빈 질문, 긴 질문, 특수 문자 등

async def test_plan_execute_agent_error_recovery():
    """에러 상황에서 복구 능력 확인"""
```

#### 성능 테스트
```python
async def test_plan_execute_agent_performance():
    """전체 응답 시간 측정 (< 10초)"""
    
async def test_plan_execute_agent_concurrent():
    """동시 요청 처리 능력 확인"""
```

#### **Phase 4 완료 기준**
- [ ] 전체 워크플로우 테스트 통과
- [ ] 성능 기준 만족 (< 10초)
- [ ] BaseAgent 인터페이스 완전 호환
- [ ] 기존 GraphRAG Agent와 동일한 품질

---

## 📋 Phase 5: 스트리밍 지원

### **구현 목표**
- 실시간 스트리밍 워크플로우 구현
- 기존 UI와 호환성 유지

### **구현 체크리스트**

#### 5.1 스트리밍 워크플로우
```python
async def astream(self, message: str, session_id: str):
    yield {"type": "workflow_start", "message": "Plan-Execute 워크플로우 시작..."}
    
    # Stage 1: Planning + Search
    yield {"type": "stage_start", "stage": "planning"}
    plan = await self.document_planner.create_plan(message)
    yield {"type": "plan_complete", "plan": plan}
    
    yield {"type": "stage_start", "stage": "search"}
    search_results = await self.tools["neptune_search"].execute(...)
    yield {"type": "search_complete", "count": search_results["count"]}
    
    # Stage 2: Rerank + Respond
    yield {"type": "stage_start", "stage": "rerank"}
    reranked_results = await self.tools["cohere_rerank"].execute(...)
    yield {"type": "rerank_complete", "count": reranked_results["count"]}
    
    yield {"type": "stage_start", "stage": "synthesis"}
    response = await self.response_synthesizer.synthesize(...)
    yield {"type": "workflow_complete", "response": response}
```

- [ ] 스트리밍 이벤트 정의
- [ ] 단계별 진행 상황 표시
- [ ] 에러 상황 스트리밍 처리
- [ ] 기존 UI 이벤트 형식 호환

### **Phase 5 테스트**

#### 테스트 5.1: 스트리밍 기능
```python
async def test_streaming_workflow():
    """스트리밍 워크플로우가 올바르게 작동하는지 확인"""
    agent = PlanExecuteAgent()
    events = []
    
    async for event in agent.astream("test query", "test_session"):
        events.append(event)
    
    # 필수 이벤트들이 순서대로 발생했는지 확인
    assert events[0]["type"] == "workflow_start"
    assert events[-1]["type"] == "workflow_complete"

async def test_streaming_ui_compatibility():
    """기존 UI와 호환성 확인"""
```

#### **Phase 5 완료 기준**
- [ ] 스트리밍 테스트 통과
- [ ] UI 호환성 확인
- [ ] 실시간 진행 상황 표시 작동
- [ ] 에러 상황 적절히 처리

---

## 📋 Phase 6: 통합 및 검증

### **구현 목표**
- 기존 시스템과 통합
- 성능 및 품질 검증

### **구현 체크리스트**

#### 6.1 시스템 통합
```python
# core/agent_manager.py 업데이트
def _load_agent_class(self, agent_config: Dict) -> BaseAgent:
    if agent_config.get("agent_class") == "PlanExecuteAgent":
        from agents.plan_execute_agent import PlanExecuteAgent
        return PlanExecuteAgent()
    # 기존 로직...

# config/agents.yaml 설정
agents:
  plan_execute:
    display_name: "Plan-Execute Agent"
    description: "Plan-Execute 패턴 기반 GraphRAG 에이전트"
    agent_class: "PlanExecuteAgent"
    bedrock_agent_id: "WT3ZJ25XCL"
    enabled: true
```

- [ ] AgentManager 통합
- [ ] 설정 파일 업데이트
- [ ] UI 컴포넌트 호환성 확인
- [ ] 기존 에이전트와 병행 운영 설정

#### 6.2 성능 비교 테스트
```python
async def test_performance_comparison():
    """기존 GraphRAG Agent vs PlanExecuteAgent 성능 비교"""
    
async def test_quality_comparison():
    """답변 품질 비교 (동일한 질문 세트)"""
    
async def test_resource_usage():
    """리소스 사용량 비교 (메모리, CPU)"""
```

### **Phase 6 테스트**

#### 통합 테스트
```python
async def test_full_system_integration():
    """전체 시스템 통합 테스트"""
    
async def test_ui_integration():
    """UI와의 통합 테스트"""
    
async def test_concurrent_agents():
    """여러 에이전트 동시 실행 테스트"""
```

#### 품질 검증
```python
def test_answer_quality_benchmark():
    """표준 질문 세트로 답변 품질 검증"""
    
def test_document_coverage():
    """11개 문서 편향 없이 검색하는지 확인"""
    
def test_korean_language_quality():
    """한국어 답변 자연스러움 확인"""
```

#### **Phase 6 완료 기준**
- [ ] 전체 시스템 통합 완료
- [ ] 성능이 기존 대비 유지 또는 개선
- [ ] 답변 품질이 기존 수준 유지
- [ ] 코드 라인 수 70% 감소 달성 (500+ → 150 이하)

---

## 🎯 최종 검증 체크리스트

### **기능 검증**
- [ ] 지능적 문서 선택 (편향 방지)
- [ ] 관계 기반 추론 (문서 간 연결점)
- [ ] 검색 정확도 (Cohere Reranking)
- [ ] 다국어 처리 (영어 검색 → 한국어 답변)

### **성능 검증**
- [ ] 응답 시간: < 10초
- [ ] 코드 복잡도: 150줄 이하
- [ ] 메모리 사용량: 기존 대비 감소
- [ ] 동시 처리: 5+ 세션

### **품질 검증**
- [ ] 답변 정확도: 기존 수준 유지
- [ ] 문서 다양성: 편향 없는 검색
- [ ] 한국어 품질: 자연스러운 번역
- [ ] UI 호환성: 기존 인터페이스 유지

### **유지보수성 검증**
- [ ] 코드 가독성: 명확한 2단계 구조
- [ ] 디버깅 용이성: 단계별 로깅
- [ ] 확장성: 새로운 도구 추가 용이
- [ ] 테스트 커버리지: > 80%

---

## 📊 성공 기준 요약

| 항목 | 현재 | 목표 | 측정 방법 |
|------|------|------|-----------|
| 코드 라인 수 | 500+ | 150 이하 | 라인 카운트 |
| 응답 시간 | ~8초 | < 10초 | 평균 응답 시간 |
| LLM 호출 | 3개 에이전트 | 2단계 | 호출 횟수 추적 |
| 의존성 | Lambda 3개 | 0개 | 의존성 목록 |
| 답변 품질 | 기준 | 유지 | 품질 평가 점수 |
| 문서 편향 | 있음 | 해결 | 문서별 검색 빈도 |

**이 가이드를 따라 단계별로 구현하고 테스트하면 안정적이고 검증된 PlanExecuteAgent를 완성할 수 있습니다.**