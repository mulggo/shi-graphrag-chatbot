#!/usr/bin/env python3
"""
두 KB 비교 테스트
CDPB5AI6BH vs ZGBA1R5CS0
"""

import boto3
import json

def test_kb_comparison():
    """두 KB를 동일한 쿼리로 비교"""
    client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    kbs = {
        "이전 KB": "CDPB5AI6BH",
        "현재 KB": "ZGBA1R5CS0"
    }
    
    test_queries = [
        "fire extinguisher",
        "SOLAS fire safety",
        "ship fire protection",
        "소화기",
        "화재 안전"
    ]
    
    print("🔍 KB 비교 테스트")
    print("=" * 60)
    
    for kb_name, kb_id in kbs.items():
        print(f"\n📋 {kb_name} ({kb_id})")
        print("-" * 40)
        
        total_results = 0
        
        for query in test_queries:
            try:
                response = client.retrieve(
                    knowledgeBaseId=kb_id,
                    retrievalQuery={'text': query},
                    retrievalConfiguration={
                        'vectorSearchConfiguration': {
                            'numberOfResults': 5
                        }
                    }
                )
                
                result_count = len(response['retrievalResults'])
                total_results += result_count
                
                print(f"  '{query}': {result_count}개")
                
                # 첫 번째 결과 미리보기
                if result_count > 0:
                    first = response['retrievalResults'][0]
                    source = first.get('metadata', {}).get('x-amz-bedrock-kb-source-uri', '').split('/')[-1]
                    score = first.get('score', 0)
                    content = first.get('content', {}).get('text', '')
                    
                    print(f"    → 최고점수: {score:.3f}, 출처: {source}")
                    print(f"    → 내용: {content[:80]}...")
                
            except Exception as e:
                print(f"  '{query}': 오류 - {e}")
        
        print(f"\n📊 총 결과: {total_results}개")
        
        # KB 정보 확인
        try:
            bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
            kb_info = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
            
            print(f"📋 KB 정보:")
            print(f"  이름: {kb_info['knowledgeBase']['name']}")
            print(f"  상태: {kb_info['knowledgeBase']['status']}")
            print(f"  생성일: {kb_info['knowledgeBase']['createdAt']}")
            
        except Exception as e:
            print(f"❌ KB 정보 조회 실패: {e}")

def test_specific_query_both_kbs():
    """특정 쿼리로 두 KB 비교"""
    print("\n" + "=" * 60)
    print("🎯 특정 쿼리 비교 테스트")
    print("=" * 60)
    
    client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    query = "SOLAS chapter II-2 fire protection and detection requirements for ships"
    
    kbs = {
        "이전 KB": "CDPB5AI6BH", 
        "현재 KB": "ZGBA1R5CS0"
    }
    
    print(f"🔍 테스트 쿼리: {query}")
    print()
    
    for kb_name, kb_id in kbs.items():
        print(f"📋 {kb_name} ({kb_id})")
        print("-" * 40)
        
        try:
            response = client.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5
                    }
                }
            )
            
            results = response['retrievalResults']
            print(f"✅ 검색 결과: {len(results)}개")
            
            for i, result in enumerate(results[:3], 1):
                source = result.get('metadata', {}).get('x-amz-bedrock-kb-source-uri', '').split('/')[-1]
                score = result.get('score', 0)
                content = result.get('content', {}).get('text', '')
                
                print(f"  {i}. 점수: {score:.3f}")
                print(f"     출처: {source}")
                print(f"     내용: {content[:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
        
        print()

if __name__ == "__main__":
    test_kb_comparison()
    test_specific_query_both_kbs()