#!/usr/bin/env python3
"""
원본 PDF에서 페이지별 OCR 추출 후 DynamoDB 저장
"""

import boto3
import json
from datetime import datetime
from typing import Dict, List

class PDFOCRExtraction:
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name='us-west-2')
        self.textract_client = boto3.client('textract', region_name='us-west-2')
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        
        # 원본 소스
        self.source_bucket = 'shi-kb-bucket'
        self.source_prefix = 'documents/all/'
        self.ocr_table_name = 'ship-firefighting-ocr'
    
    def extract_pdf_pages_ocr(self, pdf_key: str) -> List[Dict]:
        """PDF 파일의 모든 페이지 OCR 추출"""
        
        print(f"📄 PDF 처리 중: {pdf_key}")
        
        try:
            # Textract로 PDF 전체 분석
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': self.source_bucket,
                        'Name': pdf_key
                    }
                }
            )
            
            job_id = response['JobId']
            print(f"   작업 ID: {job_id}")
            
            # 작업 완료 대기
            import time
            while True:
                result = self.textract_client.get_document_text_detection(JobId=job_id)
                status = result['JobStatus']
                
                if status == 'SUCCEEDED':
                    break
                elif status == 'FAILED':
                    print(f"   ❌ Textract 실패")
                    return []
                
                print(f"   ⏳ 대기 중... ({status})")
                time.sleep(5)
            
            # 페이지별 텍스트 추출
            pages_ocr = {}
            
            # 모든 결과 페이지 처리
            next_token = None
            while True:
                if next_token:
                    result = self.textract_client.get_document_text_detection(
                        JobId=job_id, 
                        NextToken=next_token
                    )
                else:
                    result = self.textract_client.get_document_text_detection(JobId=job_id)
                
                # 블록별 처리
                for block in result['Blocks']:
                    if block['BlockType'] == 'LINE':
                        page_num = block['Page']
                        text = block['Text']
                        
                        if page_num not in pages_ocr:
                            pages_ocr[page_num] = []
                        pages_ocr[page_num].append(text)
                
                next_token = result.get('NextToken')
                if not next_token:
                    break
            
            # 문서 ID 생성 (파일명에서)
            document_id = self._extract_document_id(pdf_key)
            
            # 페이지별 OCR 데이터 구성
            ocr_results = []
            for page_num, text_lines in pages_ocr.items():
                ocr_results.append({
                    'document_id': document_id,
                    'page_number': str(page_num),
                    'ocr_text': '\n'.join(text_lines),
                    'page_image_url': f's3://{self.source_bucket}/{pdf_key}#page={page_num}',
                    'extracted_at': datetime.utcnow().isoformat() + 'Z',
                    'source_pdf': pdf_key,
                    'extraction_method': 'textract_pdf'
                })
            
            print(f"   ✅ 완료: {len(ocr_results)}페이지")
            return ocr_results
            
        except Exception as e:
            print(f"   ❌ PDF OCR 실패: {e}")
            return []
    
    def process_all_pdfs(self) -> List[Dict]:
        """모든 PDF 파일 처리"""
        
        print("🚀 전체 PDF OCR 추출 시작")
        
        # PDF 파일 리스트 (전체 11개)
        pdf_files = [
            'documents/all/02-2 SOLAS Chapter II-2_Construction Fire Protection, Fire Detection and Fire Extinction.pdf',
            'documents/all/DNV-RU-SHIP-Pt4 Ch6.pdf',
            'documents/all/DNV-RU-SHIP-Pt6 Ch5 Sec4.pdf',
            'documents/all/Design guidance_Spoolcutting.PDF',
            'documents/all/Design guidance_Support.PDF',
            'documents/all/Design_guidance_hull_penetration.PDF',
            'documents/all/FSS.pdf',
            'documents/all/IGC_Code_latest.pdf',
            'documents/all/Piping practice_Support.PDF',
            'documents/all/Piping_practice_hull_penetration.PDF'
        ]
        
        all_ocr_results = []
        
        for pdf_key in pdf_files:
            ocr_results = self.extract_pdf_pages_ocr(pdf_key)
            all_ocr_results.extend(ocr_results)
        
        return all_ocr_results
    
    def save_to_dynamodb(self, ocr_results: List[Dict]) -> bool:
        """DynamoDB에 저장"""
        
        print(f"💾 DynamoDB 저장: {len(ocr_results)}개 페이지")
        
        try:
            table = self.dynamodb.Table(self.ocr_table_name)
            
            # 배치 저장
            with table.batch_writer() as batch:
                for ocr_data in ocr_results:
                    batch.put_item(Item=ocr_data)
            
            print("✅ DynamoDB 저장 완료")
            return True
            
        except Exception as e:
            print(f"❌ DynamoDB 저장 실패: {e}")
            return False
    
    def _extract_document_id(self, pdf_key: str) -> str:
        """PDF 파일명에서 문서 ID 추출"""
        
        filename = pdf_key.split('/')[-1].replace('.pdf', '').replace('.PDF', '')
        
        # 파일명 정리
        if 'SOLAS' in filename:
            return 'solas_chapter2'
        elif 'DNV-RU-SHIP-Pt4' in filename:
            return 'dnv_pt4_ch6'
        elif 'DNV-RU-SHIP-Pt6' in filename:
            return 'dnv_pt6_ch5'
        elif 'FSS' in filename:
            return 'fss_code'
        elif 'IGC' in filename:
            return 'igc_code'
        elif 'Design guidance_Spoolcutting' in filename:
            return 'design_guidance_spoolcutting'
        elif 'Design guidance_Support' in filename:
            return 'design_guidance_support'
        elif 'Design_guidance_hull_penetration' in filename:
            return 'design_guidance_hull_penetration'
        elif 'Piping practice_Support' in filename:
            return 'piping_practice_support'
        elif 'Piping_practice_hull_penetration' in filename:
            return 'piping_practice_hull_penetration'
        else:
            return filename.lower().replace(' ', '_').replace('-', '_')

def execute_pdf_ocr_extraction():
    """PDF OCR 추출 실행"""
    
    extractor = PDFOCRExtraction()
    
    # 1. 모든 PDF 처리
    ocr_results = extractor.process_all_pdfs()
    
    if ocr_results:
        # 2. DynamoDB 저장
        success = extractor.save_to_dynamodb(ocr_results)
        
        if success:
            print(f"\n🎉 완료!")
            print(f"   - 처리된 페이지: {len(ocr_results)}개")
            print(f"   - 문서별 통계:")
            
            doc_stats = {}
            for result in ocr_results:
                doc_id = result['document_id']
                doc_stats[doc_id] = doc_stats.get(doc_id, 0) + 1
            
            for doc_id, page_count in doc_stats.items():
                print(f"     {doc_id}: {page_count}페이지")

if __name__ == "__main__":
    execute_pdf_ocr_extraction()