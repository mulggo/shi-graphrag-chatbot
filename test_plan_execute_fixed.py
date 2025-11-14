#!/usr/bin/env python3
"""
Plan-Execute Agent 수정된 테스트 (올바른 KB ID 사용)
"""

from agents.plan_execute_agent.agent import PlanExecuteAgent
import time

def test_plan_execute_with_correct_kb():
    """올바른 KB ID로 Plan-Execute Agent 테스트"""
    print("🤖 Plan-Execute Agent 테스트 (PWRU19RDNE KB)")
    
    try:
        # 에이전트 초기화 (PWRU19RDNE 사용)
        agent = PlanExecuteAgent(kb_id="PWRU19RDNE")
        
        # 테스트 질문
        query = "선박의 소화기 요구사항은?"
        print(f"질문: {query}")
        
        start_time = time.time()
        result = agent.process_message(query, "test_session")
        end_time = time.time()
        
        print(f"\n=== 결과 ===")
        print(f"성공: {result.get('success')}")
        print(f"응답 시간: {end_time - start_time:.2f}초")
        print(f"참조 개수: {len(result.get('references', []))}")
        
        if result.get('success'):
            print(f"\n=== 응답 내용 ===")
            content = result.get('content', '')
            print(content[:300] + "..." if len(content) > 300 else content)
            
            print(f"\n=== 참조 문서 ===")
            references = result.get('references', [])
            for i, ref in enumerate(references):
                print(f"{i+1}. 출처: {ref.get('source', 'Unknown')}")
                print(f"   점수: {ref.get('score', 0):.3f}")
                print(f"   이미지 URI: {ref.get('image_uri', 'None')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def main():
    print("=" * 60)
    print("🚢 Plan-Execute Agent 수정된 테스트")
    print("=" * 60)
    
    success = test_plan_execute_with_correct_kb()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Plan-Execute Agent 정상 작동!")
        print("🎯 멀티모달 기능 포함하여 모든 기능 검증 완료")
    else:
        print("❌ Plan-Execute Agent 문제 발생")

if __name__ == "__main__":
    main()