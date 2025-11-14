#!/usr/bin/env python3
"""
2.1 문서 계획 수립 테스트
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def test_document_planning():
    print("🔍 2.1 문서 계획 수립 테스트 시작...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # 문서 계획 수립 테스트
        plan = agent._create_document_plan("선박의 소화기 요구사항은?")
        
        print(f"✅ 문서 계획 수립 성공")
        print(f"   - 성공 여부: {plan.get('success')}")
        print(f"   - 선택된 문서: {plan.get('target_documents', [])}")
        print(f"   - 영어 쿼리: {plan.get('english_query', '')}")
        print(f"   - 선택 이유: {plan.get('reasoning', '')[:100]}...")
        
        # 성공 기준 확인
        if plan.get('success') and plan.get('target_documents') and plan.get('english_query'):
            print("✅ 모든 성공 기준 충족")
            return True
        else:
            print("⚠️ 일부 성공 기준 미충족")
            return False
        
    except Exception as e:
        print(f"❌ 문서 계획 수립 실패: {e}")
        print(f"   에러 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_document_planning()
    exit(0 if success else 1)