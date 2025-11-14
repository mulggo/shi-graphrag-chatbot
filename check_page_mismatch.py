#!/usr/bin/env python3
"""
CDPB5AI6BH KB의 페이지 번호 불일치 확인
"""

import boto3
import json

def check_cdpb5ai6bh_pages():
    """CDPB5AI6BH KB의 페이지 번호와 실제 내용 확인"""
    
    bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    # CDPB5AI6BH KB에서 검색
    response = bedrock_client.retrieve(
        knowledgeBaseId='CDPB5AI6BH',
        retrievalQuery={'text': 'fire detection system'},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 5
            }
        }
    )
    
    print("=== CDPB5AI6BH 페이지 번호 확인 ===")
    
    for i, result in enumerate(response['retrievalResults'][:3]):
        metadata = result.get('metadata', {})
        content = result.get('content', {}).get('text', '')
        
        kb_page = metadata.get('x-amz-bedrock-kb-document-page-number', 'N/A')
        ocr_text = metadata.get('x-amz-bedrock-kb-description', content)
        image_uri = metadata.get('x-amz-bedrock-kb-byte-content-source', '')
        
        print(f"\n결과 {i+1}:")
        print(f"  KB 페이지 번호: {kb_page}")
        print(f"  OCR 텍스트 샘플: {ocr_text[:100]}...")
        print(f"  이미지 URI: {image_uri}")
        
        # 이미지 URI에서 실제 페이지 번호 추출
        if image_uri and '#page=' in image_uri:
            actual_page = image_uri.split('#page=')[1]
            print(f"  이미지 실제 페이지: {actual_page}")
            
            if str(kb_page) != str(actual_page):
                print(f"  ⚠️  불일치 발견: KB={kb_page}, 이미지={actual_page}")
            else:
                print(f"  ✅ 일치: {kb_page}")

if __name__ == "__main__":
    check_cdpb5ai6bh_pages()