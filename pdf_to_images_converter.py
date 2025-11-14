#!/usr/bin/env python3
"""
PDF를 페이지별 이미지로 변환하여 S3에 업로드하고 DynamoDB에 저장
"""

import boto3
import fitz  # PyMuPDF
import io
from PIL import Image
import os
from typing import Dict, List
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFToImageConverter:
    def __init__(self, s3_bucket: str, dynamodb_table: str, region: str = 'us-west-2'):
        self.s3_client = boto3.client('s3', region_name=region)
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(dynamodb_table)
        self.s3_bucket = s3_bucket
        
    def convert_pdf_to_images(self, pdf_path: str, document_id: str) -> List[Dict]:
        """PDF를 페이지별 이미지로 변환하고 S3에 업로드"""
        results = []
        
        # PDF 열기
        pdf_document = fitz.open(pdf_path)
        
        for page_num in range(len(pdf_document)):
            try:
                # 페이지를 이미지로 변환
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x 해상도
                img_data = pix.tobytes("png")
                
                # S3 키 생성 (페이지 번호 포함)
                s3_key = f"page_images/{document_id}/page_{page_num + 1:03d}.png"
                
                # S3에 업로드
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                    Body=img_data,
                    ContentType='image/png'
                )
                
                # S3 URL 생성
                image_url = f"s3://{self.s3_bucket}/{s3_key}"
                
                results.append({
                    'page_number': page_num + 1,
                    'image_url': image_url,
                    's3_key': s3_key
                })
                
                logger.info(f"페이지 {page_num + 1} 변환 완료: {s3_key}")
                
            except Exception as e:
                logger.error(f"페이지 {page_num + 1} 변환 실패: {e}")
                continue
        
        pdf_document.close()
        return results
    
    def update_dynamodb_with_images(self, document_id: str, page_images: List[Dict]):
        """DynamoDB 레코드에 이미지 URL 업데이트"""
        updated_count = 0
        
        for page_info in page_images:
            page_number = page_info['page_number']
            image_url = page_info['image_url']
            
            try:
                # DynamoDB 레코드 업데이트
                response = self.table.update_item(
                    Key={
                        'document_id': document_id,
                        'page_number': page_number
                    },
                    UpdateExpression='SET page_image_url = :img_url',
                    ExpressionAttributeValues={
                        ':img_url': image_url
                    },
                    ReturnValues='UPDATED_NEW'
                )
                updated_count += 1
                logger.info(f"DynamoDB 업데이트 완료: {document_id} 페이지 {page_number}")
                
            except Exception as e:
                logger.error(f"DynamoDB 업데이트 실패: {document_id} 페이지 {page_number} - {e}")
        
        return updated_count

def main():
    # 설정
    S3_BUCKET = "shi-kb-bucket"  # 기존 버킷 사용
    DYNAMODB_TABLE = "ship-firefighting-ocr"
    
    # PDF 파일 목록 (기존 DynamoDB에 있는 문서들)
    pdf_files = [
        {"path": "/path/to/solas.pdf", "document_id": "solas"},
        {"path": "/path/to/fss_code.pdf", "document_id": "fss_code"},
        # 추가 PDF 파일들...
    ]
    
    converter = PDFToImageConverter(S3_BUCKET, DYNAMODB_TABLE)
    
    for pdf_info in pdf_files:
        pdf_path = pdf_info["path"]
        document_id = pdf_info["document_id"]
        
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
            continue
        
        logger.info(f"PDF 변환 시작: {document_id}")
        
        # PDF를 이미지로 변환
        page_images = converter.convert_pdf_to_images(pdf_path, document_id)
        
        # DynamoDB 업데이트
        updated_count = converter.update_dynamodb_with_images(document_id, page_images)
        
        logger.info(f"완료: {document_id} - {len(page_images)}개 이미지 생성, {updated_count}개 레코드 업데이트")

if __name__ == "__main__":
    main()