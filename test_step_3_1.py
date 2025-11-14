#!/usr/bin/env python3
"""
3.1 전체 프로세스 테스트
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def test_full_process():
    print("🔍 3.1 전체 프로세스 테스트 시작...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # KB ID 임시 변경
        original_method = agent._execute_neptune_search
        def temp_search(query, kb_id="CDPB5AI6BH"):
            return original_method(query, kb_id)
        agent._execute_neptune_search = temp_search
        
        # 실제 질문으로 전체 워크플로우 테스트
        query = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
        result = agent.process_message(query, "test_session")
        
        print(f"✅ 전체 프로세스 완료")
        print(f"   - 성공 여부: {result.get('success')}")
        print(f"   - 응답 길이: {len(result.get('content', ''))} 문자")
        print(f"   - 참조 개수: {len(result.get('references', []))}개")
        print(f"   - 응답 시간: {result.get('response_time', 0):.2f}초")
        print(f"   - 에이전트 타입: {result.get('agent_type')}")
        
        # 응답 내용 미리보기
        content = result.get('content', '')
        if content:
            print(f"\n=== 응답 미리보기 ===")
            print(content[:300] + "..." if len(content) > 300 else content)
        
        # 참조 문서 미리보기
        references = result.get('references', [])
        if references:
            print(f"\n=== 참조 문서 미리보기 ===")
            for i, ref in enumerate(references[:2]):
                print(f"{i+1}. 출처: {ref.get('source', 'Unknown')}")
                print(f"   점수: {ref.get('score', 0):.3f}")
                print(f"   내용: {ref.get('content', '')[:100]}...")
        
        # 성공 기준 확인
        success_criteria = [
            result.get('success') == True,
            len(result.get('content', '')) > 0,
            result.get('response_time', 0) < 30  # 30초 이내
        ]
        
        if all(success_criteria):
            print("\n✅ 모든 성공 기준 충족")
            return True
        else:
            print("\n⚠️ 일부 성공 기준 미충족")
            return False
        
    except Exception as e:
        print(f"❌ 전체 프로세스 실패: {e}")
        print(f"   에러 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_full_process()
    exit(0 if success else 1)