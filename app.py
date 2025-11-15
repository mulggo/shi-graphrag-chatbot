"""
확장 가능한 멀티 에이전트 Streamlit 애플리케이션
새로운 아키텍처로 리팩토링된 메인 앱
"""
import streamlit as st
import uuid
from core.agent_manager import AgentManager
from ui.agent_selector import AgentSelector
from ui.chat_interface import ChatInterface
from ui.reference_display import ReferenceDisplay
from ui.sidebar import Sidebar

# 페이지 설정
st.set_page_config(
    page_title="선박 규정 전문가 시스템",
    page_icon="🚢",
    layout="wide"
)

# 전역 매니저 초기화 (캐시 비활성화)
def get_agent_manager():
    return AgentManager()

def get_ui_components(_agent_manager):
    return {
        'agent_selector': AgentSelector(_agent_manager),
        'chat_interface': ChatInterface(_agent_manager),
        'reference_display': ReferenceDisplay(),
        'sidebar': Sidebar(_agent_manager)
    }

# 세션 상태 초기화
def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = 'plan_execute'  # Plan-Execute Agent를 기본값으로
    if "selected_kb_id" not in st.session_state:
        st.session_state.selected_kb_id = 'CDPB5AI6BH'  # 기본 KB
    if "previous_agent" not in st.session_state:
        st.session_state.previous_agent = None
    if "previous_kb_id" not in st.session_state:
        st.session_state.previous_kb_id = None

