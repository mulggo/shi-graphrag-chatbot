#!/usr/bin/env python3
"""
PWRU19RDNE KB 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.plan_execute_agent.agent import PlanExecuteAgent
import time

def test_pwru_kb():
    """PWRU19RDNE KB로 테스트"""
    print("🧪 PWRU19RDNE KB 테스트")
    print("=" * 50)
    
    agent = PlanExecuteAgent()
    query = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
    
    print(f"📝 테스트 질문: {query}")
    print("-" * 50)
    
    # 검색 테스트
    english_query = "SOLAS fire protection requirements for ships"
    search_results = agent._execute_neptune_search(english_query)
    print(f"🔍 검색 결과: {len(search_results)}개")
    
    if search_results:
        for i, result in enumerate(search_results[:3], 1):
            print(f"  {i}. 출처: {result.get('source', 'Unknown')}")
            print(f"     점수: {result.get('score', 0):.3f}")
            print(f"     내용: {result.get('content', '')[:100]}...")
            print()
    
    # 전체 워크플로우 테스트
    print("🚀 전체 워크플로우 테스트")
    print("-" * 30)
    
    start_time = time.time()
    result = agent.process_message(query, "test_session")
    end_time = time.time()
    
    print(f"성공: {result.get('success')}")
    print(f"시간: {end_time - start_time:.2f}초")
    print(f"응답: {result.get('content', '')}")
    print(f"참조: {len(result.get('references', []))}개")

if __name__ == "__main__":
    test_pwru_kb()