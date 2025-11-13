"""
GraphRAG Agent - Main orchestrator for multi-agent workflow

이 에이전트는 Strands workflow를 사용하여 세 개의 전문 에이전트를 조율합니다:
1. QueryAnalysisAgent: 사용자 질문 분석 및 검색 전략 생성
2. RetrievalAgent: KB 검색 및 reranking 수행
3. SynthesisAgent: 검색 결과를 한국어 답변으로 합성

Requirements: 1.1-1.5 (Multi-agent workflow), 10.1-10.4 (Integration)
"""
import logging
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from agents.base_agent import BaseAgent

from .workflow_agents import (
    create_query_analysis_agent,
    create_retrieval_agent,
    create_synthesis_agent
)
from .metrics import get_metrics

# 로깅 설정
logger = logging.getLogger(__name__)


class Agent(BaseAgent):
    """
    GraphRAG Agent - Strands workflow 기반 멀티 에이전트 오케스트레이터
    
    이 에이전트는 기존 Bedrock Agent를 사용하지 않고,
    Strands workflow를 통해 세 개의 전문 에이전트를 조율하여
    지능형 GraphRAG 검색을 수행합니다.
    
    Requirements:
    - 1.1-1.5: Multi-agent workflow architecture
    - 10.1-10.4: Integration with existing system
    """
    
    def __init__(self, config):
        """
        GraphRAG Agent 초기화
        
        Args:
            config: AgentConfig 객체
        """
        super().__init__(config)
        
        # Lambda 함수 ARN 설정
        lambda_function_names = getattr(config, 'lambda_function_names', {})
        self.lambda_classify_query_arn = lambda_function_names.get('classify_query', '')
        self.lambda_extract_entities_arn = lambda_function_names.get('extract_entities', '')
        self.lambda_kb_retrieve_arn = lambda_function_names.get('kb_retrieve', '')
        
        # Reranker 모델 ARN (선택사항)
        self.reranker_model_arn = getattr(config, 'reranker_model_arn', None)
        
        # Bedrock 모델 ID
        self.model_id = getattr(config, 'bedrock_model_id', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        
        # 메트릭 수집기 초기화
        self.metrics = get_metrics()
        
        # 워크플로우 에이전트 초기화
        self._initialize_workflow_agents()
        
        logger.info(f"GraphRAG Agent 초기화 완료: kb_id={self.knowledge_base_id}")
    
    def _initialize_workflow_agents(self):
        """
        워크플로우 에이전트 초기화
        
        세 개의 전문 에이전트를 프롬프트와 함께 초기화합니다.
        """
        try:
            # invocation_state 생성 (Lambda ARN 및 KB ID)
            # Strands Agent가 도구 호출 시 ToolContext를 통해 자동으로 전달합니다
            self.invocation_state = {
                'lambda_classify_query_arn': self.lambda_classify_query_arn,
                'lambda_extract_entities_arn': self.lambda_extract_entities_arn,
                'lambda_kb_retrieve_arn': self.lambda_kb_retrieve_arn,
                'kb_id': self.knowledge_base_id,
                'reranker_model_arn': self.reranker_model_arn
            }
            
            # Strands Agent 기반 워크플로우 에이전트 생성
            # 각 에이전트는 LLM이 추론하며 도구를 사용하는 진짜 Strands Agent입니다
            self.query_analysis_agent = create_query_analysis_agent(
                invocation_state=self.invocation_state
            )
            
            self.retrieval_agent = create_retrieval_agent(
                invocation_state=self.invocation_state
            )
            
            self.synthesis_agent = create_synthesis_agent(
                invocation_state=self.invocation_state
            )
            
            logger.info("워크플로우 에이전트 초기화 완료")
            
        except Exception as e:
            logger.error(f"워크플로우 에이전트 초기화 실패: {str(e)}")
            raise
    
    def process_message(self, message: str, session_id: str) -> Dict:
        """
        메시지 처리 - 멀티 에이전트 워크플로우 실행
        
        이 메서드는 BaseAgent 인터페이스를 구현하며,
        세 단계의 워크플로우를 순차적으로 실행합니다:
        
        1. Query Analysis: 질문 분석 및 검색 전략 생성
        2. KB Retrieval: Knowledge Base 검색 및 reranking
        3. Response Synthesis: 검색 결과를 한국어 답변으로 합성
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID
            
        Returns:
            Dict: {
                "success": bool,
                "content": str,              # 한국어 답변
                "references": List[Dict],    # ReferenceDisplay 호환 형식
                "agent_name": str,
                "metadata": Dict             # 워크플로우 메타데이터
            }
        """
        workflow_start_time = time.time()
        
        try:
            logger.info(f"워크플로우 시작: session={session_id}, message='{message[:50]}...'")
            
            # Step 1: Query Analysis (텍스트 → 텍스트)
            logger.info("Step 1: 쿼리 분석 시작")
            query_analysis_start = time.time()
            
            query_analysis_result = self.query_analysis_agent(message, invocation_state=self.invocation_state)
            query_analysis_text = str(query_analysis_result)
            
            query_analysis_duration = time.time() - query_analysis_start
            logger.info(f"Step 1 완료: duration={query_analysis_duration:.2f}s")
            self.metrics.record_query_analysis_time(query_analysis_duration)
            
            # Step 2: KB Retrieval (텍스트 → 텍스트)
            logger.info("Step 2: KB 검색 시작")
            retrieval_start = time.time()
            
            retrieval_prompt = f"""쿼리 분석 결과의 영어 키워드를 사용하여 KB에서 문서를 검색하세요.

원본 질문: {message}

쿼리 분석 결과:
{query_analysis_text}

중요: 첫 번째 검색은 쿼리 분석 결과의 영어 키워드를 사용하세요.
문서가 주로 영어로 작성되어 있어 영어 키워드가 더 정확한 검색 결과를 제공합니다.
검색 결과가 불충분한 경우 다른 키워드 조합이나 한국어 키워드를 시도하세요."""
            
            retrieval_result = self.retrieval_agent(retrieval_prompt, invocation_state=self.invocation_state)
            retrieval_text = str(retrieval_result)
            
            retrieval_duration = time.time() - retrieval_start
            logger.info(f"Step 2 완료: duration={retrieval_duration:.2f}s")
            self.metrics.record_retrieval_time(retrieval_duration, 0)
            
            # Step 3: Response Synthesis (텍스트 → 텍스트)
            logger.info("Step 3: 응답 합성 시작")
            synthesis_start = time.time()
            
            synthesis_prompt = f"""원본 질문: {message}

검색 결과:
{retrieval_text}

위 검색 결과를 바탕으로 질문에 대한 포괄적인 한국어 답변을 생성하세요."""
            
            synthesis_result = self.synthesis_agent(synthesis_prompt, invocation_state=self.invocation_state)
            synthesis_text = str(synthesis_result)
            
            synthesis_duration = time.time() - synthesis_start
            logger.info(f"Step 3 완료: duration={synthesis_duration:.2f}s")
            self.metrics.record_synthesis_time(synthesis_duration, 'unknown')
            
            # 전체 워크플로우 완료
            total_duration = time.time() - workflow_start_time
            self.metrics.record_workflow_duration(total_duration, success=True)
            
            # 최종 포맷팅 (한 번만)
            result = self._format_final_response(
                synthesis_text=synthesis_text,
                retrieval_text=retrieval_text,
                message=message,
                durations={
                    'query_analysis': query_analysis_duration,
                    'retrieval': retrieval_duration,
                    'synthesis': synthesis_duration,
                    'total': total_duration
                }
            )
            
            # 로깅
            self.log_interaction(message, result, session_id)
            
            logger.info(f"워크플로우 완료: total_duration={total_duration:.2f}s, success={result['success']}")
            
            return result
            
        except Exception as e:
            logger.error(f"워크플로우 실패: {str(e)}", exc_info=True)
            
            # 전체 워크플로우 실패 시간 기록
            total_duration = time.time() - workflow_start_time
            self.metrics.record_workflow_duration(total_duration, success=False)
            
            # 에러 유형 분류 및 메트릭 기록
            error_type = self._classify_error(str(e))
            self.metrics.record_error(error_type, 'workflow')
            
            # 에러 처리
            error_result = self._handle_workflow_failure(message, str(e), session_id)
            
            # 에러 로깅
            self.log_interaction(message, error_result, session_id)
            
            return error_result
    
    def _format_response(
        self,
        synthesis_results: Dict,
        search_strategy: Dict,
        retrieval_results: Dict,
        durations: Dict
    ) -> Dict:
        """
        워크플로우 결과를 UI 호환 형식으로 변환
        
        ReferenceDisplay 컴포넌트와 호환되는 형식으로 응답을 포맷팅합니다.
        
        Args:
            synthesis_results: 합성 에이전트 결과
            search_strategy: 쿼리 분석 결과
            retrieval_results: 검색 결과
            durations: 각 단계의 소요 시간
            
        Returns:
            Dict: UI 호환 형식의 응답
        """
        # 기본 응답 구조
        response = {
            "success": True,
            "content": synthesis_results.get('content', ''),
            "references": synthesis_results.get('references', []),
            "agent_name": self.name,
            "metadata": {
                "question_type": search_strategy.get('question_type', 'unknown'),
                "document_categories": search_strategy.get('document_categories', []),
                "total_chunks_retrieved": retrieval_results.get('total_retrieved', 0),
                "search_quality": retrieval_results.get('search_quality', 'unknown'),
                "confidence": synthesis_results.get('confidence', 'unknown'),
                "coverage": synthesis_results.get('coverage', 'unknown'),
                "reranked": retrieval_results.get('reranked', False),
                "durations": durations
            }
        }
        
        return response
    
    def _handle_workflow_failure(self, message: str, error: str, session_id: str) -> Dict:
        """
        워크플로우 실패 처리
        
        에러 발생 시 사용자에게 친화적인 에러 메시지를 반환합니다.
        
        Args:
            message: 원본 사용자 메시지
            error: 에러 메시지
            session_id: 세션 ID
            
        Returns:
            Dict: 에러 응답
        """
        logger.error(f"워크플로우 실패 처리: session={session_id}, error={error}")
        
        # 사용자 친화적인 에러 메시지 생성
        user_message = self._generate_user_friendly_error_message(error)
        
        return {
            "success": False,
            "content": user_message,
            "references": [],
            "agent_name": self.name,
            "error": error,
            "metadata": {
                "error_type": self._classify_error(error),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _generate_user_friendly_error_message(self, error: str) -> str:
        """
        사용자 친화적인 에러 메시지 생성
        
        기술적인 에러 메시지를 사용자가 이해하기 쉬운 메시지로 변환합니다.
        
        Args:
            error: 원본 에러 메시지
            
        Returns:
            str: 사용자 친화적인 에러 메시지
        """
        error_lower = error.lower()
        
        if 'lambda' in error_lower or 'function' in error_lower:
            return """죄송합니다. 검색 도구에 일시적인 문제가 발생했습니다.

잠시 후 다시 시도해주세요. 문제가 계속되면 관리자에게 문의해주세요."""
        
        elif 'timeout' in error_lower:
            return """죄송합니다. 요청 처리 시간이 초과되었습니다.

질문을 더 구체적으로 작성하거나, 잠시 후 다시 시도해주세요."""
        
        elif 'bedrock' in error_lower or 'kb' in error_lower:
            return """죄송합니다. Knowledge Base 검색 중 문제가 발생했습니다.

잠시 후 다시 시도해주세요."""
        
        elif 'invocation_state' in error_lower or 'arn' in error_lower:
            return """죄송합니다. 시스템 설정에 문제가 있습니다.

관리자에게 문의해주세요."""
        
        else:
            return f"""죄송합니다. 요청 처리 중 오류가 발생했습니다.

잠시 후 다시 시도해주세요. 문제가 계속되면 관리자에게 문의해주세요.

오류 정보: {error[:100]}"""
    
    def _classify_error(self, error: str) -> str:
        """
        에러 유형 분류
        
        Args:
            error: 에러 메시지
            
        Returns:
            str: 에러 유형 (lambda_error, timeout, bedrock_error, config_error, unknown)
        """
        error_lower = error.lower()
        
        if 'lambda' in error_lower or 'function' in error_lower:
            return 'lambda_error'
        elif 'timeout' in error_lower:
            return 'timeout'
        elif 'bedrock' in error_lower or 'kb' in error_lower:
            return 'bedrock_error'
        elif 'invocation_state' in error_lower or 'arn' in error_lower:
            return 'config_error'
        else:
            return 'unknown'
    
    def log_interaction(self, message: str, response: Dict, session_id: str):
        """
        상호작용 로깅
        
        워크플로우 실행 정보를 구조화된 형식으로 로깅합니다.
        
        Args:
            message: 사용자 메시지
            response: 에이전트 응답
            session_id: 세션 ID
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "session_id": session_id,
            "message_length": len(message),
            "response_success": response.get("success", False),
            "response_length": len(response.get("content", "")),
            "references_count": len(response.get("references", [])),
            "metadata": response.get("metadata", {})
        }
        
        # 구조화된 로깅
        if response.get("success"):
            logger.info(f"Interaction logged: {json.dumps(log_data)}")
        else:
            logger.error(f"Failed interaction logged: {json.dumps(log_data)}")
    
    def get_capabilities(self) -> List[str]:
        """
        GraphRAG 에이전트 특화 기능
        
        Returns:
            List[str]: 에이전트 기능 목록
        """
        base_capabilities = super().get_capabilities()
        graphrag_capabilities = [
            "지능형 쿼리 분석",
            "다중 문서 추론",
            "관계 기반 검색",
            "그래프 탐색",
            "고급 검색 전략",
            "Reranking 기반 정확도 향상",
            "11개 문서 균형 커버리지"
        ]
        return base_capabilities + graphrag_capabilities
    
    def get_workflow_status(self) -> Dict:
        """
        워크플로우 상태 정보 반환
        
        Returns:
            Dict: 워크플로우 설정 및 상태 정보
        """
        return {
            "agent_name": self.name,
            "display_name": self.display_name,
            "workflow_agents": {
                "query_analysis": {
                    "initialized": hasattr(self, 'query_analysis_agent'),
                    "tools": ["classify_query", "extract_entities"]
                },
                "retrieval": {
                    "initialized": hasattr(self, 'retrieval_agent'),
                    "tools": ["kb_retrieve"]
                },
                "synthesis": {
                    "initialized": hasattr(self, 'synthesis_agent'),
                    "model_id": self.model_id
                }
            },
            "lambda_functions": {
                "classify_query": bool(self.lambda_classify_query_arn),
                "extract_entities": bool(self.lambda_extract_entities_arn),
                "kb_retrieve": bool(self.lambda_kb_retrieve_arn)
            },
            "knowledge_base_id": self.knowledge_base_id,
            "reranker_enabled": bool(self.reranker_model_arn)
        }

    
    # ========================================================================
    # 최종 응답 포맷팅 (UI용)
    # ========================================================================
    
    def _format_final_response(self, synthesis_text: str, retrieval_text: str, message: str, durations: Dict) -> Dict:
        """
        최종 응답을 UI 호환 형식으로 변환
        
        Synthesis Agent의 텍스트 응답과 Retrieval Agent의 텍스트를 파싱하여
        UI가 필요로 하는 구조화된 형식으로 변환합니다.
        
        Args:
            synthesis_text: Synthesis Agent 응답 (한국어 답변 + 메타데이터)
            retrieval_text: Retrieval Agent 응답 (검색 결과)
            message: 원본 사용자 질문
            durations: 각 단계의 소요 시간
            
        Returns:
            Dict: UI 호환 형식의 응답
        """
        import re
        
        # Synthesis 텍스트에서 답변 추출
        content = synthesis_text
        confidence = "medium"
        coverage = "partial"
        
        # 신뢰도 추출
        confidence_match = re.search(r'\*\*신뢰도:\*\*\s*(high|medium|low)', synthesis_text, re.IGNORECASE)
        if confidence_match:
            confidence = confidence_match.group(1).lower()
        
        # 커버리지 추출
        coverage_match = re.search(r'\*\*커버리지:\*\*\s*(complete|partial|limited)', synthesis_text, re.IGNORECASE)
        if coverage_match:
            coverage = coverage_match.group(1).lower()
        
        # Retrieval 텍스트에서 references 추출
        references = self._extract_references_from_retrieval(retrieval_text)
        
        return {
            "success": True,
            "content": content,
            "references": references,
            "agent_name": self.name,
            "metadata": {
                "confidence": confidence,
                "coverage": coverage,
                "durations": durations
            }
        }
    
    def _extract_references_from_retrieval(self, retrieval_text: str) -> List[Dict]:
        """
        Retrieval Agent 텍스트에서 references 추출
        
        Args:
            retrieval_text: Retrieval Agent 응답 텍스트
            
        Returns:
            List[Dict]: ReferenceDisplay 호환 형식의 references
        """
        import re
        
        references = []
        
        # [문서 N] 패턴으로 문서 추출
        doc_pattern = r'\[문서 \d+\] (.+?) \(페이지 (\d+), 점수: ([\d.]+)\)\n(.+?)(?=\n\[문서|\n===|$)'
        matches = re.findall(doc_pattern, retrieval_text, re.DOTALL)
        
        for match in matches:
            doc_name, page, score, text = match
            references.append({
                "source_file": doc_name.strip() + ".pdf",
                "page_number": int(page),
                "ocr_text": text.strip()[:200] + '...',
                "image_uri": f"s3://kb-bucket/{doc_name.strip()}.pdf"
            })
        
        return references
