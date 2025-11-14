#!/usr/bin/env python3
"""
KB 설정 복원: 새로운 임시 처리 버킷 사용
"""
import boto3

def restore_kb_with_temp_bucket():
    print("🔧 KB 설정 복원 (새 임시 버킷 사용)...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        kb_id = "ZGBA1R5CS0"
        
        # bda-processor Lambda ARN
        lambda_arn = "arn:aws:lambda:us-west-2:697805350841:function:bda-processor"
        
        # 새로운 임시 처리 버킷
        temp_bucket = "s3://shi-kb-temp-processing/"
        
        # 각 데이터 소스 설정
        data_sources = [
            {"name": "dnv-ru", "id": "21W9PJ3VJR", "prefix": "documents/dnv-ru/"},
            {"name": "design-guidances", "id": "DUATA0SRUU", "prefix": "documents/design/"},
            {"name": "fss-solas-igc", "id": "HMXCQNXT1V", "prefix": "documents/fss-solas-igc/"},
            {"name": "pipes", "id": "VDXB3NKJ0O", "prefix": "documents/pipes/"}
        ]
        
        for ds in data_sources:
            print(f"\n=== {ds['name']} 업데이트 ===")
            
            # S3 설정
            data_source_config = {
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': 'arn:aws:s3:::shi-kb-bucket',
                    'inclusionPrefixes': [ds['prefix']]
                }
            }
            
            # vectorIngestionConfiguration
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
                },
                'customTransformationConfiguration': {
                    'intermediateStorage': {
                        's3Location': {
                            'uri': temp_bucket
                        }
                    },
                    'transformations': [
                        {
                            'stepToApply': 'POST_CHUNKING',
                            'transformationFunction': {
                                'transformationLambdaConfiguration': {
                                    'lambdaArn': lambda_arn
                                }
                            }
                        }
                    ]
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
                
                print(f"✅ {ds['name']} 설정 업데이트 완료")
                print(f"   - Hierarchical chunking: 1500/300 토큰, 60 오버랩")
                print(f"   - bda-processor Lambda: POST_CHUNKING")
                print(f"   - 임시 저장소: {temp_bucket}")
                
            except Exception as e:
                print(f"❌ {ds['name']} 업데이트 실패: {e}")
        
        print(f"\n✅ KB 설정 복원 완료!")
        print(f"🔄 이제 데이터 소스를 재동기화하세요")
        
        return True
        
    except Exception as e:
        print(f"❌ KB 설정 복원 실패: {e}")
        return False

if __name__ == "__main__":
    success = restore_kb_with_temp_bucket()
    exit(0 if success else 1)