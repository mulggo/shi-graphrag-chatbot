# 멀티 에이전트 애플리케이션 문서 (app.py)

## 개요

메인 Streamlit 애플리케이션(`app.py`)은 멀티 에이전트 선박 소화 규칙 챗봇 시스템을 위한 통합 인터페이스를 제공합니다. 조건부 UI 모드, 지식 그래프 시각화, 지능형 에이전트 라우팅을 특징으로 합니다.

## 아키텍처 개요

애플리케이션은 두 가지 주요 모드로 작동합니다:
1. **채팅 모드**: 전문 에이전트와의 대화형 Q&A
2. **그래프 모드**: 지식 그래프 시각화 및 탐색

## 주요 기능

### 1. 멀티 에이전트 인터페이스
- **에이전트 매니저 통합**: 중앙화된 에이전트 라우팅 및 관리
- **구성 기반**: YAML 구성에서 로드되는 에이전트
- **조건부 UI**: 그래프 시각화 중 채팅 인터페이스 숨김
- **에이전트 선택**: 다중 지식 베이스 옵션 (bda-neptune, bda-neptune-2)

### 2. 지식 그래프 시각화
- **이중 그래프 유형**: GraphRAG (Neptune Analytics) 및 FSS 온톨로지 (SPARQL)
- **대화형 시각화**: 완전한 상호작용이 가능한 900px 높이
- **실시간 전환**: 그래프 유형 간 원활한 전환
- **성능 최적화**: 2,000개 이상의 노드를 효율적으로 처리

### 3. 향상된 채팅 시스템
- **멀티 에이전트 지원**: 적절한 전문 에이전트로 쿼리 라우팅
- **참조 통합**: 고급 문서 참조 추출 및 표시
- **세션 관리**: 지속적인 대화 컨텍스트
- **한국어/영어 지원**: 이중 언어 인터페이스 및 응답

## 핵심 구성 요소

### 멀티 에이전트 시스템 통합
```python
# 에이전트 매니저 초기화
@st.cache_resource
def get_agent_manager():
    return AgentManager()

# UI 구성 요소 초기화  
@st.cache_resource
def get_ui_components(_agent_manager):
    return {
        'agent_selector': AgentSelector(_agent_manager),
        'chat_interface': ChatInterface(_agent_manager),
        'reference_display': ReferenceDisplay(),
        'sidebar': Sidebar(_agent_manager)
    }
```

### 세션 상태 관리
- `messages`: 에이전트 속성이 포함된 대화 기록
- `session_id`: UUID 기반 세션 식별자
- `selected_agent`: 현재 활성 에이전트
- `show_knowledge_graph`: 그래프 시각화 상태
- `selected_graph_type`: 활성 그래프 유형

### 조건부 UI 로직
```python
# 채팅 모드 (그래프가 활성화되지 않은 경우)
if not st.session_state.get('show_knowledge_graph', False):
    # 채팅 인터페이스 표시
    ui_components['chat_interface'].render_chat_history()

# 그래프 모드 (그래프가 선택된 경우)
if st.session_state.get('show_knowledge_graph', False):
    # 지식 그래프 시각화 표시
    selected_graph_type = st.session_state.get('selected_graph_type')
```

## 사용자 인터페이스 구성 요소

### 통합 사이드바 (`ui/sidebar.py`)
- **시스템 정보**: 에이전트 상태 및 가용성
- **GraphRAG 섹션**: 지식 베이스 선택 (bda-neptune, bda-neptune-2)
- **지식 그래프 선택기**: 라디오 버튼을 통한 그래프 유형 선택
- **에이전트 정보**: 현재 에이전트 기능 및 지원 주제
- **세션 관리**: 세션 제어 및 정보

### 채팅 인터페이스 (`ui/chat_interface.py`)
- **조건부 표시**: 그래프 모드가 비활성화된 경우에만 표시
- **에이전트 속성**: 담당 에이전트로 태그된 메시지
- **참조 통합**: 원활한 참조 표시
- **멀티 에이전트 기록**: 에이전트 전환 간 대화 컨텍스트

### 지식 그래프 뷰어
- **GraphRAG 시각화**: 2,000개 노드, 3,000개 엣지를 가진 Neptune Analytics
- **FSS 온톨로지 그래프**: SPARQL 기반 의미론적 관계
- **대화형 제어**: 줌, 팬, 노드 선택
- **성능 최적화**: 부드러운 렌더링을 위한 900px 높이

### 참조 표시 (`ui/reference_display.py`)
- **향상된 메타데이터**: 소스 속성 및 신뢰도 점수
- **이미지 통합**: S3 호스팅 원본 문서 이미지
- **OCR 텍스트 추출**: 검색 가능한 문서 내용
- **다중 형식 지원**: PDF, 이미지 및 텍스트 참조

## 구성

### 현재 AWS 리소스
- **Bedrock Agent ID**: `WT3ZJ25XCL`
- **Agent Alias ID**: `3RWZZLJDY1`
- **리전**: `us-west-2`

### Streamlit 구성
- **페이지 제목**: "선박 Firefighting 규칙 챗봇"
- **페이지 아이콘**: 🚢
- **레이아웃**: 더 나은 콘텐츠 표시를 위한 와이드 모드

## 오류 처리

### S3 이미지 로딩
- 누락되거나 접근할 수 없는 이미지의 우아한 처리
- 사용자 친화적인 오류 메시지
- 이미지 실패 시 텍스트 전용 표시로 폴백

### Agent 통신
- Bedrock Agent API 호출에 대한 예외 처리
- 사용자에게 오류 메시지 표시
- 개별 요청 실패에도 불구하고 서비스 지속

## 성능 최적화

### 캐싱
- `@st.cache_resource`를 사용한 AWS 클라이언트 캐싱
- 반복적인 클라이언트 초기화 방지
- 응답 시간 개선

### 스트리밍 응답
- Agent 응답의 실시간 표시
- 참조 정보의 점진적 로딩
- 즉각적인 피드백으로 향상된 사용자 경험

## 사용 예시

### 기본 질의
```
사용자: "선박 설계시 firefighting 규칙에 대해 알려주세요"
시스템: [Bedrock Agent를 통해 질의 처리]
응답: [참조가 포함된 상세한 답변]
```

### 참조 상호작용
1. 사용자가 참조 번호 [1], [2] 등이 포함된 응답을 받음
2. 응답 아래 확장 가능한 섹션에 참조 표시
3. 각 참조는 OCR 텍스트와 원본 이미지를 보여줌
4. 메타데이터는 추가 문서 컨텍스트 제공

## 문제 해결

### 일반적인 문제
1. **AWS 자격 증명**: 적절한 AWS 구성 확인
2. **리전 설정**: us-west-2 리전 액세스 확인
3. **Agent 권한**: Bedrock Agent 액세스 권한 확인
4. **S3 액세스**: S3 버킷 읽기 권한 확인

### 디버그 정보
- 추적을 위해 사이드바에 세션 ID 표시
- 인터페이스에 직접 오류 메시지 표시
- 개발 디버깅을 위한 콘솔 로깅

## 향후 개선사항

### 계획된 기능
- 다국어 응답 지원
- 고급 검색 필터
- 문서 업로드 기능
- 대화 기록 내보내기
- 향상된 참조 링크 시스템