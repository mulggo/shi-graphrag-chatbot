#!/usr/bin/env python3
"""
KB 설정 복원: Hierarchical chunking + Lambda transformation
"""
import boto3
import json

def restore_kb_config():
    print("🔧 KB 설정 복원 시작...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        kb_id = "ZGBA1R5CS0"
        
        # Lambda 함수 ARN (기존에 사용하던 것)
        lambda_arn = "arn:aws:lambda:us-west-2:891377311393:function:graphrag-tools"
        
        # 각 데이터 소스 업데이트
        data_sources = [
            {"name": "dnv-ru", "id": "21W9PJ3VJR", "prefix": "documents/dnv-ru/"},
            {"name": "design-guidances", "id": "DUATA0SRUU", "prefix": "documents/design/"},
            {"name": "fss-solas-igc", "id": "HMXCQNXT1V", "prefix": "documents/fss-solas-igc/"},
            {"name": "pipes", "id": "VDXB3NKJ0O", "prefix": "documents/pipes/"}
        ]
        
        for ds in data_sources:
            print(f"\n=== {ds['name']} 업데이트 ===")
            
            # 현재 설정 가져오기
            current = bedrock_agent.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['id']
            )
            
            # 새 설정 구성
            new_config = {
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': 'arn:aws:s3:::shi-kb-bucket',
                    'inclusionPrefixes': [ds['prefix']],
                    'parsingConfiguration': {
                        'parsingStrategy': 'BEDROCK_DATA_AUTOMATION',
                        'bedrockDataAutomationConfiguration': {
                            'transformationConfiguration': {
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
                    }
                },
                'chunkingConfiguration': {
                    'chunkingStrategy': 'HIERARCHICAL',
                    'hierarchicalChunkingConfiguration': {
                        'levelConfigurations': [
                            {
                                'maxTokens': 1500
                            },
                            {
                                'maxTokens': 300
                            }
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
                    dataSourceConfiguration=new_config
                )
                
                print(f"✅ {ds['name']} 설정 업데이트 완료")
                print(f"   - Hierarchical chunking: 1500/300 토큰, 60 오버랩")
                print(f"   - Lambda transformation: {lambda_arn}")
                
            except Exception as e:
                print(f"❌ {ds['name']} 업데이트 실패: {e}")
        
        print(f"\n🔄 모든 데이터 소스 재동기화 시작...")
        
        # 각 데이터 소스 재동기화
        for ds in data_sources:
            try:
                response = bedrock_agent.start_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds['id']
                )
                
                job_id = response['ingestionJob']['ingestionJobId']
                print(f"✅ {ds['name']} 동기화 시작: {job_id}")
                
            except Exception as e:
                print(f"❌ {ds['name']} 동기화 실패: {e}")
        
        print(f"\n⏳ 동기화 완료까지 약 10-15분 소요됩니다.")
        print(f"진행 상황은 AWS 콘솔에서 확인하세요.")
        
        return True
        
    except Exception as e:
        print(f"❌ KB 설정 복원 실패: {e}")
        return False

if __name__ == "__main__":
    success = restore_kb_config()
    exit(0 if success else 1)