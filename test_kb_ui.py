#!/usr/bin/env python3
"""
KB 선택 UI 기능 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.plan_execute_agent.agent import PlanExecuteAgent
from core.agent_manager import AgentManager

def test_kb_functionality():
    """KB 선택 기능 테스트"""
    print("🧪 KB 선택 기능 테스트")
    print("=" * 50)
    
    # Agent Manager 테스트
    print("1️⃣ Agent Manager 초기화")
    try:
        agent_manager = AgentManager()
        print("✅ Agent Manager 초기화 성공")
        
        available_agents = agent_manager.get_available_agents()
        print(f"✅ 사용 가능한 에이전트: {len(available_agents)}개")
        
        for agent in available_agents:
            print(f"   - {agent.name}: {agent.display_name}")
    except Exception as e:
        print(f"❌ Agent Manager 오류: {e}")
        return False
    
    # Plan-Execute Agent 직접 테스트
    print("\n2️⃣ Plan-Execute Agent KB 테스트")
    
    kbs = ["PWRU19RDNE", "CDPB5AI6BH", "ZGBA1R5CS0"]
    query = "선박 소화기 요구사항"
    
    for kb_id in kbs:
        print(f"\n📋 KB: {kb_id}")
        try:
            agent = PlanExecuteAgent(kb_id=kb_id)
            result = agent._execute_neptune_search("fire extinguisher")
            print(f"   검색 결과: {len(result)}개")
            
            if result:
                print(f"   첫 번째 결과: {result[0].get('source', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    # Agent Manager를 통한 라우팅 테스트
    print("\n3️⃣ Agent Manager 라우팅 테스트")
    
    try:
        # Plan-Execute Agent가 있는지 확인
        plan_agent = agent_manager.get_agent('plan_execute')
        if plan_agent:
            print("✅ Plan-Execute Agent 발견")
            
            # KB ID를 변경하며 테스트
            for kb_id in ["PWRU19RDNE", "CDPB5AI6BH"]:
                print(f"\n📋 KB {kb_id}로 테스트")
                result = agent_manager.route_message(
                    'plan_execute', 
                    query, 
                    'test_session',
                    kb_id=kb_id
                )
                print(f"   성공: {result.get('success')}")
                print(f"   응답 길이: {len(result.get('content', ''))}")
        else:
            print("❌ Plan-Execute Agent 없음")
    except Exception as e:
        print(f"❌ 라우팅 테스트 오류: {e}")

if __name__ == "__main__":
    test_kb_functionality()