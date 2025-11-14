#!/usr/bin/env python3
"""
Neptune KB 검색 디버깅 - 다양한 키워드로 테스트
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def debug_neptune_search():
    print("🔍 Neptune KB 검색 디버깅...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # 다양한 키워드로 검색 테스트
        test_queries = [
            "fire",
            "safety", 
            "SOLAS",
            "FSS",
            "DNV",
            "design",
            "piping",
            "hull",
            "penetration",
            "support"
        ]
        
        for query in test_queries:
            print(f"\n📝 검색어: '{query}'")
            results = agent._execute_neptune_search(query)
            print(f"   결과 수: {len(results)}")
            
            if results:
                for i, result in enumerate(results[:2]):
                    source = result.get('source', 'Unknown')
                    score = result.get('score', 0)
                    content = result.get('content', '')[:100] + "..."
                    print(f"   [{i+1}] {source} (점수: {score:.3f})")
                    print(f"       {content}")
                break  # 첫 번째 성공한 검색에서 중단
        
        # 가장 성공적인 검색어로 Cohere 테스트
        if results:
            print(f"\n🔄 '{query}' 결과로 Cohere Reranking 테스트...")
            reranked = agent._cohere_rerank(query, results)
            
            print(f"✅ 실제 문서로 Reranking 완료")
            print(f"   - 입력: {len(results)}개, 출력: {len(reranked)}개")
            
            for i, doc in enumerate(reranked[:2]):
                rerank_score = doc.get('rerank_score', 'None')
                original_score = doc.get('score', 'None')
                print(f"   [{i+1}] Rerank: {rerank_score}, Original: {original_score}")
        
    except Exception as e:
        print(f"❌ 디버깅 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_neptune_search()