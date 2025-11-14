#!/usr/bin/env python3
"""
Neptune KB의 S3 데이터 소스 확인
"""
import boto3
import json

def check_kb_s3_sources():
    print("🔍 Neptune KB S3 데이터 소스 확인...")
    
    try:
        # Bedrock Agent 클라이언트
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        # KB 데이터 소스 목록 조회
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId='ZGBA1R5CS0')
        
        print(f"📁 데이터 소스 개수: {len(data_sources['dataSourceSummaries'])}")
        
        s3_client = boto3.client('s3', region_name='us-west-2')
        
        for i, ds_summary in enumerate(data_sources['dataSourceSummaries']):
            print(f"\n=== 데이터 소스 {i+1}: {ds_summary['name']} ===")
            print(f"상태: {ds_summary['status']}")
            
            # 상세 정보 조회
            ds_detail = bedrock_agent.get_data_source(
                knowledgeBaseId='ZGBA1R5CS0',
                dataSourceId=ds_summary['dataSourceId']
            )
            
            # S3 설정 확인
            s3_config = ds_detail['dataSource']['dataSourceConfiguration']['s3Configuration']
            bucket_arn = s3_config['bucketArn']
            bucket_name = bucket_arn.split(':')[-1]
            
            print(f"S3 버킷: {bucket_name}")
            
            # 포함 접두사 확인
            inclusion_prefixes = s3_config.get('inclusionPrefixes', [])
            if inclusion_prefixes:
                print(f"포함 접두사: {inclusion_prefixes}")
            
            # S3 버킷 내용 확인
            try:
                print(f"\n📂 S3 버킷 '{bucket_name}' 내용:")
                
                # 접두사가 있으면 해당 접두사로 검색
                if inclusion_prefixes:
                    for prefix in inclusion_prefixes:
                        print(f"\n  📁 접두사: {prefix}")
                        response = s3_client.list_objects_v2(
                            Bucket=bucket_name,
                            Prefix=prefix,
                            MaxKeys=50
                        )
                        
                        if 'Contents' in response:
                            for obj in response['Contents'][:20]:  # 상위 20개만
                                file_name = obj['Key']
                                file_size = obj['Size']
                                print(f"    📄 {file_name} ({file_size:,} bytes)")
                        else:
                            print(f"    (접두사 '{prefix}'에 파일 없음)")
                else:
                    # 접두사 없으면 전체 버킷 확인
                    response = s3_client.list_objects_v2(
                        Bucket=bucket_name,
                        MaxKeys=50
                    )
                    
                    if 'Contents' in response:
                        for obj in response['Contents'][:20]:  # 상위 20개만
                            file_name = obj['Key']
                            file_size = obj['Size']
                            print(f"  📄 {file_name} ({file_size:,} bytes)")
                    else:
                        print("  (버킷에 파일 없음)")
                        
            except Exception as e:
                print(f"  ❌ S3 버킷 접근 실패: {e}")
        
    except Exception as e:
        print(f"❌ KB 데이터 소스 확인 실패: {e}")

if __name__ == "__main__":
    check_kb_s3_sources()