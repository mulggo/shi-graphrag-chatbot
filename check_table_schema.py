#!/usr/bin/env python3
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('ship-firefighting-ocr')

# 테이블 스키마 확인
print("=== 테이블 스키마 ===")
print(f"테이블명: {table.table_name}")
print(f"키 스키마: {table.key_schema}")
print(f"속성 정의: {table.attribute_definitions}")

# 샘플 데이터 확인
print("\n=== 샘플 데이터 ===")
response = table.scan(Limit=2)
for item in response['Items']:
    print(f"document_id: {item['document_id']} (타입: {type(item['document_id'])})")
    print(f"page_number: {item['page_number']} (타입: {type(item['page_number'])})")
    break