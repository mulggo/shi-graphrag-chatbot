#!/usr/bin/env python3
"""
현재 ContextEnrichmentConfiguration 설정 확인
"""
import boto3
import json

def check_context_enrichment():
    print("🔍 ContextEnrichmentConfiguration 설정 확인...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        kb_id = "ZGBA1R5CS0"
        
        # 각 데이터 소스의 현재 설정 확인
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        
        for ds in data_sources['dataSourceSummaries']:
            print(f"\n=== {ds['name']} ===")
            
            # 데이터 소스 상세 정보
            ds_detail = bedrock_agent.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['dataSourceId']
            )
            
            # vectorIngestionConfiguration 확인
            vector_config = ds_detail['dataSource'].get('vectorIngestionConfiguration', {})
            
            print("현재 vectorIngestionConfiguration:")
            print(json.dumps(vector_config, indent=2, default=str))
            
            # contextEnrichmentConfiguration 확인
            if 'contextEnrichmentConfiguration' in vector_config:
                context_config = vector_config['contextEnrichmentConfiguration']
                print(f"\n✅ ContextEnrichmentConfiguration 존재:")
                print(json.dumps(context_config, indent=2, default=str))
            else:
                print(f"\n❌ ContextEnrichmentConfiguration 없음")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 확인 실패: {e}")
        return False

if __name__ == "__main__":
    success = check_context_enrichment()
    exit(0 if success else 1)