"""
참조 문서 표시 UI 컴포넌트
"""
import streamlit as st
from typing import List, Dict
import boto3

class ReferenceDisplay:
    """참조 문서 표시 관리 클래스"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name='us-west-2')
    
    def render_references(self, references: List[Dict]):
        """참조 정보 렌더링"""
        if not references:
            return
        
        st.markdown("---")
        st.markdown("**📚 참조 문서**")
        
        for i, ref in enumerate(references, 1):
            with st.expander(
                f"[{i}] {ref['source_file']} (페이지 {ref['page_number']})", 
                expanded=False
            ):
                self._render_single_reference(ref, i)
    
    def _render_single_reference(self, ref: Dict, index: int):
        """단일 참조 정보 렌더링"""
        # OCR 텍스트 표시
        st.subheader("📄 OCR 추출 텍스트")
        if ref.get('ocr_text'):
            st.text_area(
                "원문 내용", 
                ref['ocr_text'], 
                height=300, 
                key=f"ref_text_{index}",
                help="PDF에서 OCR로 추출된 원문 텍스트입니다."
            )
        else:
            st.info("텍스트 정보가 없습니다.")
        
        # 이미지 표시
        st.subheader("🖼️ 원본 이미지")
        if ref.get('image_uri'):
            try:
                image_data = self._get_s3_image(ref['image_uri'])
                if image_data:
                    st.image(
                        image_data, 
                        caption=f"페이지 {ref['page_number']} 원본 이미지 (클릭하면 확대)", 
                        use_container_width=True
                    )
                else:
                    st.warning("이미지 로드에 실패했습니다.")
            except Exception as e:
                st.error(f"이미지 로드 실패: {e}")
        else:
            st.info("이미지 정보가 없습니다.")
        
        # 메타데이터 정보
        st.markdown("**📋 문서 정보**")
        st.json({
            "파일명": ref.get('source_file', 'Unknown'),
            "페이지": ref.get('page_number', 0),
            "텍스트 길이": f"{len(ref.get('ocr_text', ''))} 문자"
        })
    
    def _get_s3_image(self, s3_uri: str) -> bytes:
        """S3에서 이미지 다운로드"""
        try:
            if s3_uri.startswith('s3://'):
                parts = s3_uri[5:].split('/', 1)
                bucket = parts[0]
                key = parts[1] if len(parts) > 1 else ''
                
                response = self.s3_client.get_object(Bucket=bucket, Key=key)
                return response['Body'].read()
        except Exception as e:
            st.error(f"S3 이미지 로드 실패: {e}")
        
        return None