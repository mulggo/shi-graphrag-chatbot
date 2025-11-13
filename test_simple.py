"""
간단한 GraphRAG Agent 테스트
"""
import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("GraphRAG Agent 간단 테스트")
print("=" * 80)

# 1. 모듈 import 테스트
print("\n[1단계] 모듈 import 테스트...")
try:
    from core.agent_manager import AgentConfig
    print("✓ AgentConfig import 성공")
    
    from agents.graphrag_agent.agent import Agent
    print("✓ GraphRAG Agent import 성공")
except Exception as e:
    print(f"✗ Import 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 환경 변수 확인
print("\n[2단계] 환경 변수 확인...")
kb_id = os.getenv("KNOWLEDGE_BASE_ID")
extract_arn = os.getenv("LAMBDA_EXTRACT_ENTITIES_ARN")
retrieve_arn = os.getenv("LAMBDA_KB_RETRIEVE_ARN")

print(f"✓ KB ID: {kb_id}")
print(f"✓ Extract Entities ARN: {extract_arn[:60]}..." if extract_arn else "✗ Extract Entities ARN 없음")
print(f"✓ KB Retrieve ARN: {retrieve_arn[:60]}..." if retrieve_arn else "✗ KB Retrieve ARN 없음")

# 3. Agent 설정 생성
print("\n[3단계] Agent 설정 생성...")
try:
    config = AgentConfig(
        name="graphrag",
        display_name="GraphRAG 검색",
        description="테스트",
        module_path="agents.graphrag_agent.agent",
        bedrock_agent_id="",
        bedrock_alias_id="",
        bedrock_model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        knowledge_base_id=kb_id,
        lambda_function_names={
            "extract_entities": extract_arn,
            "kb_retrieve": retrieve_arn
        },
        reranker_model_arn=os.getenv("RERANKER_MODEL_ARN", "")
    )
    print("✓ 설정 생성 성공")
except Exception as e:
    print(f"✗ 설정 생성 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Agent 초기화
print("\n[4단계] Agent 초기화...")
try:
    agent = Agent(config)
    print("✓ Agent 초기화 성공")
    
    status = agent.get_workflow_status()
    print(f"✓ Query Analysis Agent: {status['workflow_agents']['query_analysis']['initialized']}")
    print(f"✓ Retrieval Agent: {status['workflow_agents']['retrieval']['initialized']}")
    print(f"✓ Synthesis Agent: {status['workflow_agents']['synthesis']['initialized']}")
except Exception as e:
    print(f"✗ Agent 초기화 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 간단한 질문 테스트
print("\n[5단계] 질문 처리 테스트...")
question = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
print(f"질문: {question}")

try:
    print("\n워크플로우 실행 중...")
    result = agent.process_message(question, session_id="test-session")
    
    print(f"\n✓ 성공 여부: {result.get('success', False)}")
    
    if result.get('success'):
        content = result.get('content', '')
        print(f"\n답변 (처음 300자):")
        print("-" * 80)
        print(content[:300] + "..." if len(content) > 300 else content)
        print("-" * 80)
        
        references = result.get('references', [])
        print(f"\n✓ 참조 문서 수: {len(references)}개")
        
        metadata = result.get('metadata', {})
        durations = metadata.get('durations', {})
        print(f"\n✓ 실행 시간:")
        print(f"  - Query Analysis: {durations.get('query_analysis', 0):.2f}초")
        print(f"  - Retrieval: {durations.get('retrieval', 0):.2f}초")
        print(f"  - Synthesis: {durations.get('synthesis', 0):.2f}초")
        print(f"  - 전체: {durations.get('total', 0):.2f}초")
        
        print("\n" + "=" * 80)
        print("✓ 테스트 성공!")
        print("=" * 80)
    else:
        error = result.get('error', 'Unknown error')
        print(f"\n✗ 실패: {error}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ 워크플로우 실행 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
