#!/usr/bin/env python3
"""
상세 검색 테스트 - 다양한 검색어와 설정으로 테스트
"""
import boto3
import json

def test_detailed_search():
    print("🔍 상세 검색 테스트...")
    
    try:
        bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        kb_id = "ZGBA1R5CS0"
        
        # 다양한 검색어 테스트
        test_queries = [
            # 영어 키워드
            "fire extinguisher",
            "fire safety", 
            "SOLAS",
            "DNV",
            "FSS",
            "IGC",
            "design guidance",
            "piping",
            "hull penetration",
            "support system",
            
            # 한국어 키워드  
            "소화기",
            "화재 안전",
            "설계 가이드",
            "배관",
            
            # 구체적 내용
            "portable extinguisher",
            "fire detection",
            "insulation penetration",
            "spoolcutting"
        ]
        
        successful_queries = []
        
        for query in test_queries:
            try:
                response = bedrock_runtime.retrieve(
                    knowledgeBaseId="CDPB5AI6BH",
                    retrievalQuery={'text': query},
                    retrievalConfiguration={
                        'vectorSearchConfiguration': {
                            'numberOfResults': 10
                        }
                    }
                )
                
                results = response['retrievalResults']
                
                if results:
                    print(f"✅ '{query}': {len(results)}개 결과")
                    successful_queries.append((query, len(results)))
                    
                    # 첫 번째 결과 상세 정보
                    first = results[0]
                    print(f"   점수: {first.get('score', 0):.3f}")
                    print(f"   내용: {first.get('content', {}).get('text', '')[:100]}...")
                    
                    # 메타데이터 확인
                    metadata = first.get('metadata', {})
                    if metadata:
                        print(f"   메타데이터: {list(metadata.keys())}")
                        for key, value in metadata.items():
                            if key != 'source':
                                print(f"     {key}: {str(value)[:50]}...")
                else:
                    print(f"❌ '{query}': 결과 없음")
                    
            except Exception as e:
                print(f"❌ '{query}': 검색 실패 - {e}")
        
        print(f"\n=== 요약 ===")
        print(f"성공한 검색어: {len(successful_queries)}개")
        
        if successful_queries:
            print("성공한 검색어들:")
            for query, count in successful_queries:
                print(f"  - '{query}': {count}개")
        
        # 가장 많은 결과를 반환한 검색어로 상세 분석
        if successful_queries:
            best_query = max(successful_queries, key=lambda x: x[1])
            print(f"\n=== 최고 성능 검색어: '{best_query[0]}' ===")
            
            response = bedrock_runtime.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': best_query[0]},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 10
                    }
                }
            )
            
            for i, result in enumerate(response['retrievalResults'], 1):
                print(f"{i}. 점수: {result.get('score', 0):.3f}")
                print(f"   내용: {result.get('content', {}).get('text', '')[:150]}...")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ 상세 검색 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_detailed_search()
    exit(0 if success else 1)