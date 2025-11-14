#!/usr/bin/env python3
"""
ZGBA1R5CS0 KB 내용 디버깅
다양한 검색어로 KB 내용 확인
"""

import boto3
import json

def test_kb_with_various_queries():
    """다양한 검색어로 KB 테스트"""
    client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    kb_id = "ZGBA1R5CS0"
    
    # 다양한 검색어 테스트
    test_queries = [
        # 영어 검색어
        "fire extinguisher",
        "fire safety",
        "SOLAS",
        "ship",
        "safety",
        "fire",
        "extinguisher",
        "detection",
        "system",
        
        # 한국어 검색어  
        "소화기",
        "화재",
        "안전",
        "선박",
        "시스템",
        
        # 일반적인 단어
        "the",
        "and",
        "requirements",
        "regulations"
    ]
    
    print(f"🔍 KB ID: {kb_id} 내용 탐색")
    print("=" * 60)
    
    results_found = 0
    
    for query in test_queries:
        try:
            response = client.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 3
                    }
                }
            )
            
            result_count = len(response['retrievalResults'])
            results_found += result_count
            
            print(f"📝 '{query}': {result_count}개 결과")
            
            # 결과가 있으면 첫 번째 결과 미리보기
            if result_count > 0:
                first_result = response['retrievalResults'][0]
                content = first_result.get('content', {}).get('text', '')
                source = first_result.get('metadata', {}).get('x-amz-bedrock-kb-source-uri', '')
                score = first_result.get('score', 0)
                
                print(f"   ✅ 첫 번째 결과:")
                print(f"      점수: {score:.3f}")
                print(f"      출처: {source.split('/')[-1] if source else 'Unknown'}")
                print(f"      내용: {content[:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ '{query}' 검색 실패: {e}")
    
    print("=" * 60)
    print(f"📊 총 검색 결과: {results_found}개")
    
    if results_found == 0:
        print("⚠️  KB가 완전히 비어있거나 접근 권한 문제일 수 있습니다.")
        
        # KB 정보 확인
        try:
            bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
            kb_info = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
            print(f"\n📋 KB 정보:")
            print(f"   이름: {kb_info['knowledgeBase']['name']}")
            print(f"   상태: {kb_info['knowledgeBase']['status']}")
            print(f"   생성일: {kb_info['knowledgeBase']['createdAt']}")
            
        except Exception as e:
            print(f"❌ KB 정보 조회 실패: {e}")
    
    return results_found > 0

if __name__ == "__main__":
    test_kb_with_various_queries()