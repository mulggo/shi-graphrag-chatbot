#!/usr/bin/env python3
"""
S3 이미지 로드 기능 테스트
"""

import boto3
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

from ui.reference_display import ReferenceDisplay

def test_s3_image_loading():
    """S3 이미지 로드 테스트"""
    
    display = ReferenceDisplay()
    
    # 테스트 URI
    test_uri = "s3://claude-neptune/aws/bedrock/knowledge_bases/PWRU19RDNE/O1UH2CWINM/"
    
    print(f"🔍 S3 이미지 로드 테스트: {test_uri}")
    
    try:
        images = display._get_s3_images_from_directory(test_uri)
        
        print(f"📊 결과: {len(images)}개 이미지")
        
        for i, (img_key, img_data) in enumerate(images[:3]):
            print(f"  {i+1}. {img_key} ({len(img_data)} bytes)")
            
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_s3_image_loading()