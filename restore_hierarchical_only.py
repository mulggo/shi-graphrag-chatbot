#!/usr/bin/env python3
"""
Hierarchical chunking만 먼저 적용
"""
import boto3

def restore_hierarchical_chunking():
    print("🔧 Hierarchical chunking 설정...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        kb_id = "ZGBA1R5CS0"
        
        # 각 데이터 소스 설정
        data_sources = [
            {"name": "dnv-ru", "id": "21W9PJ3VJR", "prefix": "documents/dnv-ru/"},
            {"name": "design-guidances", "id": "DUATA0SRUU", "prefix": "documents/design/"},
            {"name": "fss-solas-igc", "id": "HMXCQNXT1V", "prefix": "documents/fss-solas-igc/"},
            {"name": "pipes", "id": "VDXB3NKJ0O", "prefix": "documents/pipes/"}
        ]
        
        for ds in data_sources:
            print(f"\n=== {ds['name']} 업데이트 ===")
            
            # 기본 S3 설정
            data_source_config = {
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': 'arn:aws:s3:::shi-kb-bucket',
                    'inclusionPrefixes': [ds['prefix']]
                }
            }
            
            # Hierarchical chunking만 설정
            vector_ingestion_config = {
                'chunkingConfiguration': {
                    'chunkingStrategy': 'HIERARCHICAL',
                    'hierarchicalChunkingConfiguration': {
                        'levelConfigurations': [
                            {'maxTokens': 1500},
                            {'maxTokens': 300}
                        ],
                        'overlapTokens': 60
                    }
                }
            }
            
            try:
                # 데이터 소스 업데이트
                response = bedrock_agent.update_data_source(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds['id'],
                    name=ds['name'],
                    dataSourceConfiguration=data_source_config,
                    vectorIngestionConfiguration=vector_ingestion_config
                )
                
                print(f"✅ {ds['name']} Hierarchical chunking 설정 완료")
                print(f"   - 레벨 1: 1500 토큰")
                print(f"   - 레벨 2: 300 토큰")
                print(f"   - 오버랩: 60 토큰")
                
            except Exception as e:
                print(f"❌ {ds['name']} 업데이트 실패: {e}")
        
        print(f"\n✅ Hierarchical chunking 설정 완료!")
        print(f"📝 다음 단계: Lambda transformation 별도 설정 필요")
        
        return True
        
    except Exception as e:
        print(f"❌ Hierarchical chunking 설정 실패: {e}")
        return False

if __name__ == "__main__":
    success = restore_hierarchical_chunking()
    exit(0 if success else 1)