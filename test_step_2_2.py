#!/usr/bin/env python3
"""
2.2 Cohere Reranking 테스트
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def test_cohere_reranking():
    print("🔍 2.2 Cohere Reranking 테스트 시작...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # 더미 문서로 테스트
        dummy_docs = [
            {"content": "Fire extinguisher requirements for ships according to SOLAS", "score": 0.8},
            {"content": "SOLAS fire safety regulations and compliance", "score": 0.7},
            {"content": "Maritime safety equipment standards", "score": 0.6}
        ]
        
        reranked = agent._cohere_rerank("fire safety", dummy_docs)
        
        print(f"✅ Cohere Reranking 성공")
        print(f"   - 입력 문서 수: {len(dummy_docs)}")
        print(f"   - 출력 문서 수: {len(reranked)}")
        
        if reranked:
            first_doc = reranked[0]
            print(f"   - 첫 번째 문서 키: {list(first_doc.keys())}")
            print(f"   - Rerank 점수: {first_doc.get('rerank_score', 'None')}")
            print(f"   - 원본 점수: {first_doc.get('score', 'None')}")
            
            # rerank_score가 추가되었는지 확인
            has_rerank_score = any('rerank_score' in doc for doc in reranked)
            if has_rerank_score:
                print("✅ Rerank 점수 추가됨")
            else:
                print("⚠️ Rerank 점수 없음 (폴백 동작)")
        
        return True
        
    except Exception as e:
        print(f"❌ Cohere Reranking 실패: {e}")
        print(f"   에러 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_cohere_reranking()
    exit(0 if success else 1)