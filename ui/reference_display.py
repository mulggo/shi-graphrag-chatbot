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
        
        # Plan-Execute Agent 형식 감지
        if references and 'source_file' not in references[0]:
            self._render_simple_references(references)
        else:
            # 기존 형식
            for i, ref in enumerate(references, 1):
                with st.expander(
                    f"[{i}] {ref['source_file']} (페이지 {ref['page_number']})", 
                    expanded=False
                ):
                    self._render_single_reference(ref, i)
    
    def _render_single_reference(self, ref: Dict, index: int):
        """단일 참조 정보 렌더링"""
        import time
        # OCR 텍스트 표시
        st.subheader("📄 OCR 추출 텍스트")
        if ref.get('ocr_text'):
            # 타임스탬프와 메시지 인덱스를 포함한 고유 키 생성
            unique_key = f"ref_text_{st.session_state.session_id}_{len(st.session_state.messages)}_{index}_{int(time.time() * 1000)}"
            st.text_area(
                "원문 내용", 
                ref['ocr_text'], 
                height=300, 
                key=unique_key,
                help="PDF에서 OCR로 추출된 원문 텍스트입니다."
            )
        else:
            st.info("텍스트 정보가 없습니다.")
        
        # 페이지 이미지 표시
        image_uri = ref.get('image_uri', '')
        if image_uri and image_uri.startswith('s3://'):
            with st.expander("🖼️ 페이지 이미지", expanded=False):
                # 단일 이미지 표시
                image_data = self._get_s3_image(image_uri)
                
                if image_data:
                    try:
                        st.image(
                            image_data, 
                            caption=f"{ref.get('source_file', 'Unknown')} - 페이지 {ref.get('page_number', '?')}", 
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"이미지 표시 실패: {e}")
                else:
                    st.warning("이미지를 로드할 수 없습니다.")
        
        # 메타데이터 정보
        st.markdown("**📋 문서 정보**")
        st.json({
            "파일명": ref.get('source_file', 'Unknown'),
            "페이지": ref.get('page_number', 1),
            "텍스트 길이": f"{len(ref.get('ocr_text', ''))} 문자"
        })
    
    def _get_s3_image(self, s3_uri: str) -> bytes:
        """S3에서 단일 이미지 다운로드"""
        try:
            if s3_uri.startswith('s3://'):
                parts = s3_uri[5:].split('/', 1)
                bucket = parts[0]
                key = parts[1] if len(parts) > 1 else ''
                
                response = self.s3_client.get_object(Bucket=bucket, Key=key)
                return response['Body'].read()
        except Exception as e:
            return None
        
        return None
    
    def _get_s3_images_from_directory(self, s3_dir_uri: str) -> list:
        """디렉토리에서 이미지 목록 가져오기"""
        try:
            if s3_dir_uri.startswith('s3://'):
                parts = s3_dir_uri[5:].split('/', 1)
                bucket = parts[0]
                prefix = parts[1] if len(parts) > 1 else ''
                
                response = self.s3_client.list_objects_v2(
                    Bucket=bucket, 
                    Prefix=prefix,
                    MaxKeys=10
                )
                
                images = []
                for obj in response.get('Contents', []):
                    key = obj['Key']
                    if key.lower().endswith(('.png', '.jpg', '.jpeg')):
                        try:
                            img_response = self.s3_client.get_object(Bucket=bucket, Key=key)
                            img_data = img_response['Body'].read()
                            images.append((key, img_data))
                        except:
                            continue
                
                return images
        except Exception as e:
            st.error(f"S3 디렉토리 이미지 로드 실패: {e}")
        
        return []
    
    def _render_simple_references(self, references: List[Dict]):
        """간단한 참조 정보 렌더링 (Plan-Execute Agent용)"""
        for i, ref in enumerate(references, 1):
            with st.expander(
                f"[{i}] {ref.get('source', 'Unknown')} (점수: {ref.get('score', 0):.3f})", 
                expanded=False
            ):
                st.markdown("**📝 문서 내용**")
                import time
                unique_key = f"simple_ref_{st.session_state.session_id}_{len(st.session_state.messages)}_{i}_{int(time.time() * 1000)}"
                st.text_area(
                    "추출된 내용", 
                    ref.get('content', ''), 
                    height=200, 
                    key=unique_key,
                    help="Knowledge Base에서 검색된 문서 내용입니다."
                )
                
                st.markdown("**📊 메타데이터**")
                st.json({
                    "출처": ref.get('source', 'Unknown'),
                    "점수": ref.get('score', 0),
                    "Rerank 점수": ref.get('rerank_score', '없음'),
                    "내용 길이": f"{len(ref.get('content', ''))} 문자"
                })