"""
Plan-Execute Agent 모듈
AWS IDP 패턴 기반 단순화된 GraphRAG 에이전트
"""

from .agent import PlanExecuteAgent

class Agent:
    """
    AgentManager 호환성을 위한 래퍼 클래스
    기존 에이전트 인터페이스와 동일한 형태로 동작
    """
    
    def __init__(self, config):
        """
        에이전트 초기화
        
        Args:
            config: AgentConfig 객체 (agents.yaml에서 로드됨)
        """
        self.config = config
        self.agent = PlanExecuteAgent(config, kb_id=config.knowledge_base_id)
    
    @property
    def kb_id(self):
        return self.agent.kb_id
    
    @kb_id.setter
    def kb_id(self, value):
        self.agent.kb_id = value
    
    def process_message(self, message: str, session_id: str) -> dict:
        """
        메시지 처리 (기존 인터페이스 호환)
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID
            
        Returns:
            dict: 응답 결과 (success, content, references 포함)
        """
        return self.agent.process_message(message, session_id)

# 모듈 레벨에서 Agent 클래스를 export
__all__ = ['Agent']