"""
에이전트 선택 UI 컴포넌트
사용자가 다양한 에이전트 중에서 선택할 수 있는 인터페이스
"""
import streamlit as st
from typing import List, Optional
from core.agent_manager import AgentConfig

class AgentSelector:
    """에이전트 선택기 UI 컴포넌트"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
    
    def render_agent_tabs(self) -> Optional[str]:
        """에이전트 탭 렌더링"""
        available_agents = self.agent_manager.get_available_agents()
        
        if not available_agents:
            st.error("사용 가능한 에이전트가 없습니다.")
            return None
        
        # 탭 생성
        tab_names = [agent.display_name for agent in available_agents]
        tabs = st.tabs(tab_names)
        
        selected_agent = None
        
        for i, (tab, agent) in enumerate(zip(tabs, available_agents)):
            with tab:
                self._render_agent_info(agent)
                if st.button(f"{agent.display_name} 선택", key=f"select_{agent.name}"):
                    selected_agent = agent.name
                    st.session_state.selected_agent = agent.name
        
        return selected_agent or st.session_state.get('selected_agent')
    
    def render_agent_selector(self) -> Optional[str]:
        """드롭다운 방식 에이전트 선택기"""
        available_agents = self.agent_manager.get_available_agents()
        
        if not available_agents:
            st.error("사용 가능한 에이전트가 없습니다.")
            return None
        
        # 선택 옵션 생성
        options = {f"{agent.ui_config.get('icon', '🤖')} {agent.display_name}": agent.name 
                  for agent in available_agents}
        
        selected_display = st.selectbox(
            "전문 분야를 선택하세요:",
            options.keys(),
            key="agent_selector"
        )
        
        return options[selected_display] if selected_display else None
    
    def _render_agent_info(self, agent: AgentConfig):
        """에이전트 정보 표시"""
        # 아이콘과 설명
        icon = agent.ui_config.get('icon', '🤖')
        color = agent.ui_config.get('color', '#000000')
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px;">{icon}</div>
            <h3 style="color: {color};">{agent.display_name}</h3>
            <p>{agent.description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 지원 주제
        topics = agent.ui_config.get('topics', [])
        if topics:
            st.markdown("**지원 주제:**")
            for topic in topics:
                st.markdown(f"• {topic}")
    
    def render_current_agent_info(self, agent_name: str):
        """현재 선택된 에이전트 정보 표시"""
        agent_config = self.agent_manager.agents.get(agent_name)
        if not agent_config:
            return
        
        icon = agent_config.ui_config.get('icon', '🤖')
        color = agent_config.ui_config.get('color', '#000000')
        
        st.markdown(f"""
        <div style="background-color: {color}20; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <strong>{icon} {agent_config.display_name}</strong><br>
            <small>{agent_config.description}</small>
        </div>
        """, unsafe_allow_html=True)