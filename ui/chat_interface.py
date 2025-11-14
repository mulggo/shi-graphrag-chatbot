"""
채팅 인터페이스 UI 컴포넌트
"""
import streamlit as st
from typing import Dict, List

class ChatInterface:
    """채팅 인터페이스 관리 클래스"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
    
    def render_chat_history(self):
        """채팅 히스토리 렌더링"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    self._render_assistant_message(message)
                else:
                    self._render_user_message(message)
    
    def _render_user_message(self, message: Dict):
        """사용자 메시지 렌더링"""
        st.markdown(message["content"])
    
    def _render_assistant_message(self, message: Dict):
        """어시스턴트 메시지 렌더링"""
        # 메인 응답
        st.markdown(message["content"])
        
        # 참조 정보가 있으면 간략 표시
        references = message.get("references", [])
        if references:
            # Plan-Execute Agent와 기존 에이전트 형식 모두 지원
            ref_summary = ", ".join([
                f"[{i}] {ref.get('source_file', ref.get('source', 'Unknown'))}" 
                for i, ref in enumerate(references, 1)
            ])
            st.caption(f"📚 참조: {ref_summary}")
            
            # 참조 상세 표시
            from ui.reference_display import ReferenceDisplay
            display = ReferenceDisplay()
            display.render_references(references)
        
