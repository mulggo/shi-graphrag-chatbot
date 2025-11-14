#!/usr/bin/env python3
"""
페이지 번호 기반 OCR 정보 조회 서비스
KB에서 페이지 번호를 받아서 별도 저장소에서 OCR 데이터 조회
"""

import boto3
import json
import re
from typing import Dict, List, Optional, Any

class OCRLookupService:
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.s3_client = boto3.client('s3', region_name='us-west-2')
        
        # OCR 데이터 저장용 테이블/버킷
        self.ocr_table_name = 'ship-firefighting-ocr'
        self.ocr_bucket = 'claude-neptune-ocr'
    
    def extract_page_numbers_from_kb_response(self, kb_response: Dict) -> List[str]:
        """KB 응답에서 페이지 번호 추출"""
        
        page_numbers = []
        
        # 참조 문서에서 페이지 번호 추출
        references = kb_response.get('references', [])
        for ref in references:
            source = ref.get('source', '')
            content = ref.get('content', '')
            
            # 소스에서 페이지 번호 추출 (파일명 패턴)
            page_match = re.search(r'(?:page|p)[-_]?(\d+)', source, re.IGNORECASE)
            if page_match:
                page_numbers.append(page_match.group(1))
            
            # 콘텐츠에서 페이지 번호 추출
            content_match = re.search(r'(?:page|페이지)\s*(\d+)', content, re.IGNORECASE)
            if content_match:
                page_numbers.append(content_match.group(1))
        
        return list(set(page_numbers))  # 중복 제거
    
    def get_ocr_from_dynamodb(self, page_number: str, document_id: str = 'default') -> Optional[Dict]:
        """DynamoDB에서 OCR 데이터 조회"""
        
        try:
            table = self.dynamodb.Table(self.ocr_table_name)
            
            response = table.get_item(
                Key={
                    'document_id': document_id,
                    'page_number': page_number
                }
            )
            
            if 'Item' in response:
                return {
                    'page_number': page_number,
                    'ocr_text': response['Item'].get('ocr_text', ''),
                    'page_image_url': response['Item'].get('page_image_url', ''),
                    'extracted_at': response['Item'].get('extracted_at', ''),
                    'source': 'dynamodb'
                }
            
            return None
            
        except Exception as e:
            print(f"DynamoDB 조회 실패: {e}")
            return None
    
    def get_ocr_from_s3(self, page_number: str, document_id: str = 'default') -> Optional[Dict]:
        """S3에서 OCR 데이터 조회"""
        
        try:
            # S3 키 패턴: ocr/{document_id}/page_{page_number}.json
            key = f'ocr/{document_id}/page_{page_number}.json'
            
            response = self.s3_client.get_object(
                Bucket=self.ocr_bucket,
                Key=key
            )
            
            ocr_data = json.loads(response['Body'].read())
            ocr_data['source'] = 's3'
            
            return ocr_data
            
        except Exception as e:
            print(f"S3 조회 실패: {e}")
            return None
    
    def lookup_ocr_data(self, page_numbers: List[str], document_id: str = 'default') -> Dict[str, Dict]:
        """페이지 번호 리스트로 OCR 데이터 일괄 조회"""
        
        ocr_results = {}
        
        for page_num in page_numbers:
            # 1순위: DynamoDB 조회
            ocr_data = self.get_ocr_from_dynamodb(page_num, document_id)
            
            # 2순위: S3 조회
            if not ocr_data:
                ocr_data = self.get_ocr_from_s3(page_num, document_id)
            
            if ocr_data:
                ocr_results[page_num] = ocr_data
        
        return ocr_results
    
    def enhance_kb_response_with_ocr(self, kb_response: Dict, kb_id: str, document_id: str = 'default') -> Dict:
        """KB 응답에 OCR 데이터 추가 (PWRU19RDNE KB에만 적용)"""
        
        # CDPB5AI6BH KB는 이미 OCR 메타데이터가 있으므로 스킵
        if kb_id == 'CDPB5AI6BH':
            return kb_response
        
        # PWRU19RDNE KB에만 OCR 조회 서비스 적용
        if kb_id != 'PWRU19RDNE':
            return kb_response
        
        # 1. KB 응답에서 페이지 번호 추출
        page_numbers = self.extract_page_numbers_from_kb_response(kb_response)
        
        if not page_numbers:
            return kb_response
        
        # 2. OCR 데이터 조회
        ocr_data = self.lookup_ocr_data(page_numbers, document_id)
        
        # 3. KB 응답에 OCR 정보 추가
        enhanced_response = kb_response.copy()
        enhanced_response['ocr_data'] = ocr_data
        enhanced_response['page_numbers'] = page_numbers
        
        # 4. 참조 문서에 OCR 텍스트 추가
        for ref in enhanced_response.get('references', []):
            for page_num, ocr_info in ocr_data.items():
                if page_num in ref.get('source', '') or page_num in ref.get('content', ''):
                    ref['ocr_text'] = ocr_info.get('ocr_text', '')
                    ref['page_image_url'] = ocr_info.get('page_image_url', '')
        
        return enhanced_response

# DynamoDB 테이블 생성 스크립트
def create_ocr_table():
    """OCR 데이터 저장용 DynamoDB 테이블 생성"""
    
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    
    table = dynamodb.create_table(
        TableName='ship-firefighting-ocr',
        KeySchema=[
            {
                'AttributeName': 'document_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'page_number',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'document_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'page_number',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    return table

# 사용 예시
def test_ocr_lookup():
    service = OCRLookupService()
    
    # 가상의 KB 응답
    kb_response = {
        'content': '선박의 소화기 요구사항은 페이지 15에 명시되어 있습니다.',
        'references': [
            {
                'source': 'solas_chapter2_page_15.pdf',
                'content': '고정식 소화 시스템... (page 15)',
                'score': 0.85
            }
        ]
    }
    
    # OCR 데이터로 KB 응답 강화
    enhanced = service.enhance_kb_response_with_ocr(kb_response)
    
    print("강화된 응답:")
    print(f"페이지 번호: {enhanced.get('page_numbers', [])}")
    print(f"OCR 데이터: {enhanced.get('ocr_data', {})}")

if __name__ == "__main__":
    test_ocr_lookup()