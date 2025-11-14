"""
사이드바 UI 컴포넌트 - 정리된 버전
"""
import streamlit as st
import uuid

class Sidebar:
    """사이드바 관리 클래스"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
    
    def render_sidebar(self):
        """사이드바 전체 렌더링"""
        self._render_agent_selector()
        st.markdown("---")
        self._render_kb_selector()
        st.markdown("---")
        self._render_graph_selector()
        st.markdown("---")
        self._render_current_agent_info()
        st.markdown("---")
        self._render_session_controls()
    
    def _render_agent_selector(self):
        """에이전트 선택"""
        st.markdown("### 🤖 에이전트 선택")
        
        available_agents = self.agent_manager.get_available_agents()
        
        # 에이전트 옵션 생성
        options = []
        for agent in available_agents:
            icon = agent.ui_config.get('icon', '🤖') if agent.ui_config else '🤖'
            options.append(f"{icon} {agent.display_name}")
        
        # 라디오 버튼
        selected = st.radio(
            "에이전트:",
            options=options,
            index=2,  # Plan-Execute Agent (인덱스 2)
            key="agent_radio"
        )
        
        # 선택된 에이전트 찾기
        selected_index = options.index(selected)
        selected_agent = available_agents[selected_index].name
        
        # 세션 상태에 저장
        st.session_state.selected_agent = selected_agent
        
        # 디버그
        st.caption(f"선택: {selected_index} → {selected_agent}")
    
    def _render_kb_selector(self):
        """Knowledge Base 선택"""
        st.markdown("### 🧠 Knowledge Base")
        
        kb_options = [
            "🔥 PWRU19RDNE (최적)",
            "📚 CDPB5AI6BH (풍부)", 
            "⚠️ ZGBA1R5CS0 (제한적)"
        ]
        
        kb_ids = ["PWRU19RDNE", "CDPB5AI6BH", "ZGBA1R5CS0"]
        
        selected_kb = st.radio(
            "KB 선택:",
            options=kb_options,
            index=0,
            key="kb_radio"
        )
        
        kb_index = kb_options.index(selected_kb)
        st.session_state.selected_kb_id = kb_ids[kb_index]
    
    def _render_graph_selector(self):
        """지식 그래프 선택"""
        st.markdown("### 🕸️ 지식 그래프")
        
        graph_options = [
            "선택 안함",
            "🕸️ GraphRAG",
            "🔥 FSS GraphDB"
        ]
        
        selected_graph = st.radio(
            "그래프:",
            options=graph_options,
            index=0,
            key="graph_radio"
        )
        
        if selected_graph != "선택 안함":
            st.session_state.show_knowledge_graph = True
            st.session_state.selected_graph_type = selected_graph
        else:
            st.session_state.show_knowledge_graph = False
    
    def _render_current_agent_info(self):
        """현재 선택된 에이전트 정보"""
        selected_agent = st.session_state.get('selected_agent')
        if selected_agent:
            agent_config = next(
                (a for a in self.agent_manager.get_available_agents() 
                 if a.name == selected_agent), None
            )
            if agent_config:
                icon = agent_config.ui_config.get('icon', '🤖') if agent_config.ui_config else '🤖'
                st.markdown(f"### {icon} 현재 에이전트")
                st.markdown(f"**{agent_config.display_name}**")
                st.caption(agent_config.description)
    
    def _render_session_controls(self):
        """세션 제어"""
        st.markdown("### 📋 세션")
        
        if st.button("🔄 새 세션", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()