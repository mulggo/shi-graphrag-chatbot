"""
GraphRAG Agent vs Base Bedrock Agent 비교 테스트
동일한 질문에 대한 두 에이전트의 응답을 비교
"""
import os
import sys
from dotenv import load_dotenv
import time
import boto3

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_manager import AgentConfig
from agents.graphrag_agent.agent import Agent as GraphRAGAgent

def test_compare_agents():
    """두 에이전트 비교 테스트"""
    
    print("=" * 80)
    print("에이전트 비교 테스트: GraphRAG vs Firefighting")
    print("=" * 80)
    
    # 테스트 질문
    question = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
    session_id = "compare-test-session"
    
    print(f"\n질문: {question}\n")
    
    # 1. Firefighting Agent (기존 Bedrock Agent 기반)
    print("=" * 80)
    print("[1] Firefighting Agent (Bedrock Agent 기반)")
    print("=" * 80)
    
    try:
        ff_config = AgentConfig(
            name="firefighting",
            display_name="소방 규정 검색",
            description="선박 소방 규정 전문 에이전트",
            module_path="agents.firefighting_agent.agent",
            bedrock_agent_id=os.getenv("BEDROCK_AGENT_ID", "H5YNZKKNSW"),
            bedrock_alias_id=os.getenv("BEDROCK_AGENT_ALIAS_ID", "FD3LV7TEN4"),
            bedrock_model_id="",
            knowledge_base_id=os.getenv("KNOWLEDGE_BASE_ID", "ZGBA1R5CS0")
        )
        
        ff_agent = FirefightingAgent(ff_config)
        print("✓ Agent 초기화 성공")
        
        start_time = time.time()
        ff_result = ff_agent.process_message(question, session_id + "-ff")
        ff_duration = time.time() - start_time
        
        if ff_result.get('success'):
            content = ff_result.get('content', '')
            print(f"\n답변 길이: {len(content)}자")
            print(f"실행 시간: {ff_duration:.2f}초")
            print(f"참조 문서 수: {len(ff_result.get('references', []))}개")
            print(f"\n답변 (처음 300자):")
            print("-" * 80)
            print(content[:300] + "..." if len(content) > 300 else content)
            print("-" * 80)
        else:
            print(f"\n✗ 실패: {ff_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n✗ Firefighting Agent 실행 실패: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")
    
    # 2. GraphRAG Agent (멀티 에이전트 워크플로우)
    print("=" * 80)
    print("[2] GraphRAG Agent (멀티 에이전트 워크플로우)")
    print("=" * 80)
    
    try:
        gr_config = AgentConfig(
            name="graphrag",
            display_name="GraphRAG 검색",
            description="GraphRAG 기반 고급 검색 에이전트",
            module_path="agents.graphrag_agent.agent",
            bedrock_agent_id="",
            bedrock_alias_id="",
            bedrock_model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
            knowledge_base_id=os.getenv("KNOWLEDGE_BASE_ID", "ZGBA1R5CS0"),
            lambda_function_names={
                "extract_entities": os.getenv("LAMBDA_EXTRACT_ENTITIES_ARN", ""),
                "kb_retrieve": os.getenv("LAMBDA_KB_RETRIEVE_ARN", "")
            },
            reranker_model_arn=os.getenv("RERANKER_MODEL_ARN", "")
        )
        
        gr_agent = GraphRAGAgent(gr_config)
        print("✓ Agent 초기화 성공")
        
        status = gr_agent.get_workflow_status()
        print(f"✓ Query Analysis Agent: {status['workflow_agents']['query_analysis']['initialized']}")
        print(f"✓ Retrieval Agent: {status['workflow_agents']['retrieval']['initialized']}")
        print(f"✓ Synthesis Agent: {status['workflow_agents']['synthesis']['initialized']}")
        
        start_time = time.time()
        gr_result = gr_agent.process_message(question, session_id + "-gr")
        gr_duration = time.time() - start_time
        
        if gr_result.get('success'):
            content = gr_result.get('content', '')
            print(f"\n답변 길이: {len(content)}자")
            print(f"실행 시간: {gr_duration:.2f}초")
            print(f"참조 문서 수: {len(gr_result.get('references', []))}개")
            
            metadata = gr_result.get('metadata', {})
            durations = metadata.get('durations', {})
            print(f"\n워크플로우 단계별 시간:")
            print(f"  - Query Analysis: {durations.get('query_analysis', 0):.2f}초")
            print(f"  - Retrieval: {durations.get('retrieval', 0):.2f}초")
            print(f"  - Synthesis: {durations.get('synthesis', 0):.2f}초")
            
            print(f"\n답변 (처음 300자):")
            print("-" * 80)
            print(content[:300] + "..." if len(content) > 300 else content)
            print("-" * 80)
            
            print(f"\n신뢰도: {metadata.get('confidence', 'N/A')}")
            print(f"커버리지: {metadata.get('coverage', 'N/A')}")
        else:
            print(f"\n✗ 실패: {gr_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n✗ GraphRAG Agent 실행 실패: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("비교 테스트 완료")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_compare_agents()
    sys.exit(0 if success else 1)
