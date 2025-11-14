#!/usr/bin/env python3
"""
이미지 URI 확인 테스트
"""

import boto3
import json

def test_image_uri():
    """PWRU19RDNE에서 이미지 URI 확인"""
    bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    response = bedrock_client.retrieve(
        knowledgeBaseId='PWRU19RDNE',
        retrievalQuery={'text': 'fire extinguisher'},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 3
            }
        }
    )
    
    for i, result in enumerate(response['retrievalResults']):
        print(f"\n=== 결과 {i+1} ===")
        metadata = result.get('metadata', {})
        
        print("모든 메타데이터 키:")
        for key in metadata.keys():
            print(f"  - {key}")
        
        # 이미지 관련 필드들 확인
        image_uri = metadata.get('x-amz-bedrock-kb-byte-content-source', '')
        print(f"이미지 URI: {image_uri}")
        
        if image_uri:
            print("✅ 이미지 URI 발견!")
        else:
            print("❌ 이미지 URI 없음")

if __name__ == "__main__":
    test_image_uri()