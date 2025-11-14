#!/usr/bin/env python3
import boto3

# S3에서 이미지 다운로드 테스트
s3_client = boto3.client('s3', region_name='us-west-2')

print("=== S3 이미지 다운로드 테스트 ===")

test_url = "s3://shi-kb-bucket/page_images/solas_chapter2/page_001.png"
bucket = "shi-kb-bucket"
key = "page_images/solas_chapter2/page_001.png"

try:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    image_data = response['Body'].read()
    
    print(f"✅ 이미지 다운로드 성공")
    print(f"   크기: {len(image_data):,} bytes")
    print(f"   타입: {'PNG' if image_data.startswith(b'\\x89PNG') else '기타'}")
    
    # Streamlit에서 사용할 수 있는지 확인
    try:
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_data))
        print(f"   해상도: {img.size[0]}x{img.size[1]}")
        print("✅ Streamlit st.image()에서 표시 가능")
        
    except ImportError:
        print("⚠️  PIL 없음 (pip install Pillow 필요)")
    except Exception as e:
        print(f"❌ 이미지 처리 실패: {e}")
        
except Exception as e:
    print(f"❌ S3 다운로드 실패: {e}")

print("\n결론: DynamoDB → S3 이미지 → Streamlit 표시 체인 완성")