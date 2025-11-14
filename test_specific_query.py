#!/usr/bin/env python3
"""
특정 질문으로 Plan-Execute Agent 테스트
질문: "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.plan_execute_agent.agent import PlanExecuteAgent
import time

def test_specific_query():
    """특정 질문으로 전체 워크플로우 테스트"""
    print("🧪 Plan-Execute Agent 특정 질문 테스트")
    print("KB ID: ZGBA1R5CS0")
    print("=" * 60)
    
    query = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
    print(f"📝 테스트 질문: {query}")
    print("=" * 60)
    
    try:
        agent = PlanExecuteAgent()
        
        # 1단계: 문서 계획 수립 확인
        print("\n🎯 1단계: 문서 계획 수립")
        print("-" * 40)
        
        plan = agent._create_document_plan(query)
        if plan.get('success'):
            print("✅ 계획 수립 성공")
            print(f"  - 선택된 문서 수: {len(plan.get('target_documents', []))}")
            print(f"  - 영어 검색 쿼리: {plan.get('english_query', '')}")
            print("  - 선택된 문서들:")
            for i, doc in enumerate(plan.get('target_documents', []), 1):
                print(f"    {i}. {doc}")
        else:
            print(f"❌ 계획 수립 실패: {plan.get('error', 'Unknown')}")
            return False
        
        # 2단계: Neptune KB 검색 확인
        print(f"\n🔍 2단계: Neptune KB 검색")
        print("-" * 40)
        
        english_query = plan.get('english_query', query)
        print(f"검색 쿼리: {english_query}")
        
        search_results = agent._execute_neptune_search(english_query)
        print(f"✅ 검색 완료: {len(search_results)}개 결과")
        
        if search_results:
            print("상위 3개 결과:")
            for i, result in enumerate(search_results[:3], 1):
                print(f"  {i}. 출처: {result.get('source', 'Unknown')}")
                print(f"     점수: {result.get('score', 0):.3f}")
                print(f"     내용: {result.get('content', '')[:100]}...")
                print()
        else:
            print("⚠️  검색 결과 없음")
        
        # 3단계: 전체 워크플로우 실행
        print(f"\n🚀 3단계: 전체 워크플로우 실행")
        print("-" * 40)
        
        start_time = time.time()
        result = agent.process_message(query, "test_session")
        end_time = time.time()
        
        print(f"📊 실행 결과:")
        print(f"  - 성공 여부: {result.get('success')}")
        print(f"  - 실행 시간: {end_time - start_time:.2f}초")
        print(f"  - 응답 길이: {len(result.get('content', ''))}자")
        print(f"  - 참조 문서 수: {len(result.get('references', []))}")
        
        if result.get('success'):
            print(f"\n📄 생성된 응답:")
            print("-" * 40)
            content = result.get('content', '')
            print(content)
            
            references = result.get('references', [])
            if references:
                print(f"\n📚 참조 문서 ({len(references)}개):")
                print("-" * 40)
                for i, ref in enumerate(references, 1):
                    print(f"{i}. 출처: {ref.get('source', 'Unknown')}")
                    print(f"   점수: {ref.get('score', 0):.3f}")
                    print(f"   내용: {ref.get('content', '')[:150]}...")
                    print()
            else:
                print("\n📚 참조 문서: 없음")
        else:
            print(f"\n❌ 워크플로우 실패:")
            print(f"   오류: {result.get('content', '')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_specific_query()
    
    print("\n" + "=" * 60)
    print("📋 최종 결과")
    print("=" * 60)
    
    if success:
        print("🎉 테스트 성공! Plan-Execute Agent가 정상 작동합니다.")
    else:
        print("❌ 테스트 실패. 로그를 확인하세요.")

if __name__ == "__main__":
    main()