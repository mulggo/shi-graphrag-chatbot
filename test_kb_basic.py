"""
기본 KB ID 변경 테스트 - Firefighting Agent 사용
"""
import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("KB ID 변경 테스트 - Firefighting Agent")
print("=" * 80)

# 1. 환경 변수 확인
print("\n[1단계] 환경 변수 확인...")
kb_id = os.getenv("KNOWLEDGE_BASE_ID")
agent_id = os.getenv("BEDROCK_AGENT_ID")
alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID")

print(f"✓ KB ID: {kb_id}")
print(f"✓ Agent ID: {agent_id}")
print(f"✓ Alias ID: {alias_id}")

# 2. 모듈 import 테스트
print("\n[2단계] 모듈 import 테스트...")
try:
    from core.agent_manager import AgentConfig
    print("✓ AgentConfig import 성공")
    
    from agents.firefighting_agent.agent import Agent
    print("✓ Firefighting Agent import 성공")
except Exception as e:
    print(f"✗ Import 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Agent 설정 생성
print("\n[3단계] Agent 설정 생성...")
try:
    config = AgentConfig(
        name="firefighting",
        display_name="선박 소방 규정",
        description="테스트",
        module_path="agents.firefighting_agent.agent",
        bedrock_agent_id=agent_id,
        bedrock_alias_id=alias_id,
        knowledge_base_id=kb_id
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
    print(f"✓ KB ID: {agent.knowledge_base_id}")
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
    print("\n에이전트 실행 중...")
    import time
    start_time = time.time()
    
    result = agent.process_message(question, session_id="test-session")
    
    duration = time.time() - start_time
    
    print(f"\n✓ 성공 여부: {result.get('success', False)}")
    print(f"✓ 실행 시간: {duration:.2f}초")
    
    if result.get('success'):
        content = result.get('content', '')
        print(f"\n답변 길이: {len(content)}자")
        print(f"참조 문서 수: {len(result.get('references', []))}개")
        
        print(f"\n답변 (처음 300자):")
        print("-" * 80)
        print(content[:300] + "..." if len(content) > 300 else content)
        print("-" * 80)
        
        print("\n" + "=" * 80)
        print("✓ KB ID 변경 테스트 성공!")
        print(f"✓ 새로운 KB ID ({kb_id})로 정상 동작 확인")
        print("=" * 80)
    else:
        error = result.get('error', 'Unknown error')
        print(f"\n✗ 실패: {error}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ 에이전트 실행 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)