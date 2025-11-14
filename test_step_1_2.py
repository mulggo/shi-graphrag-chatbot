#!/usr/bin/env python3
"""
1.2 Neptune KB 연결 테스트
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def test_neptune_kb_connection():
    print("🔍 1.2 Neptune KB 연결 테스트 시작...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # 간단한 검색 테스트
        result = agent._execute_neptune_search("fire extinguisher", "CDPB5AI6BH")
        
        print(f"✅ Neptune KB 검색 성공")
        print(f"   - 검색 결과 개수: {len(result)}")
        
        if result:
            first_result = result[0]
            print(f"   - 첫 번째 결과 키: {list(first_result.keys())}")
            print(f"   - 첫 번째 내용: {first_result.get('content', '')[:100]}...")
        else:
            print("   - 검색 결과 없음 (정상 - 빈 결과)")
            
        return True
        
    except Exception as e:
        print(f"❌ Neptune KB 연결 실패: {e}")
        print(f"   에러 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_neptune_kb_connection()
    exit(0 if success else 1)