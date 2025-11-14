#!/usr/bin/env python3
"""
PDF를 페이지별 이미지로 변환하여 S3 업로드 및 DynamoDB 업데이트
"""

import boto3
import fitz  # PyMuPDF
import io
import os
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFToImageProcessor:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name='us-west-2')
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.table = self.dynamodb.Table('ship-firefighting-ocr')
        self.bucket = 'shi-kb-bucket'
        
    def convert_pdf_to_images(self, pdf_s3_key: str, document_id: str) -> int:
        """PDF를 페이지별 이미지로 변환하고 S3 업로드"""
        
        # S3에서 PDF 다운로드
        logger.info(f"PDF 다운로드: {pdf_s3_key}")
        pdf_obj = self.s3_client.get_object(Bucket=self.bucket, Key=pdf_s3_key)
        pdf_data = pdf_obj['Body'].read()
        
        # PDF 열기
        pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
        total_pages = len(pdf_doc)
        logger.info(f"총 {total_pages}페이지 처리 시작")
        
        uploaded_count = 0
        
        for page_num in range(total_pages):
            try:
                # 페이지를 이미지로 변환
                page = pdf_doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x 해상도
                img_data = pix.tobytes("png")
                
                # S3 키 생성
                s3_key = f"page_images/{document_id}/page_{page_num + 1:03d}.png"
                
                # S3 업로드
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=s3_key,
                    Body=img_data,
                    ContentType='image/png'
                )
                
                # DynamoDB 업데이트
                image_url = f"s3://{self.bucket}/{s3_key}"
                self.update_dynamodb_image_url(document_id, page_num + 1, image_url)
                
                uploaded_count += 1
                if uploaded_count % 10 == 0:
                    logger.info(f"진행률: {uploaded_count}/{total_pages}")
                    
            except Exception as e:
                logger.error(f"페이지 {page_num + 1} 처리 실패: {e}")
        
        pdf_doc.close()
        logger.info(f"완료: {uploaded_count}/{total_pages} 페이지")
        return uploaded_count
    
    def update_dynamodb_image_url(self, document_id: str, page_number: int, image_url: str):
        """DynamoDB 레코드의 이미지 URL 업데이트"""
        try:
            self.table.update_item(
                Key={
                    'document_id': document_id,
                    'page_number': str(page_number)  # 문자열로 변환
                },
                UpdateExpression='SET page_image_url = :url',
                ExpressionAttributeValues={':url': image_url}
            )
        except Exception as e:
            logger.error(f"DynamoDB 업데이트 실패: {document_id} 페이지 {page_number} - {e}")

def main():
    processor = PDFToImageProcessor()
    
    # PDF 파일 매핑 (S3 키 → 문서 ID) - 전체 11개
    pdf_mappings = [
        {
            's3_key': 'documents/all/02-2 SOLAS Chapter II-2_Construction Fire Protection, Fire Detection and Fire Extinction.pdf',
            'document_id': 'solas_chapter2'
        },
        {
            's3_key': 'documents/all/FSS.pdf', 
            'document_id': 'fss_code'
        },
        {
            's3_key': 'documents/all/DNV-RU-SHIP-Pt4 Ch6.pdf',
            'document_id': 'dnv_pt4_ch6'
        },
        {
            's3_key': 'documents/all/DNV-RU-SHIP-Pt6 Ch5 Sec4.pdf',
            'document_id': 'dnv_pt6_ch5'
        },
        {
            's3_key': 'documents/all/IGC_Code_latest.pdf',
            'document_id': 'igc_code'
        },
        {
            's3_key': 'documents/all/Design guidance_Spoolcutting.PDF',
            'document_id': 'design_guidance_spoolcutting'
        },
        {
            's3_key': 'documents/all/Design guidance_Support.PDF',
            'document_id': 'design_guidance_support'
        },
        {
            's3_key': 'documents/all/Design_guidance_hull_penetration.PDF',
            'document_id': 'design_guidance_hull_penetration'
        },
        {
            's3_key': 'documents/all/Piping practice_Support.PDF',
            'document_id': 'piping_practice_support'
        },
        {
            's3_key': 'documents/all/Piping_practice_hull_penetration.PDF',
            'document_id': 'piping_practice_hull_penetration'
        }
    ]
    
    total_processed = 0
    
    for mapping in pdf_mappings:
        logger.info(f"\n=== {mapping['document_id']} 처리 시작 ===")
        
        try:
            count = processor.convert_pdf_to_images(
                mapping['s3_key'], 
                mapping['document_id']
            )
            total_processed += count
            logger.info(f"{mapping['document_id']} 완료: {count}페이지")
            
        except Exception as e:
            logger.error(f"{mapping['document_id']} 실패: {e}")
    
    logger.info(f"\n🎉 전체 완료: {total_processed}페이지 처리됨")

if __name__ == "__main__":
    main()