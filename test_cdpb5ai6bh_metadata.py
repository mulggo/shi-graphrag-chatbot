#!/usr/bin/env python3
"""
CDPB5AI6BH KB 메타데이터 확인
"""

import boto3
import json

def check_cdpb5ai6bh_metadata():
    """CDPB5AI6BH KB의 메타데이터 구조 확인"""
    bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    try:
        response = bedrock_client.retrieve(
            knowledgeBaseId='CDPB5AI6BH',
            retrievalQuery={'text': 'fire'},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 1
                }
            }
        )
        
        result = response['retrievalResults'][0]
        metadata = result.get('metadata', {})
        
        print("=== CDPB5AI6BH KB 메타데이터 ===")
        for key, value in metadata.items():
            print(f"{key}: {str(value)[:100]}...")
        
        # OCR 관련 필드 찾기
        ocr_fields = []
        for key in metadata.keys():
            if 'ocr' in key.lower() or 'description' in key.lower() or 'text' in key.lower():
                ocr_fields.append(key)
        
        print(f"\n=== OCR 관련 필드 ===")
        for field in ocr_fields:
            print(f"- {field}")
        
        return metadata
        
    except Exception as e:
        print(f"CDPB5AI6BH 접근 실패: {e}")
        return {}

if __name__ == "__main__":
    check_cdpb5ai6bh_metadata()