"""
Workflow Agents - Strands Agent 기반 멀티 에이전트 워크플로우

각 에이전트는 Strands Agent 객체로 구현되어 LLM이 추론하며 도구를 사용합니다.
ReAct 패턴: Think (추론) → Act (도구 호출) → Observe (결과 평가) → 반복

Requirements: 4.1-4.6 (Query Analysis), 5.1-5.8 (Retrieval), 6.1-6.5 (Synthesis)
"""
from typing import Dict
import logging

from strands import Agent

from .prompts import get_prompt_by_agent_type
from .tools import extract_entities, kb_retrieve

# 로깅 설정
logger = logging.getLogger(__name__)


def create_query_analysis_agent(invocation_state: Dict) -> Agent:
    """
    쿼리 분석 Strands Agent 생성
    
    LLM이 사용자 질문을 분석하고 classify_query, extract_entities 도구를 사용하여
    검색 전략을 생성합니다.
    
    ReAct 패턴:
    - Think: "이 질문의 유형은? 어떤 엔티티가 중요한가?"
    - Act: classify_query, extract_entities 도구 호출
    - Observe: 결과를 종합하여 검색 전략 생성
    
    Args:
        invocation_state: Lambda ARN 및 KB ID 포함 (Agent 호출 시 사용)
        
    Returns:
        Strands Agent 객체
    """
    logger.info("쿼리 분석 Agent 생성")
    return Agent(
        system_prompt=get_prompt_by_agent_type("query_analysis"),
        tools=[extract_entities]
    )


def create_retrieval_agent(invocation_state: Dict) -> Agent:
    """
    검색 실행 Strands Agent 생성
    
    LLM이 KB 검색을 수행하고, 결과의 충분성을 평가하며, 필요시 재검색합니다.
    
    핵심 기능 (LLM이 추론):
    - 검색 결과가 충분한지 판단
    - 검색된 문서가 적합한지 평가
    - 더 필요한 문서가 있는지 추론
    - 필요시 다른 키워드로 재검색 (최대 3회)
    
    ReAct 패턴:
    - Think: "이 검색 결과로 질문에 답할 수 있는가?"
    - Act: kb_retrieve 도구 호출
    - Observe: 결과 평가 - 충분한가? 적합한 문서인가?
    - Think: "더 필요한 정보가 있는가?"
    - Act: 필요시 다른 키워드로 재검색
    - Finish: 충분한 결과 확보 시 완료
    
    Args:
        invocation_state: Lambda ARN 및 KB ID 포함 (Agent 호출 시 사용)
        
    Returns:
        Strands Agent 객체
    """
    logger.info("검색 실행 Agent 생성")
    return Agent(
        system_prompt=get_prompt_by_agent_type("kb_retrieval"),
        tools=[kb_retrieve]
    )


def create_synthesis_agent(invocation_state: Dict) -> Agent:
    """
    응답 합성 Strands Agent 생성
    
    LLM이 검색 결과를 분석하고 한국어 답변을 생성합니다.
    
    ReAct 패턴:
    - Think: "검색된 정보를 어떻게 조합하여 답변할까?"
    - Act: 정보 통합 및 답변 생성
    - Observe: 답변의 완전성 확인
    
    Args:
        invocation_state: 설정 정보 포함 (Agent 호출 시 사용)
        
    Returns:
        Strands Agent 객체
    """
    logger.info("응답 합성 Agent 생성")
    return Agent(
        system_prompt=get_prompt_by_agent_type("response_synthesis"),
        tools=[]
    )
