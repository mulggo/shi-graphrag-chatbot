#!/usr/bin/env python3
"""
UUID 파일명 기반 OCR 전략 - KB 응답과 S3 이미지 매칭
"""

import boto3
import json
import re
from typing import Dict, List, Optional

class AlternativeOCRStrategy:
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name='us-west-2')
        self.textract_client = boto3.client('textract', region_name='us-west-2')
        self.bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    def method1_kb_source_to_s3_mapping(self, kb_response: Dict) -> List[Dict]:
        """방법 1: KB 응답의 source 정보로 S3 이미지 매핑"""
        
        ocr_results = []
        
        for ref in kb_response.get('references', []):
            source = ref.get('source', '')
            
            # source에서 S3 URI 추출
            s3_match = re.search(r's3://([^/]+)/(.+)', source)
            if s3_match:
                bucket = s3_match.group(1)
                key = s3_match.group(2)
                
                # 해당 이미지의 OCR 추출
                ocr_text = self._extract_ocr_from_s3(bucket, key)
                if ocr_text:
                    ocr_results.append({
                        'source': source,
                        'ocr_text': ocr_text,
                        'reference_content': ref.get('content', ''),
                        'score': ref.get('score', 0)
                    })
        
        return ocr_results
    
    def method2_content_similarity_matching(self, kb_response: Dict) -> List[Dict]:
        """방법 2: KB 콘텐츠와 S3 이미지 OCR 유사도 매칭"""
        
        # KB 응답의 주요 키워드 추출
        content = kb_response.get('content', '')
        keywords = self._extract_keywords(content)
        
        # S3의 모든 이미지에서 OCR 추출 후 유사도 계산
        s3_images = self._list_s3_images('claude-neptune')
        
        matched_results = []
        for image_key in s3_images[:10]:  # 처음 10개만 테스트
            ocr_text = self._extract_ocr_from_s3('claude-neptune', image_key)
            
            if ocr_text:
                similarity = self._calculate_similarity(keywords, ocr_text)
                if similarity > 0.3:  # 임계값
                    matched_results.append({
                        'image_key': image_key,
                        'ocr_text': ocr_text,
                        'similarity': similarity
                    })
        
        # 유사도 순으로 정렬
        return sorted(matched_results, key=lambda x: x['similarity'], reverse=True)
    
    def method3_kb_retrieve_with_image_refs(self, query: str, kb_id: str) -> Dict:
        """방법 3: KB 검색시 이미지 참조 정보 함께 조회"""
        
        try:
            response = self.bedrock_agent.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5
                    }
                }
            )
            
            enhanced_results = []
            for result in response.get('retrievalResults', []):
                
                # 메타데이터에서 이미지 정보 확인
                metadata = result.get('metadata', {})
                
                # location에서 S3 정보 추출
                location = result.get('location', {})
                s3_location = location.get('s3Location', {})
                
                if s3_location:
                    bucket = s3_location.get('uri', '').replace('s3://', '').split('/')[0]
                    key = '/'.join(s3_location.get('uri', '').replace('s3://', '').split('/')[1:])
                    
                    # 해당 이미지의 OCR 추출
                    ocr_text = self._extract_ocr_from_s3(bucket, key)
                    
                    enhanced_results.append({
                        'content': result.get('content', {}).get('text', ''),
                        'score': result.get('score', 0),
                        'metadata': metadata,
                        's3_location': s3_location.get('uri', ''),
                        'ocr_text': ocr_text,
                        'source': 'kb_retrieve_enhanced'
                    })
            
            return {
                'results': enhanced_results,
                'query': query,
                'kb_id': kb_id
            }
            
        except Exception as e:
            print(f"KB 검색 실패: {e}")
            return {'results': [], 'error': str(e)}
    
    def _extract_ocr_from_s3(self, bucket: str, key: str) -> str:
        """S3 이미지에서 OCR 추출"""
        
        try:
            response = self.textract_client.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            
            text_blocks = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    text_blocks.append(block['Text'])
            
            return '\n'.join(text_blocks)
            
        except Exception as e:
            print(f"OCR 추출 실패 ({key}): {e}")
            return ""
    
    def _list_s3_images(self, bucket: str) -> List[str]:
        """S3 버킷의 이미지 파일 리스트"""
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix='aws/bedrock/knowledge_bases/PWRU19RDNE/',
                MaxKeys=50
            )
            
            return [obj['Key'] for obj in response.get('Contents', [])]
            
        except Exception as e:
            print(f"S3 리스트 실패: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 주요 키워드 추출"""
        
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 필요)
        import re
        words = re.findall(r'\b[가-힣a-zA-Z]{2,}\b', text)
        return list(set(words))[:10]  # 상위 10개
    
    def _calculate_similarity(self, keywords: List[str], ocr_text: str) -> float:
        """키워드와 OCR 텍스트 유사도 계산"""
        
        if not keywords or not ocr_text:
            return 0.0
        
        matches = sum(1 for keyword in keywords if keyword in ocr_text)
        return matches / len(keywords)

# 테스트 함수
def test_alternative_strategies():
    strategy = AlternativeOCRStrategy()
    
    # 방법 3 테스트: KB 검색 + 이미지 OCR
    result = strategy.method3_kb_retrieve_with_image_refs(
        "선박 소화기 요구사항", 
        "PWRU19RDNE"
    )
    
    print("🔍 KB 검색 + OCR 결과:")
    for i, res in enumerate(result.get('results', [])[:2]):
        print(f"\n{i+1}. 점수: {res.get('score', 0):.3f}")
        print(f"   콘텐츠: {res.get('content', '')[:100]}...")
        print(f"   S3 위치: {res.get('s3_location', '')}")
        print(f"   OCR 텍스트: {res.get('ocr_text', '')[:100]}...")

if __name__ == "__main__":
    test_alternative_strategies()