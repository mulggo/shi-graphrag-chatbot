"""
선박 소방 규정 전문 에이전트
기존 기능을 새로운 아키텍처로 마이그레이션
"""
from agents.base_agent import BaseAgent
from typing import Dict

class Agent(BaseAgent):
    """선박 소방 규정 전문 에이전트"""
    
    def __init__(self, config):
        super().__init__(config)
        
    def process_message(self, message: str, session_id: str) -> Dict:
        """
        소방 관련 메시지 처리
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID
            
        Returns:
            Dict: 처리 결과
        """
        # 소방 관련 키워드 확인 및 전처리
        enhanced_message = self._enhance_firefighting_query(message)
        
        # Bedrock Agent 호출
        result = self.invoke_bedrock_agent(enhanced_message, session_id)
        
        # 로깅
        self.log_interaction(message, result, session_id)
        
        return result
    
    def _enhance_firefighting_query(self, message: str) -> str:
        """소방 관련 쿼리 향상"""
        # 소방 관련 키워드 매핑
        firefighting_keywords = {
            "소화기": "fire extinguisher",
            "스프링클러": "sprinkler system",
            "화재 감지": "fire detection",
            "소화 시스템": "fire suppression system",
            "SOLAS": "Safety of Life at Sea",
            "고정식": "fixed fire fighting system",
            "휴대용": "portable fire extinguisher"
        }
        
        enhanced = message
        
        # 컨텍스트 추가
        if any(keyword in message for keyword in firefighting_keywords.keys()):
            enhanced = f"선박 소방 규정 관련 질문: {message}"
        
        return enhanced
    
    def get_capabilities(self) -> list:
        """소방 에이전트 특화 기능"""
        base_capabilities = super().get_capabilities()
        firefighting_capabilities = [
            "SOLAS 규정 해석",
            "소화 시스템 설계 가이드",
            "화재 위험 평가",
            "소방 장비 선택 지원",
            "규정 준수 확인"
        ]
        return base_capabilities + firefighting_capabilities