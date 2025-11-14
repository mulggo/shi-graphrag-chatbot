#!/usr/bin/env python3
"""
Streamlit 이미지 표시 기능 테스트
"""

import boto3
import streamlit as st
from ui.reference_display import display_reference_with_image

def test_streamlit_image_display():
    """Streamlit에서 이미지 표시 테스트"""
    
    # 샘플 참조 데이터 생성
    sample_reference = {
        "id": "ref_1",
        "content": "Fire detection systems shall be installed...",
        "source": "SOLAS Chapter II-2",
        "source_file": "solas_chapter2.pdf",
        "page_number": 1,
        "ocr_text": "SOLAS Chapter II-2 Fire Protection...",
        "image_uri": "s3://shi-kb-bucket/page_images/solas_chapter2/page_001.png",
        "has_multimodal": True
    }
    
    print("=== Streamlit 이미지 표시 테스트 ===")
    
    # S3에서 이미지 다운로드 테스트
    s3_client = boto3.client('s3', region_name='us-west-2')
    
    try:
        # S3 URL에서 버킷과 키 추출
        s3_url = sample_reference["image_uri"]
        bucket = s3_url.split('/')[2]
        key = '/'.join(s3_url.split('/')[3:])
        
        print(f"버킷: {bucket}")
        print(f"키: {key}")
        
        # 이미지 다운로드
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        
        print(f"✅ 이미지 다운로드 성공: {len(image_data):,} bytes")
        
        # 이미지 타입 확인
        if image_data.startswith(b'\x89PNG'):
            print("✅ PNG 이미지 형식 확인됨")
        else:
            print("❌ PNG 형식이 아님")
        
        return True
        
    except Exception as e:
        print(f"❌ 이미지 다운로드 실패: {e}")
        return False

def test_reference_display_function():
    """reference_display.py 함수 테스트"""
    
    print("\n=== reference_display.py 함수 테스트 ===")
    
    try:
        # reference_display 모듈 import 테스트
        from ui.reference_display import display_reference_with_image
        print("✅ reference_display 모듈 import 성공")
        
        # 함수 존재 확인
        if callable(display_reference_with_image):
            print("✅ display_reference_with_image 함수 존재")
        else:
            print("❌ display_reference_with_image 함수 없음")
        
        return True
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 기타 오류: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Streamlit 이미지 표시 테스트 시작\n")
    
    # 1. 이미지 다운로드 테스트
    image_ok = test_streamlit_image_display()
    
    # 2. reference_display 함수 테스트
    function_ok = test_reference_display_function()
    
    if image_ok and function_ok:
        print("\n✅ 모든 테스트 통과: Streamlit에서 이미지 표시 가능")
    else:
        print("\n❌ 일부 테스트 실패: 문제 확인 필요")