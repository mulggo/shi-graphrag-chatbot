"""
사이드바 UI 컴포넌트
"""
import streamlit as st
import uuid
from typing import Dict

class Sidebar:
    """사이드바 관리 클래스"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
    
    def render_sidebar(self):
        """사이드바 전체 렌더링"""
        self._render_data_structure_info()
        st.markdown("---")
        self._render_system_info()
        st.markdown("---")
        self._render_graphrag_info()
        st.markdown("---")
        self._render_knowledge_graph()
        st.markdown("---")
        self._render_agent_info()
        st.markdown("---")
        self._render_session_info()
    
    def _render_session_info(self):
        """세션 정보 표시"""
        st.markdown("### 📋 세션 정보")
        st.markdown(f"**세션 ID:** `{st.session_state.session_id[:8]}...`")
        st.markdown(f"**메시지 수:** {len(st.session_state.messages)}")
        
        if st.button("🔄 새 세션 시작", width='stretch'):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
    def _render_agent_info(self):
        """현재 에이전트 정보 표시"""
        selected_agent = st.session_state.get('selected_agent')
        if selected_agent:
            agent_config = next((a for a in self.agent_manager.get_available_agents() if a.name == selected_agent), None)
            if agent_config:
                icon = agent_config.ui_config.get('icon', '🤖') if agent_config.ui_config else '🤖'
                st.markdown(f"### {icon} 현재 에이전트")
                st.markdown(f"**{agent_config.display_name}**")
                st.markdown(f"{agent_config.description}")
    
    def _render_data_structure_info(self):
        """데이터 구조 정보 표시"""
        st.markdown("### 📊 데이터 구조")
        
        # 데이터 구조 안내서 라디오 버튼
        schema_option = st.radio(
            "데이터 구조:",
            options=["선택 안함", "📊 데이터 구조 안내서"],
            index=0,
            key="data_schema_radio"
        )
        
        # 라디오 버튼 선택에 따라 상태 업데이트
        if schema_option == "📊 데이터 구조 안내서":
            if not st.session_state.get('show_data_schema', False):
                st.session_state.show_data_schema = True
                st.rerun()
        else:
            if st.session_state.get('show_data_schema', False):
                st.session_state.show_data_schema = False
                st.rerun()
    
    def _render_system_info(self):
        """에이전트 선택 정보 표시"""
        st.markdown("### 🤖 에이전트 선택")
        
        # 사용 가능한 에이전트 수
        available_agents = self.agent_manager.get_available_agents()
        st.markdown(f"**사용 가능한 에이전트:** {len(available_agents)}개")
        
        # 에이전트 이름과 라벨 매핑
        agent_names = [agent.name for agent in available_agents]
        agent_labels = []
        for agent in available_agents:
            icon = agent.ui_config.get('icon', '🤖') if agent.ui_config else '🤖'
            agent_labels.append(f"{icon} {agent.display_name}")
        
        # 기본값 설정 (Plan-Execute Agent 우선)
        default_index = 0
        if "plan_execute" in agent_names:
            default_index = agent_names.index("plan_execute")
        
        # 라디오 버튼 렌더링
        selected_label = st.radio(
            "에이전트 선택:",
            options=agent_labels,
            index=default_index,
            key="agent_radio_selector"
        )
        
        # 선택된 에이전트 찾기
        selected_index = agent_labels.index(selected_label)
        selected_agent = agent_names[selected_index]
        
        # 세션 상태에 즉시 저장
        st.session_state.selected_agent = selected_agent
        
        # 디버그 정보
        with st.expander("🔧 디버그 정보"):
            st.write(f"에이전트 순서: {agent_names}")
            st.write(f"선택된 인덱스: {selected_index}")
            st.write(f"선택된 에이전트: {selected_agent}")
    
    def _render_graphrag_info(self):
        """GraphRAG 정보 섹션"""
        st.markdown("### 🧠 GraphRAG")
        
        # KB 선택 라디오 버튼 (3개 KB 추가)
        kb_options = {
            "선택 안함": None,
            "🔥 PWRU19RDNE (최적)": "PWRU19RDNE",
            "📚 CDPB5AI6BH (풍부)": "CDPB5AI6BH", 
            "⚠️ ZGBA1R5CS0 (제한적)": "ZGBA1R5CS0"
        }
        
        selected_kb_label = st.radio(
            "Knowledge Base 선택:",
            options=list(kb_options.keys()),
            index=1,  # 기본값으로 PWRU19RDNE 선택
            key="kb_selector_radio"
        )
        
        # 선택된 KB ID를 세션 상태에 저장
        st.session_state.selected_kb_id = kb_options[selected_kb_label]
        
        # KB 정보 표시
        if st.session_state.selected_kb_id:
            kb_info = {
                "PWRU19RDNE": "✅ SOLAS 문서 풍부, 최적 성능",
                "CDPB5AI6BH": "📖 가장 많은 검색 결과", 
                "ZGBA1R5CS0": "⚠️ 제한적 문서, 테스트용"
            }
            st.markdown(f"**상태:** {kb_info.get(st.session_state.selected_kb_id, '알 수 없음')}")
    
    def _render_knowledge_graph(self):
        """지식 그래프 섹션 렌더링"""
        st.markdown("### 🕸️ 지식 그래프")
        st.markdown("Neptune Analytics 기반 문서 관계 시각화")
        
        # 라디오 버튼으로 지식 그래프 선택
        graph_option = st.radio(
            "그래프 선택:",
            options=["선택 안함", "🕸️ 모든 문서의 GraphRAG", "FSS 문서 GraphDB"],
            index=0,
            key="knowledge_graph_radio"
        )
        
        # 라디오 버튼 선택에 따라 상태 업데이트
        if graph_option in ["🕸️ 모든 문서의 GraphRAG", "FSS 문서 GraphDB"]:
            if not st.session_state.get('show_knowledge_graph', False) or st.session_state.get('selected_graph_type') != graph_option:
                st.session_state.show_knowledge_graph = True
                st.session_state.selected_graph_type = graph_option
                st.rerun()
        else:
            if st.session_state.get('show_knowledge_graph', False):
                st.session_state.show_knowledge_graph = False
                st.session_state.selected_graph_type = None
                st.rerun()