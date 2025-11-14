#!/usr/bin/env python3
"""
응답 합성 과정 디버깅
검색 결과는 있는데 왜 "관련 문서를 찾지 못했습니다"가 나오는지 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.plan_execute_agent.agent import PlanExecuteAgent
import json

def debug_synthesis_process():
    """응답 합성 과정을 단계별로 디버깅"""
    print("🔍 응답 합성 과정 디버깅")
    print("=" * 50)
    
    agent = PlanExecuteAgent()
    query = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
    
    # 1단계: 검색 결과 확인
    print("1️⃣ 검색 결과 확인")
    print("-" * 30)
    
    english_query = "SOLAS chapter II-2 fire protection and detection requirements for ships, FSS code fire safety systems for ships"
    search_results = agent._execute_neptune_search(english_query)
    
    print(f"검색 결과 수: {len(search_results)}")
    print(f"검색 결과가 비어있는가? {not search_results}")
    
    if search_results:
        print("\n검색 결과 상세:")
        for i, result in enumerate(search_results):
            print(f"  결과 {i+1}:")
            print(f"    content 길이: {len(result.get('content', ''))}")
            print(f"    content 내용: {result.get('content', '')[:100]}...")
            print(f"    source: {result.get('source', '')}")
            print(f"    score: {result.get('score', 0)}")
            print()
    
    # 2단계: Cohere Reranking 확인
    print("2️⃣ Cohere Reranking 확인")
    print("-" * 30)
    
    if search_results:
        reranked = agent._cohere_rerank(query, search_results)
        print(f"Reranking 후 결과 수: {len(reranked)}")
        
        if reranked:
            print("Reranking 결과:")
            for i, result in enumerate(reranked):
                print(f"  결과 {i+1}:")
                print(f"    rerank_score: {result.get('rerank_score', 'None')}")
                print(f"    original_score: {result.get('score', 0)}")
                print(f"    content 길이: {len(result.get('content', ''))}")
                print()
    
    # 3단계: 전체 합성 과정 확인
    print("3️⃣ 전체 합성 과정 확인")
    print("-" * 30)
    
    synthesis_result = agent._synthesize_response(query, search_results)
    
    print(f"합성 결과:")
    print(f"  text 길이: {len(synthesis_result.get('text', ''))}")
    print(f"  text 내용: {synthesis_result.get('text', '')}")
    print(f"  references 수: {len(synthesis_result.get('references', []))}")
    
    # 4단계: 조건 확인
    print("\n4️⃣ 조건 확인")
    print("-" * 30)
    
    print(f"search_results가 비어있는가? {not search_results}")
    print(f"if not documents 조건: {not search_results}")
    
    if search_results:
        print("검색 결과가 있으므로 정상적으로 처리되어야 함")
    else:
        print("검색 결과가 없어서 '관련 문서를 찾지 못했습니다' 반환")

def test_manual_synthesis():
    """수동으로 합성 과정 테스트"""
    print("\n" + "=" * 50)
    print("🧪 수동 합성 테스트")
    print("=" * 50)
    
    # 더미 문서로 테스트
    dummy_docs = [
        {
            'content': 'SOLAS Chapter II-2 requires ships to have fire extinguishers, fire detection systems, and sprinkler systems for fire safety.',
            'source': 'SOLAS_Chapter_II-2.pdf',
            'score': 0.8
        },
        {
            'content': 'FSS Code specifies the requirements for fire safety systems including portable fire extinguishers and fixed fire fighting systems.',
            'source': 'FSS_Code.pdf', 
            'score': 0.7
        }
    ]
    
    agent = PlanExecuteAgent()
    query = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
    
    print(f"더미 문서 수: {len(dummy_docs)}")
    print("더미 문서로 합성 테스트...")
    
    result = agent._synthesize_response(query, dummy_docs)
    
    print(f"\n결과:")
    print(f"  text: {result.get('text', '')}")
    print(f"  references 수: {len(result.get('references', []))}")

if __name__ == "__main__":
    debug_synthesis_process()
    test_manual_synthesis()