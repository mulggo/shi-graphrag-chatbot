#!/usr/bin/env python3
"""
KB ID 변경 후 Plan-Execute Agent 테스트
ZGBA1R5CS0 KB로 변경 후 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.plan_execute_agent.agent import PlanExecuteAgent
import time

def test_kb_connection():
    """1단계: KB 연결 테스트"""
    print("🔍 1단계: KB 연결 테스트 (ZGBA1R5CS0)")
    print("=" * 50)
    
    try:
        agent = PlanExecuteAgent()
        print("✅ AWS 클라이언트 초기화 성공")
        
        # KB 검색 테스트
        print("\n🔍 Neptune KB 검색 테스트...")
        results = agent._execute_neptune_search("fire extinguisher")
        print(f"✅ 검색 완료: {len(results)}개 결과")
        
        if results:
            print(f"첫 번째 결과 미리보기:")
            print(f"  - 출처: {results[0].get('source', 'Unknown')}")
            print(f"  - 점수: {results[0].get('score', 0):.3f}")
            print(f"  - 내용: {results[0].get('content', '')[:100]}...")
        else:
            print("⚠️  검색 결과 없음 (KB가 비어있거나 쿼리 불일치)")
            
        return True
        
    except Exception as e:
        print(f"❌ KB 연결 실패: {e}")
        return False

def test_document_planning():
    """2단계: 문서 계획 수립 테스트"""
    print("\n🎯 2단계: 문서 계획 수립 테스트")
    print("=" * 50)
    
    try:
        agent = PlanExecuteAgent()
        
        test_queries = [
            "선박의 소화기 요구사항은?",
            "SOLAS 화재 감지 시스템 규정",
            "스프링클러 시스템 설치 기준"
        ]
        
        for query in test_queries:
            print(f"\n📝 테스트 쿼리: {query}")
            plan = agent._create_document_plan(query)
            
            if plan.get('success'):
                print(f"✅ 계획 수립 성공")
                print(f"  - 선택 문서: {len(plan.get('target_documents', []))}개")
                print(f"  - 영어 쿼리: {plan.get('english_query', '')}")
                if plan.get('target_documents'):
                    print(f"  - 첫 번째 문서: {plan['target_documents'][0]}")
            else:
                print(f"❌ 계획 수립 실패: {plan.get('error', 'Unknown')}")
                
        return True
        
    except Exception as e:
        print(f"❌ 문서 계획 테스트 실패: {e}")
        return False

def test_full_workflow():
    """3단계: 전체 워크플로우 테스트"""
    print("\n🚀 3단계: 전체 워크플로우 테스트")
    print("=" * 50)
    
    try:
        agent = PlanExecuteAgent()
        
        test_query = "선박의 소화기 요구사항은?"
        print(f"📝 테스트 쿼리: {test_query}")
        
        start_time = time.time()
        result = agent.process_message(test_query, "test_session")
        end_time = time.time()
        
        print(f"\n📊 결과 분석:")
        print(f"  - 성공 여부: {result.get('success')}")
        print(f"  - 응답 시간: {end_time - start_time:.2f}초")
        print(f"  - 응답 길이: {len(result.get('content', ''))}자")
        print(f"  - 참조 개수: {len(result.get('references', []))}")
        
        if result.get('success'):
            print(f"\n📄 응답 미리보기:")
            content = result.get('content', '')
            print(f"{content[:200]}...")
            
            print(f"\n📚 참조 문서:")
            for i, ref in enumerate(result.get('references', [])[:2]):
                print(f"  {i+1}. {ref.get('source', 'Unknown')} (점수: {ref.get('score', 0):.3f})")
                print(f"     {ref.get('content', '')[:80]}...")
        else:
            print(f"❌ 전체 워크플로우 실패: {result.get('content', '')}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ 전체 워크플로우 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🧪 Plan-Execute Agent KB 변경 테스트")
    print("KB ID: ZGBA1R5CS0")
    print("=" * 60)
    
    # 단계별 테스트 실행
    tests = [
        ("KB 연결", test_kb_connection),
        ("문서 계획", test_document_planning), 
        ("전체 워크플로우", test_full_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 최종 결과 요약
    print("\n" + "=" * 60)
    print("📋 테스트 결과 요약")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name:15} : {status}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n총 {len(results)}개 테스트 중 {success_count}개 성공")
    
    if success_count == len(results):
        print("🎉 모든 테스트 통과! KB 변경 성공!")
    else:
        print("⚠️  일부 테스트 실패. 로그를 확인하세요.")

if __name__ == "__main__":
    main()