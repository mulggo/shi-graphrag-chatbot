import streamlit as st
import boto3
import json
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# 페이지 설정
st.set_page_config(
    page_title="선박 Firefighting 규칙 챗봇",
    page_icon="🚢",
    layout="wide"
)

# 제목
st.title("🚢 선박 Firefighting 규칙 챗봇")
st.markdown("선박 설계시 firefighting 관련 규칙을 문의하세요")

# AWS 클라이언트 초기화
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-agent-runtime', region_name='us-west-2')

@st.cache_resource
def get_s3_client():
    return boto3.client('s3', region_name='us-west-2')

client = get_bedrock_client()
s3_client = get_s3_client()

# S3 이미지 다운로드 함수
def get_s3_image(s3_uri):
    try:
        # S3 URI 파싱 (s3://bucket/key)
        if s3_uri.startswith('s3://'):
            parts = s3_uri[5:].split('/', 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ''
            
            # S3에서 이미지 다운로드
            response = s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
    except Exception as e:
        st.error(f"S3 이미지 로드 실패: {e}")
        return None
    return None

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "references" in message:
            # 참조 정보가 있는 어시스턴트 메시지
            references = message["references"]
            if references:
                enhanced_content = message["content"]
                for i, ref in enumerate(references, 1):
                    if 'SOLAS' in ref['source_file']:
                        enhanced_content = enhanced_content.replace(
                            'SOLAS', f'SOLAS[[{i}]](#ref-{i}-hist)', 1
                        )
                st.markdown(enhanced_content)
                
                # 참조 정보 간략 표시
                if len(references) > 0:
                    ref_summary = ", ".join([f"[{i}] {ref['source_file']}" for i, ref in enumerate(references, 1)])
                    st.caption(f"📚 참조: {ref_summary}")
            else:
                st.markdown(message["content"])
        else:
            st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("선박 firefighting 규칙에 대해 질문하세요"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Agent 응답
    with st.chat_message("assistant"):
        with st.spinner("답변을 생성하고 있습니다..."):
            try:
                response = client.invoke_agent(
                    agentId='H5YNZKKNSW',
                    agentAliasId='FD3LV7TEN4',
                    sessionId=st.session_state.session_id,
                    inputText=prompt,
                    enableTrace=True
                )
                
                completion = ""
                references = []
                
                for event in response.get("completion", []):
                    if 'chunk' in event:
                        chunk = event["chunk"]
                        completion += chunk["bytes"].decode()
                    
                    # 참조 정보 추출
                    if 'trace' in event:
                        trace_event = event.get("trace")
                        if 'trace' in trace_event:
                            trace_data = trace_event['trace']
                            if 'orchestrationTrace' in trace_data:
                                orch_trace = trace_data['orchestrationTrace']
                                if 'observation' in orch_trace:
                                    obs = orch_trace['observation']
                                    if 'knowledgeBaseLookupOutput' in obs:
                                        kb_lookup = obs['knowledgeBaseLookupOutput']
                                        if 'retrievedReferences' in kb_lookup:
                                            refs = kb_lookup['retrievedReferences']
                                            for ref in refs:
                                                ref_data = {
                                                    'source_file': ref.get('metadata', {}).get('x-amz-bedrock-kb-source-uri', '').split('/')[-1],
                                                    'page_number': ref.get('metadata', {}).get('x-amz-bedrock-kb-document-page-number', 0),
                                                    'ocr_text': ref.get('metadata', {}).get('x-amz-bedrock-kb-description', ''),
                                                    'image_uri': ref.get('metadata', {}).get('x-amz-bedrock-kb-byte-content-source', '')
                                                }
                                                # 빈 참조 필터링: OCR 텍스트가 있고 페이지 번호가 0이 아닌 경우만 추가
                                                if ref_data['ocr_text'] and ref_data['page_number'] > 0:
                                                    references.append(ref_data)
                
                # 기본 응답 표시
                st.markdown(completion)
                
                # 참조 정보 표시
                if references:
                    st.markdown("---")
                    st.markdown("**📚 참조 문서**")
                    
                    for i, ref in enumerate(references, 1):
                        with st.expander(f"[{i}] {ref['source_file']} (페이지 {ref['page_number']})", expanded=False):
                            # OCR 텍스트 표시
                            st.subheader("📄 OCR 추출 텍스트")
                            if ref['ocr_text']:
                                st.text_area(
                                    "원문 내용", 
                                    ref['ocr_text'], 
                                    height=300, 
                                    key=f"ref_text_{i}",
                                    help="PDF에서 OCR로 추출된 원문 텍스트입니다."
                                )
                            else:
                                st.info("텍스트 정보가 없습니다.")
                            
                            # 이미지 표시
                            st.subheader("🖼️ 원본 이미지")
                            if ref['image_uri']:
                                try:
                                    image_data = get_s3_image(ref['image_uri'])
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
                                "파일명": ref['source_file'],
                                "페이지": ref['page_number'],
                                "텍스트 길이": f"{len(ref['ocr_text'])} 문자"
                            })
                
                # 응답을 세션에 저장 (참조 정보 포함)
                response_with_refs = {
                    "role": "assistant", 
                    "content": completion,
                    "references": references if references else []
                }
                st.session_state.messages.append(response_with_refs)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

# 사이드바에 정보 표시
with st.sidebar:
    st.markdown("### 📋 사용 정보")
    st.markdown(f"**세션 ID:** `{st.session_state.session_id[:8]}...`")
    st.markdown(f"**메시지 수:** {len(st.session_state.messages)}")
    
    if st.button("새 세션 시작"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🚢 지원 주제")
    st.markdown("""
    - 고정식 소화 시스템
    - 휴대용 소화기
    - 배수 시스템
    - 안전 구역
    - SOLAS 규정
    """)
    
    # st.markdown("---")
    # st.markdown("### 🔗 참조 기능")
    # st.markdown("""
    # - 답변에 [[1]], [[2]] 번호 표시
    # - 번호 클릭시 참조 문서로 이동
    # - OCR 추출 원문 텍스트 제공
    # - S3 원본 이미지 위치 정보
    # """)