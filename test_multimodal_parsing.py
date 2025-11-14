#!/usr/bin/env python3
"""
멀티모달 파싱 instruction 테스트 스크립트
PWRU19RDNE KB의 메타데이터 구조 확인
"""

import boto3
import json
from typing import Dict, Any

def test_kb_metadata_structure():
    """KB 메타데이터 구조 확인"""
    
    # Bedrock Agent 클라이언트
    bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    # 두 KB 비교 테스트
    kbs = {
        'CDPB5AI6BH': 'OCR 메타데이터 포함 KB',
        'PWRU19RDNE': '멀티모달 KB (수정 필요)'
    }
    
    for kb_id, description in kbs.items():
        print(f"\n=== {description} ({kb_id}) ===")
        
        try:
            # 간단한 검색으로 메타데이터 구조 확인
            response = bedrock_agent.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={
                    'text': 'fire extinguisher'
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 1
                    }
                }
            )
            
            # 첫 번째 결과의 메타데이터 분석
            if response['retrievalResults']:
                result = response['retrievalResults'][0]
                metadata = result.get('metadata', {})
                
                print(f"✅ 검색 성공")
                print(f"메타데이터 키: {list(metadata.keys())}")
                
                # OCR 관련 메타데이터 확인
                ocr_keys = [k for k in metadata.keys() if 'ocr' in k.lower() or 'page' in k.lower()]
                if ocr_keys:
                    print(f"📄 OCR 관련 키: {ocr_keys}")
                else:
                    print("❌ OCR 메타데이터 없음")
                    
                # 전체 메타데이터 구조 출력
                print(f"전체 메타데이터: {json.dumps(metadata, indent=2, ensure_ascii=False)[:500]}...")
                
        except Exception as e:
            print(f"❌ 검색 실패: {e}")

def check_s3_multimodal_storage():
    """S3 멀티모달 스토리지 확인"""
    
    s3_client = boto3.client('s3', region_name='us-west-2')
    bucket_name = 'claude-neptune'
    
    print(f"\n=== S3 멀티모달 스토리지 확인 ({bucket_name}) ===")
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=10
        )
        
        if 'Contents' in response:
            print(f"✅ 객체 {len(response['Contents'])}개 발견")
            
            for obj in response['Contents'][:3]:
                print(f"- {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("❌ 객체 없음")
            
    except Exception as e:
        print(f"❌ S3 접근 실패: {e}")

if __name__ == "__main__":
    print("🔍 멀티모달 파싱 메타데이터 구조 테스트")
    
    test_kb_metadata_structure()
    check_s3_multimodal_storage()
    
    print("\n📋 결론:")
    print("1. CDPB5AI6BH에 OCR 메타데이터가 있다면 ✅")
    print("2. PWRU19RDNE에 동일한 구조가 없다면 파싱 instruction 수정 필요 ❌")
    print("3. 멀티모달 파싱 instruction으로 재구성 권장 🔄")