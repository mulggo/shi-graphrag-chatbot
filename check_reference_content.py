#!/usr/bin/env python3
"""
참조 문서의 실제 내용 확인
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def check_reference_content():
    print("🔍 참조 문서 실제 내용 확인...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        
        # KB ID 변경
        original_method = agent._execute_neptune_search
        def temp_search(query, kb_id="CDPB5AI6BH"):
            return original_method(query, kb_id)
        agent._execute_neptune_search = temp_search
        
        # 검색 결과 확인
        query = "fire extinguisher requirements ships"
        search_results = agent._execute_neptune_search(query)
        
        print(f"검색 결과: {len(search_results)}개")
        
        for i, result in enumerate(search_results[:3], 1):
            print(f"\n=== 참조 문서 {i} ===")
            print(f"점수: {result.get('score', 0):.3f}")
            print(f"소스: {result.get('source', 'Unknown')}")
            print(f"내용 (전체):")
            print(result.get('content', '')[:500] + "..." if len(result.get('content', '')) > 500 else result.get('content', ''))
        
        # 실제 응답 생성 과정 확인
        print(f"\n=== 응답 생성 과정 ===")
        
        # 1. 문서 계획
        plan = agent._create_document_plan("선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘")
        print(f"계획된 영어 쿼리: {plan.get('english_query', '')}")
        
        # 2. 검색 실행
        search_results = agent._execute_neptune_search(plan.get('english_query', ''))
        print(f"검색된 문서 수: {len(search_results)}")
        
        # 3. Reranking
        reranked = agent._cohere_rerank(plan.get('english_query', ''), search_results)
        print(f"Reranked 문서 수: {len(reranked)}")
        
        # 4. 실제 사용된 컨텍스트 확인
        if reranked:
            print(f"\n=== 실제 사용된 컨텍스트 ===")
            for i, doc in enumerate(reranked[:3], 1):
                print(f"문서 {i}: {doc['content'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 확인 실패: {e}")
        return False

if __name__ == "__main__":
    success = check_reference_content()
    exit(0 if success else 1)