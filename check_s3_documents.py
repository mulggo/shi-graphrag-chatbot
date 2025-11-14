#!/usr/bin/env python3
"""
S3 버킷의 실제 문서 확인
"""
import boto3

def check_s3_documents():
    print("🔍 S3 버킷 문서 확인...")
    
    try:
        s3 = boto3.client('s3')
        bucket_name = 'shi-kb-bucket'
        
        # 각 데이터 소스 경로별 문서 확인
        prefixes = [
            'documents/dnv-ru/',
            'documents/design/', 
            'documents/fss-solas-igc/',
            'documents/pipes/'
        ]
        
        total_files = 0
        
        for prefix in prefixes:
            print(f"\n=== {prefix} ===")
            
            try:
                response = s3.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    MaxKeys=20
                )
                
                if 'Contents' in response:
                    files = response['Contents']
                    print(f"파일 수: {len(files)}개")
                    total_files += len(files)
                    
                    for i, obj in enumerate(files[:5], 1):
                        size_mb = obj['Size'] / (1024 * 1024)
                        print(f"{i}. {obj['Key']} ({size_mb:.2f}MB)")
                        
                    if len(files) > 5:
                        print(f"... 외 {len(files) - 5}개 파일")
                else:
                    print("파일 없음")
                    
            except Exception as e:
                print(f"경로 확인 실패: {e}")
        
        print(f"\n총 파일 수: {total_files}개")
        
        # 최근 동기화 상태 확인
        print("\n=== 최근 동기화 상태 ===")
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId='ZGBA1R5CS0')
        
        for ds in data_sources['dataSourceSummaries']:
            # 최근 동기화 작업 확인
            try:
                ingestion_jobs = bedrock_agent.list_ingestion_jobs(
                    knowledgeBaseId='ZGBA1R5CS0',
                    dataSourceId=ds['dataSourceId'],
                    maxResults=3
                )
                
                print(f"\n{ds['name']} 동기화 작업:")
                for job in ingestion_jobs['ingestionJobSummaries']:
                    print(f"  - {job['status']}: {job['startedAt']} ({job.get('statistics', {}).get('numberOfDocumentsScanned', 0)}개 문서)")
                    
            except Exception as e:
                print(f"{ds['name']} 동기화 작업 확인 실패: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ S3 문서 확인 실패: {e}")
        return False

if __name__ == "__main__":
    success = check_s3_documents()
    exit(0 if success else 1)