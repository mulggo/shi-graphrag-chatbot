#!/usr/bin/env python3
"""
Neptune KB에 실제로 있는 문서들 확인
"""
import boto3
import json

def check_neptune_kb_documents():
    print("🔍 Neptune KB 문서 목록 확인...")
    
    try:
        # Bedrock Agent 클라이언트로 KB 정보 조회
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        # KB 기본 정보
        kb_info = bedrock_agent.get_knowledge_base(knowledgeBaseId='ZGBA1R5CS0')
        print(f"✅ KB 이름: {kb_info['knowledgeBase']['name']}")
        print(f"✅ KB 상태: {kb_info['knowledgeBase']['status']}")
        
        # 데이터 소스 확인
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId='ZGBA1R5CS0')
        print(f"\n📁 데이터 소스 개수: {len(data_sources['dataSourceSummaries'])}")
        
        for i, ds in enumerate(data_sources['dataSourceSummaries']):
            print(f"  {i+1}. {ds['name']} (상태: {ds['status']})")
        
        # 실제 검색으로 문서 샘플 확인
        bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        # 다양한 키워드로 검색해서 실제 문서 확인
        test_queries = ["fire", "safety", "ship", "regulation", "SOLAS"]
        
        all_sources = set()
        
        for query in test_queries:
            try:
                response = bedrock_runtime.retrieve(
                    knowledgeBaseId='ZGBA1R5CS0',
                    retrievalQuery={'text': query},
                    retrievalConfiguration={
                        'vectorSearchConfiguration': {
                            'numberOfResults': 20
                        }
                    }
                )
                
                for result in response['retrievalResults']:
                    source = result.get('metadata', {}).get('source', 'Unknown')
                    if source and source != 'Unknown':
                        all_sources.add(source)
                        
            except Exception as e:
                print(f"  ⚠️ '{query}' 검색 실패: {e}")
        
        print(f"\n📚 실제 문서 소스 ({len(all_sources)}개):")
        for i, source in enumerate(sorted(all_sources), 1):
            print(f"  {i}. {source}")
            
        return sorted(all_sources)
        
    except Exception as e:
        print(f"❌ Neptune KB 확인 실패: {e}")
        return []

if __name__ == "__main__":
    documents = check_neptune_kb_documents()