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
        self._render_system_info()
        st.markdown("---")
        self._render_graphrag_info()
        st.markdown("---")
        self._render_knowledge_graph()
        st.markdown("---")
        self._render_agent_info()
    
    def _render_session_info(self):
        """세션 정보 표시"""
        st.markdown("### 📋 세션 정보")
        st.markdown(f"**세션 ID:** `{st.session_state.session_id[:8]}...`")
        st.markdown(f"**메시지 수:** {len(st.session_state.messages)}")
        
        if st.button("🔄 새 세션 시작", width='stretch'):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.selected_agent = None
            st.rerun()
    
    def _render_agent_info(self):
        """현재 에이전트 정보 표시"""
        st.markdown("### 🚢 선박 소방 규정")
        
        # 지원 주제
        topics = [
            "고정식 소화 시스템",
            "휴대용 소화기", 
            "배수 시스템",
            "안전 구역",
            "SOLAS 규정"
        ]
        
        st.markdown("**지원 주제:**")
        for topic in topics:
            st.markdown(f"• {topic}")
    
    def _render_system_info(self):
        """시스템 정보 표시"""
        st.markdown("### ⚙️ 시스템 정보")
        
        # 사용 가능한 에이전트 수
        available_agents = self.agent_manager.get_available_agents()
        st.markdown(f"**사용 가능한 에이전트:** {len(available_agents)}개")
        
        # 에이전트 목록
        if available_agents:
            st.markdown("**에이전트 목록:**")
            st.markdown("🟢 Bedrock Agent")
        
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
    
    def _render_graphrag_info(self):
        """GraphRAG 정보 섹션"""
        st.markdown("### 🧠 GraphRAG")
        
        # KB 선택 라디오 버튼
        kb_option = st.radio(
            "Knowledge Base 선택:",
            options=["선택 안함", "bda-neptune"],  # "bda-neptune-2" 주석 처리
            index=1,  # 기본값으로 bda-neptune 선택
            key="kb_selector_radio"
        )
    
    def _render_agent_info(self):
        """현재 에이전트 정보 표시"""
        st.markdown("### 🚢 선박 소방 규정")
        
        # 지원 주제
        topics = [
            "고정식 소화 시스템",
            "휴대용 소화기", 
            "배수 시스템",
            "안전 구역",
            "SOLAS 규정"
        ]
        
        st.markdown("**지원 주제:**")
        for topic in topics:
            st.markdown(f"• {topic}")
    
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