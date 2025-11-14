#!/usr/bin/env python3
"""
텍스트-이미지 매핑 정확성 검증
"""

import boto3
import json

def verify_text_image_mapping():
    """검색된 텍스트와 이미지가 실제로 매칭되는지 확인"""
    bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    s3_client = boto3.client('s3', region_name='us-west-2')
    
    # 1. 검색 실행
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
    content = result.get('content', {}).get('text', '')
    metadata = result.get('metadata', {})
    
    print("=== 검색된 텍스트 ===")
    print(content[:200] + "...")
    print(f"\n페이지: {metadata.get('x-amz-bedrock-kb-document-page-number')}")
    print(f"소스: {metadata.get('x-amz-bedrock-kb-source-uri')}")
    
    # 2. S3에서 이미지들 가져오기
    data_source_id = metadata.get('x-amz-bedrock-kb-data-source-id', '')
    if data_source_id:
        prefix = f"aws/bedrock/knowledge_bases/PWRU19RDNE/{data_source_id}/"
        
        try:
            s3_response = s3_client.list_objects_v2(
                Bucket='claude-neptune',
                Prefix=prefix,
                MaxKeys=5
            )
            
            print(f"\n=== S3 이미지 샘플 ===")
            for obj in s3_response.get('Contents', [])[:3]:
                key = obj['Key']
                if key.lower().endswith('.png'):
                    print(f"이미지: {key}")
                    
                    # 이미지 메타데이터만 확인
                    try:
                        img_response = s3_client.head_object(Bucket='claude-neptune', Key=key)
                        print(f"  용량: {img_response['ContentLength']} bytes")
                        print(f"  수정일: {img_response['LastModified']}")
                        
                    except Exception as e:
                        print(f"  메타데이터 확인 실패: {e}")
            
            # 3. 매핑 검증 결론
            print(f"\n=== 매핑 검증 결과 ===")
            print("❓ 텍스트와 이미지의 정확한 매핑 여부:")
            print("  - Knowledge Base에서 직접적인 매핑 정보 없음")
            print("  - 이미지 파일명이 UUID로 되어있어 연결고리 불분명")
            print("  - 페이지 번호 기반 매핑도 불가능")
            print("\n💡 결론: 정확한 매핑 보장 어려움")
            
        except Exception as e:
            print(f"S3 접근 실패: {e}")

if __name__ == "__main__":
    verify_text_image_mapping()