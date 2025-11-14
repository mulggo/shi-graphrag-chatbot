#!/usr/bin/env python3
"""
다른 KB로 Plan-Execute Agent 테스트
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def test_different_kb():
    print("🔍 다른 KB로 Plan-Execute Agent 테스트...")
    
    # 테스트할 KB들
    kbs = [
        {"id": "VCWJQ37BZH", "name": "bda-os"},
        {"id": "PWRU19RDNE", "name": "claude-neptune"},
        {"id": "CDPB5AI6BH", "name": "bda-neptune-2"},
        {"id": "ZRYWIRPOFK", "name": "mcp"}
    ]
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        for kb in kbs:
            print(f"\n=== {kb['name']} ({kb['id']}) 테스트 ===")
            
            # KB ID 변경하여 테스트
            agent = PlanExecuteAgent()
            
            # 간단한 검색 테스트
            result = agent._execute_neptune_search("fire extinguisher", kb['id'])
            print(f"검색 결과: {len(result)}개")
            
            if result:
                print(f"첫 번째 결과 점수: {result[0].get('score', 0):.3f}")
                print(f"첫 번째 내용: {result[0].get('content', '')[:100]}...")
            
            # 다양한 검색어로 테스트
            test_queries = ["SOLAS", "fire safety", "piping", "소화기"]
            
            for query in test_queries:
                try:
                    search_result = agent._execute_neptune_search(query, kb['id'])
                    print(f"  '{query}': {len(search_result)}개")
                except Exception as e:
                    print(f"  '{query}': 실패 - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_different_kb()
    exit(0 if success else 1)