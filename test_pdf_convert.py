#!/usr/bin/env python3
import boto3
import fitz

# 간단한 테스트
s3_client = boto3.client('s3', region_name='us-west-2')

# S3에서 작은 PDF 하나만 테스트
try:
    pdf_obj = s3_client.get_object(
        Bucket='shi-kb-bucket', 
        Key='documents/all/FSS.pdf'
    )
    pdf_data = pdf_obj['Body'].read()
    
    pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
    print(f"PDF 열기 성공: {len(pdf_doc)}페이지")
    
    # 첫 페이지만 테스트
    page = pdf_doc.load_page(0)
    pix = page.get_pixmap()
    print(f"첫 페이지 변환 성공: {pix.width}x{pix.height}")
    
    pdf_doc.close()
    print("✅ 테스트 성공")
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")