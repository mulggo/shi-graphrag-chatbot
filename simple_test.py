#!/usr/bin/env python3
import boto3

# 1. DynamoDB 확인
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('ship-firefighting-ocr')

print("=== DynamoDB 이미지 URL 확인 ===")
response = table.scan(Limit=3)
for item in response['Items']:
    print(f"{item['document_id']} 페이지 {item['page_number']}: {item['page_image_url']}")

# 2. S3 이미지 확인
s3_client = boto3.client('s3', region_name='us-west-2')

print("\n=== S3 이미지 파일 확인 ===")
test_keys = [
    'page_images/solas_chapter2/page_001.png',
    'page_images/fss_code/page_001.png'
]

for key in test_keys:
    try:
        response = s3_client.head_object(Bucket='shi-kb-bucket', Key=key)
        print(f"✅ {key}: {response['ContentLength']:,} bytes")
    except Exception as e:
        print(f"❌ {key}: 없음")

print("\n결론: DynamoDB URL이 S3 이미지를 가리키면 Streamlit에서 표시 가능")