#!/usr/bin/env python3
import boto3

# DynamoDB 연결
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('ship-firefighting-ocr')

# 샘플 레코드 조회
response = table.scan(Limit=3)

print("=== DynamoDB OCR 데이터 구조 ===")
for item in response['Items']:
    print(f"\n문서: {item['document_id']}")
    print(f"페이지: {item['page_number']}")
    print(f"OCR 텍스트 길이: {len(item['ocr_text'])} 문자")
    print(f"이미지 URL: {item['page_image_url']}")
    print(f"OCR 텍스트 샘플: {item['ocr_text'][:100]}...")