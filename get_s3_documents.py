#!/usr/bin/env python3
"""S3 버킷에서 실제 문서 목록 가져오기"""
import boto3
import json

def get_kb_documents():
    """Knowledge Base의 S3 데이터 소스에서 문서 목록 가져오기"""
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
    kb_id = 'ZGBA1R5CS0'
    
    try:
        # Data Sources 조회
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        
        for ds in data_sources['dataSourceSummaries']:
            print(f"\n데이터 소스: {ds['name']}")
            print(f"상태: {ds['status']}")
            
            # 데이터 소스 상세 정보
            ds_detail = bedrock_agent.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['dataSourceId']
            )
            
            # S3 설정 확인
            s3_config = ds_detail['dataSource']['dataSourceConfiguration']['s3Configuration']
            bucket_arn = s3_config['bucketArn']
            bucket_name = bucket_arn.split(':::')[-1]
            
            print(f"S3 버킷: {bucket_name}")
            
            # S3에서 파일 목록 가져오기
            s3_client = boto3.client('s3', region_name='us-west-2')
            
            # 버킷의 모든 객체 나열
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' in response:
                print(f"\n총 {len(response['Contents'])}개 파일:")
                for obj in response['Contents']:
                    file_name = obj['Key']
                    size_mb = obj['Size'] / (1024 * 1024)
                    print(f"  - {file_name} ({size_mb:.2f} MB)")
            else:
                print("파일이 없습니다.")
                
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_kb_documents()
