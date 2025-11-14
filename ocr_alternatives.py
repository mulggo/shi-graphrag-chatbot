#!/usr/bin/env python3
"""
KB 외부에서 OCR 데이터를 가져오는 대안 방법들
"""

import boto3
import json
from typing import Dict, List, Any

class OCRAlternatives:
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name='us-west-2')
        self.textract_client = boto3.client('textract', region_name='us-west-2')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    def method1_s3_textract_ocr(self, bucket: str, key: str) -> Dict:
        """방법 1: S3 원본 이미지를 Textract로 OCR"""
        
        try:
            response = self.textract_client.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            
            # 텍스트 추출
            text_blocks = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    text_blocks.append(block['Text'])
            
            return {
                'success': True,
                'ocr_text': '\n'.join(text_blocks),
                'page_number': self._extract_page_from_filename(key),
                'source': f's3://{bucket}/{key}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def method2_claude_vision_ocr(self, bucket: str, key: str) -> Dict:
        """방법 2: Claude Vision으로 이미지 OCR"""
        
        try:
            # S3에서 이미지 다운로드
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            image_data = response['Body'].read()
            
            # Claude Vision으로 OCR
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
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
                                "text": "Extract all text from this image. Include page numbers if visible."
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
            ocr_text = result['content'][0]['text']
            
            return {
                'success': True,
                'ocr_text': ocr_text,
                'page_number': self._extract_page_from_filename(key),
                'source': f's3://{bucket}/{key}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def method3_kb_content_parsing(self, kb_response: Dict) -> Dict:
        """방법 3: KB 응답에서 OCR 텍스트 파싱"""
        
        try:
            # KB 응답의 content에서 OCR 텍스트 추출
            content = kb_response.get('content', '')
            
            # 패턴 매칭으로 페이지 번호 추출
            import re
            page_match = re.search(r'(?:page|페이지)\s*(\d+)', content, re.IGNORECASE)
            page_number = page_match.group(1) if page_match else None
            
            # 전체 텍스트를 OCR로 간주
            return {
                'success': True,
                'ocr_text': content,
                'page_number': page_number,
                'source': 'kb_content_parsing'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def method4_s3_metadata_lookup(self, bucket: str, prefix: str = '') -> List[Dict]:
        """방법 4: S3 메타데이터에서 OCR 정보 조회"""
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            
            ocr_data = []
            for obj in response.get('Contents', []):
                # 객체 메타데이터 조회
                metadata_response = self.s3_client.head_object(
                    Bucket=bucket,
                    Key=obj['Key']
                )
                
                metadata = metadata_response.get('Metadata', {})
                
                if 'ocr_text' in metadata or 'page_number' in metadata:
                    ocr_data.append({
                        'key': obj['Key'],
                        'ocr_text': metadata.get('ocr_text', ''),
                        'page_number': metadata.get('page_number', ''),
                        'source': f's3://{bucket}/{obj["Key"]}'
                    })
            
            return ocr_data
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def _extract_page_from_filename(self, filename: str) -> str:
        """파일명에서 페이지 번호 추출"""
        import re
        match = re.search(r'(?:page|p)[-_]?(\d+)', filename, re.IGNORECASE)
        return match.group(1) if match else 'unknown'

# 사용 예시
def test_ocr_alternatives():
    ocr = OCRAlternatives()
    
    # 방법 1: Textract OCR
    result1 = ocr.method1_s3_textract_ocr('claude-neptune', 'sample-page.jpg')
    print("Textract OCR:", result1)
    
    # 방법 2: Claude Vision OCR  
    result2 = ocr.method2_claude_vision_ocr('claude-neptune', 'sample-page.jpg')
    print("Claude Vision OCR:", result2)
    
    # 방법 4: S3 메타데이터 조회
    result4 = ocr.method4_s3_metadata_lookup('claude-neptune')
    print("S3 Metadata:", result4[:2])  # 처음 2개만

if __name__ == "__main__":
    test_ocr_alternatives()