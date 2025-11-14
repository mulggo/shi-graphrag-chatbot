#!/usr/bin/env python3
"""
3.2 한국어 응답 품질 확인
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def test_korean_response_quality():
    print("🔍 3.2 한국어 응답 품질 확인 시작...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # 다양한 질문으로 테스트
        test_queries = [
            "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘",
            "SOLAS 화재 감지 시스템 규정은?",
            "선박 소화기 배치 기준"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n=== 테스트 {i}: {query} ===")
            
            result = agent.process_message(query, f"test_session_{i}")
            response_text = result.get('content', '')
            
            print(f"성공 여부: {result.get('success')}")
            print(f"응답 길이: {len(response_text)} 문자")
            print(f"응답 시간: {result.get('response_time', 0):.2f}초")
            
            # 한국어 응답 확인
            print("=== 응답 내용 ===")
            if len(response_text) > 200:
                print(response_text[:200] + "...")
            else:
                print(response_text)
            
            # 참조 문서 확인
            references = result.get('references', [])
            print(f"\n=== 참조 문서 ({len(references)}개) ===")
            for j, ref in enumerate(references[:2]):
                print(f"{j+1}. 출처: {ref.get('source', 'Unknown')}")
                print(f"   점수: {ref.get('score', 0):.3f}")
                print(f"   내용: {ref.get('content', '')[:80]}...")
            
            if not references:
                print("참조 문서 없음")
        
        print("\n✅ 한국어 응답 품질 확인 완료")
        return True
        
    except Exception as e:
        print(f"❌ 한국어 응답 품질 확인 실패: {e}")
        print(f"   에러 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_korean_response_quality()
    exit(0 if success else 1)