def main():
    initialize_session()
    
    # 매니저 및 UI 컴포넌트 초기화
    agent_manager = get_agent_manager()
    ui_components = get_ui_components(agent_manager)
    
    # 메인 제목
    st.title("🚢 선박 소방 규정 챗봇")
    st.markdown("선박 소방 시스템 및 SOLAS 규정에 대해 질문하세요")
    
    # 데이터 스키마 안내서 표시
    if st.session_state.get('show_data_schema', False):
        st.markdown("---")
        st.markdown("### 📊 데이터 구조 안내서")
        
        try:
            from data_structure_guide import schema_explorer
            schema_explorer.render_schema_explorer()
        except Exception as e:
            st.error(f"데이터 스키마 로드 실패: {e}")
    
    # 지식 그래프 표시
    elif st.session_state.get('show_knowledge_graph', False):
        selected_graph_type = st.session_state.get('selected_graph_type', '🕸️ GraphRAG')
        
        st.markdown("---")
        st.markdown(f"### {selected_graph_type}")
        
        # 그래프 타입별 설명 추가
        if selected_graph_type == "FSS 문서 GraphDB":
            st.markdown("""
            **Neptune SPARQL 기반 FSS 온톨로지 시각화**
            
            FSS(Fire Safety Systems) 규정의 구조화된 온톨로지를 보여주는 지식 그래프입니다.
            SPARQL 쿼리를 통해 실시간으로 데이터를 조회하여 시각화합니다.
            
            - 🔥 **FSS 챕터**: 17개 챕터별 구조화
            - 📋 **총 클래스**: 42개 온톨로지 클래스
            - 🏗️ **총 인스턴스**: 186개 구체적 인스턴스
            - ➡️ **방향성**: 화살표로 관계 방향 표시
            """)
        elif selected_graph_type == "📊 데이터 스키마 탐색기":
            st.markdown("""
            **Knowledge Base 및 Neptune DB 스키마 분석**
            
            이 도구는 시스템에서 사용하는 모든 데이터 소스의 내부 구조와 스키마를 탐색할 수 있게 해줍니다.
            개발자와 데이터 분석가를 위한 기술적 세부사항을 제공합니다.
            
            - 📚 **Knowledge Base**: 임베딩 벡터, 메타데이터 구조
            - 🕸️ **Neptune Analytics**: 그래프 스키마, 노드/엣지 타입
            - 🔗 **Neptune SPARQL**: RDF 온톨로지, 클래스 계층구조
            - 📋 **데이터 샘플**: 실제 데이터 구조 예시
            """)
        
        with st.spinner(f"{selected_graph_type}를 로드하고 있습니다..."):
            try:
                import streamlit.components.v1 as components
                
                if selected_graph_type == "📚 GraphRAG\n(bda+neptune)":
                    from knowledge_graph_bda import create_neptune_graph_bda
                    
                    # BDA Neptune Analytics 그래프
                    net = create_neptune_graph_bda()
                    html_string = net.generate_html()
                    components.html(html_string, height=900)
                    
                elif selected_graph_type == "⚡ GraphRAG\n(claude+neptune)":
                    from knowledge_graph_claude import create_neptune_graph_claude
                    
                    # Claude Neptune Analytics 그래프
                    net = create_neptune_graph_claude()
                    html_string = net.generate_html()
                    components.html(html_string, height=900)
                    
                elif selected_graph_type == "🔥 FSS GraphDB":
                    from fss_full_graph import get_full_ontology, create_full_graph
                    
                    # FSS 온톨로지 데이터 가져오기
                    data = get_full_ontology()
                    
                    if data and data['results']['bindings']:
                        st.success(f"✅ {len(data['results']['bindings'])}개 트리플 로드 완료")
                        
                        # FSS 그래프 생성
                        net, node_count, edge_count = create_full_graph(data)
                        st.info(f"📊 노드: {node_count}개, 엣지: {edge_count}개")
                        
                        # HTML 생성 및 표시 (GraphRAG와 동일한 방식)
                        html_string = net.generate_html()
                        components.html(html_string, height=900)  # 더 큰 높이
                    else:
                        st.error("❌ FSS 데이터를 가져올 수 없습니다.")
                        st.info("Neptune SPARQL 엔드포인트 연결을 확인해주세요.")
                

                
                # 닫기 버튼
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("❌ 지식 그래프 닫기", use_container_width=True):
                        st.session_state.show_knowledge_graph = False
                        st.session_state.selected_graph_type = None
                        st.rerun()
                        
            except Exception as e:
                st.error(f"지식 그래프 로드 실패: {e}")
                st.info("Neptune 연결을 확인해주세요.")
                if st.button("❌ 닫기"):
                    st.session_state.show_knowledge_graph = False
                    st.session_state.selected_graph_type = None
                    st.rerun()
    
    # 채팅 인터페이스 (지식 그래프나 데이터 스키마가 표시되지 않을 때만)
    else:
        # 사이드바에서 선택된 에이전트 사용 (기본값: firefighting)
        selected_agent = st.session_state.get('selected_agent', 'firefighting')
        selected_kb_id = st.session_state.get('selected_kb_id')
        
        # 에이전트나 KB 변경 감지 및 채팅 초기화
        if (st.session_state.previous_agent != selected_agent or 
            st.session_state.previous_kb_id != selected_kb_id):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.previous_agent = selected_agent
            st.session_state.previous_kb_id = selected_kb_id
            st.rerun()
        
        # 채팅 인터페이스
        ui_components['chat_interface'].render_chat_history()
        
        # 사용자 입력 처리
        if prompt := st.chat_input("질문을 입력하세요..."):
            # 사용자 메시지 추가
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt,
                "agent": selected_agent
            })
            
            # 채팅 메시지 표시
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # AI 응답 생성
            with st.chat_message("assistant"):
                with st.spinner("답변을 생성하고 있습니다..."):
                    # 선택된 에이전트로 메시지 라우팅 (KB ID 포함)
                    # st.write(f"🔍 디버그: selected_agent = {selected_agent}")
                    # st.write(f"🔍 디버그: selected_kb_id = {selected_kb_id}")
                    result = agent_manager.route_message(
                        selected_agent, 
                        prompt, 
                        st.session_state.session_id,
                        kb_id=selected_kb_id
                    )
                    # st.write(f"🔍 디버그: route_message 결과 = {result.get('success')}")
                    
                    # 에이전트 정보 표시
                    agent_config = next((a for a in agent_manager.get_available_agents() if a.name == selected_agent), None)
                    if agent_config:
                        icon = agent_config.ui_config.get('icon', '🤖') if agent_config.ui_config else '🤖'
                        st.caption(f"{icon} {agent_config.display_name} 사용 중")
                    
                    if result.get("success"):
                        # 응답 표시
                        st.markdown(result["content"])
                        
                        # 참조 정보 표시
                        references = result.get("references", [])
                        # st.write(f"🔍 디버그: 참조 개수 = {len(references)}")
                        if references:
                            # st.write(f"🔍 디버그: 첫 번째 참조 키 = {list(references[0].keys())}")
                            ui_components['reference_display'].render_references(references)
                        # else:
                            # st.write("🔍 디버그: 참조 없음")
                        
                        # 세션에 저장
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["content"],
                            "references": references,
                            "agent": selected_agent
                        })
                    else:
                        st.error(f"오류: {result.get('error', '알 수 없는 오류')}")

    
    # 사이드바
    with st.sidebar:
        ui_components['sidebar'].render_sidebar()

if __name__ == "__main__":
    main()