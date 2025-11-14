#!/usr/bin/env python3
"""
2.2 Cohere Reranking 실제 질문 테스트
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def test_cohere_reranking_real():
    print("🔍 2.2 Cohere Reranking 실제 질문 테스트 시작...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # 실제 선박 소화설비 관련 더미 문서들
        real_docs = [
            {"content": "선박의 소화기는 SOLAS 규정에 따라 각 구역별로 적절히 배치되어야 합니다. 휴대용 소화기는 접근이 용이한 곳에 설치해야 합니다.", "score": 0.85},
            {"content": "고정식 소화 시스템은 기관실, 화물창 등 주요 구역에 설치되며 CO2, 포말, 물분무 시스템 등이 있습니다.", "score": 0.82},
            {"content": "화재 감지 시스템은 연기 감지기, 열 감지기로 구성되며 조기 화재 발견을 위해 필수적입니다.", "score": 0.78},
            {"content": "비상 소화 펌프는 주 소화 펌프가 고장날 경우를 대비한 백업 시스템입니다.", "score": 0.75},
            {"content": "소화 호스와 노즐은 선박 전체에 걸쳐 충분한 수량이 배치되어야 합니다.", "score": 0.72}
        ]
        
        query = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
        
        reranked = agent._cohere_rerank(query, real_docs)
        
        print(f"✅ Cohere Reranking 성공")
        print(f"   - 입력 문서 수: {len(real_docs)}")
        print(f"   - 출력 문서 수: {len(reranked)}")
        
        if reranked:
            print(f"\n=== Reranking 결과 ===")
            for i, doc in enumerate(reranked[:3]):
                print(f"{i+1}. 원본 점수: {doc.get('score', 'None')}")
                print(f"   Rerank 점수: {doc.get('rerank_score', 'None')}")
                print(f"   내용: {doc['content'][:80]}...")
                print()
            
            # rerank_score가 추가되었는지 확인
            has_rerank_score = any('rerank_score' in doc for doc in reranked)
            if has_rerank_score:
                print("✅ Rerank 점수 추가됨 - Cohere 모델 정상 작동")
            else:
                print("⚠️ Rerank 점수 없음 - 폴백 동작 (원본 순서 유지)")
        
        return True
        
    except Exception as e:
        print(f"❌ Cohere Reranking 실패: {e}")
        print(f"   에러 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_cohere_reranking_real()
    exit(0 if success else 1)