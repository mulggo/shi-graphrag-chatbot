#!/usr/bin/env python3
"""
이미지 표시 기능 테스트
"""

import boto3
from agents.plan_execute_agent.agent import PlanExecuteAgent

def test_image_retrieval():
    """Plan-Execute Agent의 이미지 검색 기능 테스트"""
    
    # DynamoDB에서 샘플 레코드 확인
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('ship-firefighting-ocr')
    
    print("=== DynamoDB 샘플 레코드 확인 ===")
    response = table.scan(Limit=3)
    
    for item in response['Items']:
        print(f"문서: {item['document_id']}")
        print(f"페이지: {item['page_number']}")
        print(f"이미지 URL: {item['page_image_url']}")
        print(f"OCR 텍스트 길이: {len(item['ocr_text'])} 문자")
        print("---")
    
    # Agent 테스트
    print("\n=== Plan-Execute Agent 테스트 ===")
    agent = PlanExecuteAgent()
    
    # 테스트 쿼리
    test_message = "선박의 화재 감지 시스템에 대해 알려주세요"
    session_id = "test_session"
    
    try:
        response = agent.process_message(test_message, session_id)
        
        print(f"응답: {response['response'][:200]}...")
        print(f"참조 개수: {len(response.get('references', []))}")
        
        # 참조에 이미지가 포함되었는지 확인
        for i, ref in enumerate(response.get('references', [])[:3]):
            print(f"\n참조 {i+1}:")
            print(f"  소스: {ref.get('source', 'N/A')}")
            print(f"  이미지 URL: {ref.get('image_url', 'N/A')}")
            print(f"  OCR 텍스트 길이: {len(ref.get('ocr_text', ''))} 문자")
        
        return True
        
    except Exception as e:
        print(f"Agent 테스트 실패: {e}")
        return False

def test_s3_image_access():
    """S3 이미지 접근 테스트"""
    
    print("\n=== S3 이미지 접근 테스트 ===")
    s3_client = boto3.client('s3', region_name='us-west-2')
    
    # 샘플 이미지 확인
    test_keys = [
        'page_images/solas_chapter2/page_001.png',
        'page_images/fss_code/page_001.png',
        'page_images/igc_code/page_001.png'
    ]
    
    for key in test_keys:
        try:
            response = s3_client.head_object(Bucket='shi-kb-bucket', Key=key)
            size = response['ContentLength']
            print(f"✅ {key}: {size:,} bytes")
        except Exception as e:
            print(f"❌ {key}: {e}")

if __name__ == "__main__":
    print("🔍 이미지 표시 기능 테스트 시작\n")
    
    # 1. S3 이미지 접근 테스트
    test_s3_image_access()
    
    # 2. DynamoDB 및 Agent 테스트
    success = test_image_retrieval()
    
    if success:
        print("\n✅ 테스트 완료: 이미지 표시 준비됨")
    else:
        print("\n❌ 테스트 실패: 문제 확인 필요")