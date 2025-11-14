#!/usr/bin/env python3
"""
DynamoDB OCR 테이블 구축을 위한 추출 플랜
S3 원본 이미지 → OCR 추출 → DynamoDB 저장
"""

import boto3
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import base64

class OCRExtractionPlan:
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name='us-west-2')
        self.textract_client = boto3.client('textract', region_name='us-west-2')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        
        # 설정
        self.source_bucket = 'claude-neptune'  # 원본 이미지 버킷
        self.ocr_table_name = 'ship-firefighting-ocr'
    
    def step1_scan_source_images(self) -> List[Dict]:
        """1단계: S3에서 원본 이미지 파일 스캔"""
        
        print("🔍 1단계: S3 원본 이미지 스캔")
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.source_bucket,
                Prefix='',  # 전체 스캔 또는 특정 prefix
                MaxKeys=1000
            )
            
            image_files = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                
                # 이미지 파일만 필터링
                if key.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
                    
                    # 파일명에서 문서 ID와 페이지 번호 추출
                    document_id, page_number = self._parse_filename(key)
                    
                    if document_id and page_number:
                        image_files.append({
                            'key': key,
                            'document_id': document_id,
                            'page_number': page_number,
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'].isoformat()
                        })
            
            print(f"✅ 발견된 이미지 파일: {len(image_files)}개")
            return image_files
            
        except Exception as e:
            print(f"❌ S3 스캔 실패: {e}")
            return []
    
    def step2_extract_ocr_batch(self, image_files: List[Dict]) -> List[Dict]:
        """2단계: 배치로 OCR 추출"""
        
        print("📝 2단계: OCR 텍스트 추출")
        
        ocr_results = []
        
        for i, file_info in enumerate(image_files):
            print(f"처리 중: {i+1}/{len(image_files)} - {file_info['key']}")
            
            try:
                # Textract로 OCR 추출
                ocr_text = self._extract_ocr_textract(file_info['key'])
                
                # 추출 실패시 Claude Vision 시도
                if not ocr_text:
                    ocr_text = self._extract_ocr_claude_vision(file_info['key'])
                
                if ocr_text:
                    ocr_results.append({
                        'document_id': file_info['document_id'],
                        'page_number': file_info['page_number'],
                        'ocr_text': ocr_text,
                        'page_image_url': f"s3://{self.source_bucket}/{file_info['key']}",
                        'extracted_at': datetime.utcnow().isoformat() + 'Z',
                        'file_size': file_info['size'],
                        'extraction_method': 'textract'
                    })
                
            except Exception as e:
                print(f"❌ OCR 추출 실패 ({file_info['key']}): {e}")
        
        print(f"✅ OCR 추출 완료: {len(ocr_results)}개")
        return ocr_results
    
    def step3_save_to_dynamodb(self, ocr_results: List[Dict]) -> bool:
        """3단계: DynamoDB에 저장"""
        
        print("💾 3단계: DynamoDB 저장")
        
        try:
            table = self.dynamodb.Table(self.ocr_table_name)
            
            # 배치 저장
            with table.batch_writer() as batch:
                for ocr_data in ocr_results:
                    batch.put_item(Item=ocr_data)
            
            print(f"✅ DynamoDB 저장 완료: {len(ocr_results)}개 레코드")
            return True
            
        except Exception as e:
            print(f"❌ DynamoDB 저장 실패: {e}")
            return False
    
    def step4_create_index_summary(self) -> Dict:
        """4단계: 인덱스 요약 생성"""
        
        print("📊 4단계: 인덱스 요약 생성")
        
        try:
            table = self.dynamodb.Table(self.ocr_table_name)
            
            # 전체 스캔으로 통계 생성
            response = table.scan()
            items = response['Items']
            
            # 문서별 페이지 수 집계
            doc_stats = {}
            for item in items:
                doc_id = item['document_id']
                if doc_id not in doc_stats:
                    doc_stats[doc_id] = {
                        'page_count': 0,
                        'total_ocr_length': 0,
                        'pages': []
                    }
                
                doc_stats[doc_id]['page_count'] += 1
                doc_stats[doc_id]['total_ocr_length'] += len(item.get('ocr_text', ''))
                doc_stats[doc_id]['pages'].append(item['page_number'])
            
            summary = {
                'total_documents': len(doc_stats),
                'total_pages': len(items),
                'documents': doc_stats,
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            print(f"✅ 인덱스 요약:")
            print(f"   - 총 문서: {summary['total_documents']}개")
            print(f"   - 총 페이지: {summary['total_pages']}개")
            
            return summary
            
        except Exception as e:
            print(f"❌ 인덱스 요약 생성 실패: {e}")
            return {}
    
    def _parse_filename(self, filename: str) -> tuple:
        """파일명에서 document_id와 page_number 추출"""
        
        # 패턴 1: solas_chapter2_page_15.jpg
        pattern1 = r'([a-zA-Z0-9_]+)_page_(\d+)\.'
        match1 = re.search(pattern1, filename, re.IGNORECASE)
        if match1:
            return match1.group(1), match1.group(2)
        
        # 패턴 2: chapter2/page_15.jpg
        pattern2 = r'([a-zA-Z0-9_]+)/.*page_?(\d+)\.'
        match2 = re.search(pattern2, filename, re.IGNORECASE)
        if match2:
            return match2.group(1), match2.group(2)
        
        # 패턴 3: doc_15.jpg (페이지 번호만)
        pattern3 = r'(\w+)_(\d+)\.'
        match3 = re.search(pattern3, filename, re.IGNORECASE)
        if match3:
            return 'default_document', match3.group(2)
        
        return None, None
    
    def _extract_ocr_textract(self, s3_key: str) -> str:
        """Textract로 OCR 추출"""
        
        try:
            response = self.textract_client.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': self.source_bucket,
                        'Name': s3_key
                    }
                }
            )
            
            text_blocks = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    text_blocks.append(block['Text'])
            
            return '\n'.join(text_blocks)
            
        except Exception as e:
            print(f"Textract 실패 ({s3_key}): {e}")
            return ""
    
    def _extract_ocr_claude_vision(self, s3_key: str) -> str:
        """Claude Vision으로 OCR 추출 (폴백)"""
        
        try:
            # S3에서 이미지 다운로드
            response = self.s3_client.get_object(Bucket=self.source_bucket, Key=s3_key)
            image_data = response['Body'].read()
            
            # Base64 인코딩
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Claude Vision 호출
            prompt = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": "Extract all text from this document page. Preserve formatting and include page numbers if visible."
                            }
                        ]
                    }
                ]
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps(prompt)
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            print(f"Claude Vision 실패 ({s3_key}): {e}")
            return ""

def execute_full_extraction_plan():
    """전체 추출 플랜 실행"""
    
    print("🚀 OCR 추출 플랜 시작")
    
    extractor = OCRExtractionPlan()
    
    # 1단계: 이미지 파일 스캔
    image_files = extractor.step1_scan_source_images()
    if not image_files:
        print("❌ 처리할 이미지 파일이 없습니다.")
        return
    
    # 2단계: OCR 추출
    ocr_results = extractor.step2_extract_ocr_batch(image_files)
    if not ocr_results:
        print("❌ OCR 추출 결과가 없습니다.")
        return
    
    # 3단계: DynamoDB 저장
    success = extractor.step3_save_to_dynamodb(ocr_results)
    if not success:
        print("❌ DynamoDB 저장 실패")
        return
    
    # 4단계: 인덱스 요약
    summary = extractor.step4_create_index_summary()
    
    print("🎉 OCR 추출 플랜 완료!")
    return summary

if __name__ == "__main__":
    execute_full_extraction_plan()