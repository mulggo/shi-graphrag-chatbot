#!/usr/bin/env python3
"""
KB 선택 기능 테스트
3개의 KB로 동일한 질문을 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.plan_execute_agent.agent import PlanExecuteAgent
import time

def test_kb_selection():
    """3개 KB로 동일한 질문 테스트"""
    
    kbs = {
        "🔥 PWRU19RDNE (최적)": "PWRU19RDNE",
        "📚 CDPB5AI6BH (풍부)": "CDPB5AI6BH", 
        "⚠️ ZGBA1R5CS0 (제한적)": "ZGBA1R5CS0"
    }
    
    query = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
    
    print("🧪 KB 선택 기능 테스트")
    print("=" * 60)
    print(f"📝 테스트 질문: {query}")
    print("=" * 60)
    
    results = {}
    
    for kb_name, kb_id in kbs.items():
        print(f"\n{kb_name} ({kb_id}) 테스트")
        print("-" * 40)
        
        try:
            # KB ID로 에이전트 생성
            agent = PlanExecuteAgent(kb_id=kb_id)
            
            start_time = time.time()
            result = agent.process_message(query, "test_session")
            end_time = time.time()
            
            results[kb_name] = {
                "success": result.get('success'),
                "response_time": end_time - start_time,
                "content_length": len(result.get('content', '')),
                "references_count": len(result.get('references', [])),
                "content": result.get('content', '')[:100] + "..."
            }
            
            print(f"✅ 성공: {result.get('success')}")
            print(f"⏱️ 시간: {end_time - start_time:.2f}초")
            print(f"📝 응답 길이: {len(result.get('content', ''))}자")
            print(f"📚 참조 수: {len(result.get('references', []))}개")
            print(f"💬 응답 미리보기: {result.get('content', '')[:100]}...")
            
        except Exception as e:
            print(f"❌ 오류: {e}")
            results[kb_name] = {"error": str(e)}
    
    # 결과 비교
    print("\n" + "=" * 60)
    print("📊 KB 성능 비교")
    print("=" * 60)
    
    print(f"{'KB 이름':<20} {'성공':<6} {'시간':<8} {'응답길이':<8} {'참조수':<6}")
    print("-" * 60)
    
    for kb_name, result in results.items():
        if 'error' not in result:
            success = "✅" if result['success'] else "❌"
            time_str = f"{result['response_time']:.1f}s"
            length_str = f"{result['content_length']}자"
            refs_str = f"{result['references_count']}개"
            
            print(f"{kb_name:<20} {success:<6} {time_str:<8} {length_str:<8} {refs_str:<6}")
        else:
            print(f"{kb_name:<20} ❌     오류     -        -      -")

if __name__ == "__main__":
    test_kb_selection()