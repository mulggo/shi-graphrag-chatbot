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
        self._render_data_schema_button()
        st.markdown("---")
        self._render_agent_selector()
        st.markdown("---")
        self._render_kb_selector()
        st.markdown("---")
        self._render_graph_selector()
        st.markdown("---")
        self._render_session_controls()
    
    def _render_data_schema_button(self):
        """데이터 구조 안내서 버튼"""
        st.markdown("📊 **데이터 구조 안내서**")
        
        if st.button("📊 데이터 구조 보기", use_container_width=True):
            # 다른 모든 보기 상태 초기화
            st.session_state.show_knowledge_graph = False
            st.session_state.selected_graph_type = None
            # 데이터 스키마 보기 상태 설정
            st.session_state.show_data_schema = True
            st.rerun()
    
    def _render_agent_selector(self):
        """에이전트 선택"""
#        st.markdown("### 🤖 에이전트 선택")
        
        available_agents = self.agent_manager.get_available_agents()
        
        if not available_agents:
            st.error("사용 가능한 에이전트가 없습니다.")
            return
        
        # 에이전트 옵션 생성
        options = []
        agent_names = []
        for agent in available_agents:
            icon = agent.ui_config.get('icon', '🤖') if agent.ui_config else '🤖'
            options.append(f"{icon} {agent.display_name}")
            agent_names.append(agent.name)
        
        # 현재 선택된 에이전트의 인덱스 찾기
        current_agent = st.session_state.get('selected_agent', 'plan_execute')
        try:
            current_index = agent_names.index(current_agent)
        except ValueError:
            current_index = 0  # 기본값
        
        # 라디오 버튼
        selected = st.radio(
            "에이전트:",
            options=options,
            index=current_index,
            key="agent_radio"
        )
        
        # 선택된 에이전트 찾기
        selected_index = options.index(selected)
        selected_agent = agent_names[selected_index]
        
        # 세션 상태에 저장 (변경된 경우에만)
        if st.session_state.get('selected_agent') != selected_agent:
            st.session_state.selected_agent = selected_agent
            st.rerun()
        
        # 디버그
        # st.caption(f"선택: {selected_index} → {selected_agent}")
    
    def _render_kb_selector(self):
        """Knowledge Base 선택"""
        st.markdown("### 🧠 Knowledge Base")
        
        kb_options = [
            "🔥 GraphRAG(claude+neptune)",
            "📚 GraphRAG(bda+neptune)"
        ]
        
        kb_ids = ["PWRU19RDNE", "CDPB5AI6BH"]
        
        # 현재 선택된 KB의 인덱스 찾기
        current_kb = st.session_state.get('selected_kb_id', 'PWRU19RDNE')
        try:
            current_kb_index = kb_ids.index(current_kb)
        except ValueError:
            current_kb_index = 0  # 기본값 (PWRU19RDNE)
        
        selected_kb = st.radio(
            "KB 선택:",
            options=kb_options,
            index=current_kb_index,
            key="kb_radio"
        )
        
        kb_index = kb_options.index(selected_kb)
        new_kb_id = kb_ids[kb_index]
        
        # KB 변경된 경우에만 업데이트
        if st.session_state.get('selected_kb_id') != new_kb_id:
            st.session_state.selected_kb_id = new_kb_id
            st.rerun()
    
    def _render_graph_selector(self):
        """지식 그래프 선택"""
        st.markdown("### 🕸️ 지식 그래프")
        
        graph_options = [
            "선택 안함",
            "📚 GraphRAG(bda+neptune)",
            "⚡ GraphRAG(claude+neptune)",
            "🔥 FSS GraphDB"
        ]
        
        selected_graph = st.radio(
            "그래프:",
            options=graph_options,
            index=0,
            key="graph_radio"
        )
        
        # 상태 변경 감지 후에만 rerun 호출
        current_show = st.session_state.get('show_knowledge_graph', False)
        current_type = st.session_state.get('selected_graph_type', '')
        
        if selected_graph != "선택 안함":
            new_show = True
            new_type = selected_graph
        else:
            new_show = False
            new_type = ''
        
        # 상태가 실제로 변경된 경우에만 rerun
        if current_show != new_show or current_type != new_type:
            st.session_state.show_knowledge_graph = new_show
            st.session_state.selected_graph_type = new_type
            # 지식 그래프 선택 시 데이터 스키마 비활성화
            if new_show:
                st.session_state.show_data_schema = False
            st.rerun()
    
    def _render_current_agent_info(self):
        """현재 선택된 에이전트 정보"""
        # 에이전트 정보 숨김 처리
        pass
        # selected_agent = st.session_state.get('selected_agent')
        # if selected_agent:
        #     agent_config = next(
        #         (a for a in self.agent_manager.get_available_agents() 
        #          if a.name == selected_agent), None
        #     )
        #     if agent_config:
        #         icon = agent_config.ui_config.get('icon', '🤖') if agent_config.ui_config else '🤖'
        #         st.markdown(f"### {icon} 현재 에이전트")
        #         st.markdown(f"**{agent_config.display_name}**")
        #         st.caption(agent_config.description)
    
    def _render_session_controls(self):
        """세션 제어"""
        st.markdown("### 📋 세션")
        
        if st.button("🔄 새 세션", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            # 지식 그래프 초기화
            st.session_state.show_knowledge_graph = False
            st.session_state.selected_graph_type = None
            st.rerun()