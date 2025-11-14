#!/usr/bin/env python3
"""
검색 결과와 정확히 매칭되는 이미지 찾기
"""

import boto3
import json

def find_exact_image():
    """검색 결과의 정확한 이미지 매칭 방법 찾기"""
    bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    s3_client = boto3.client('s3', region_name='us-west-2')
    
    # 검색 실행
    response = bedrock_client.retrieve(
        knowledgeBaseId='PWRU19RDNE',
        retrievalQuery={'text': 'fire extinguisher'},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 1
            }
        }
    )
    
    result = response['retrievalResults'][0]
    metadata = result.get('metadata', {})
    content = result.get('content', {}).get('text', '')
    
    print("=== 검색 결과 분석 ===")
    print(f"내용: {content[:100]}...")
    print(f"소스 URI: {metadata.get('x-amz-bedrock-kb-source-uri', '')}")
    print(f"페이지: {metadata.get('x-amz-bedrock-kb-document-page-number', '')}")
    print(f"데이터 소스: {metadata.get('x-amz-bedrock-kb-data-source-id', '')}")
    
    # S3에서 해당 문서의 이미지들 확인
    data_source_id = metadata.get('x-amz-bedrock-kb-data-source-id', '')
    page_number = metadata.get('x-amz-bedrock-kb-document-page-number', '')
    
    if data_source_id:
        prefix = f"aws/bedrock/knowledge_bases/PWRU19RDNE/{data_source_id}/"
        
        print(f"\n=== S3 이미지 검색 ===")
        print(f"검색 경로: s3://claude-neptune/{prefix}")
        
        try:
            s3_response = s3_client.list_objects_v2(
                Bucket='claude-neptune',
                Prefix=prefix,
                MaxKeys=20
            )
            
            images = []
            for obj in s3_response.get('Contents', []):
                key = obj['Key']
                if key.lower().endswith('.png'):
                    # 파일명에서 패턴 분석
                    filename = key.split('/')[-1]
                    print(f"이미지: {filename}")
                    
                    # 페이지 번호나 문서 ID로 매칭 시도
                    if page_number and str(page_number) in filename:
                        print(f"  ✅ 페이지 {page_number} 매칭!")
                    
                    images.append(key)
            
            print(f"\n총 {len(images)}개 이미지 발견")
            
            # 매칭 전략 제안
            print("\n=== 매칭 전략 ===")
            print("1. 파일명의 UUID와 검색 결과 연결")
            print("2. 페이지 번호 기반 매칭")
            print("3. 문서 청크 순서 기반 매칭")
            
        except Exception as e:
            print(f"S3 검색 실패: {e}")

if __name__ == "__main__":
    find_exact_image()