"""
기본 에이전트 클래스
모든 에이전트가 상속받아 사용하는 공통 인터페이스와 기능 제공
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import boto3
import json
import uuid
from datetime import datetime

class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스"""
    
    def __init__(self, config):
        self.config = config
        self.name = config.name
        self.display_name = config.display_name
        self.description = config.description
        
        # AWS 클라이언트 초기화
        self.bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        self.s3_client = boto3.client('s3', region_name='us-west-2')
        
        # 에이전트별 설정
        self.agent_id = config.bedrock_agent_id
        self.alias_id = config.bedrock_alias_id
        self.knowledge_base_id = config.knowledge_base_id
        
    @abstractmethod
    def process_message(self, message: str, session_id: str) -> Dict:
        """
        메시지 처리 - 각 에이전트에서 구현해야 함
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID
            
        Returns:
            Dict: 처리 결과
        """
        pass
    
    def invoke_bedrock_agent(self, message: str, session_id: str) -> Dict:
        """AWS Bedrock Agent 호출"""
        try:
            response = self.bedrock_client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.alias_id,
                sessionId=session_id,
                inputText=message,
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
                    refs = self._extract_references(event['trace'])
                    references.extend(refs)
            
            return {
                "success": True,
                "content": completion,
                "references": references,
                "agent_name": self.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_name": self.name
            }
    
    def _extract_references(self, trace_event) -> List[Dict]:
        """트레이스에서 참조 정보 추출"""
        references = []
        
        try:
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
                                    # 유효한 참조만 추가
                                    if ref_data['ocr_text'] and ref_data['page_number'] > 0:
                                        references.append(ref_data)
        except Exception as e:
            print(f"참조 정보 추출 중 오류: {e}")
        
        return references
    
    def get_s3_image(self, s3_uri: str) -> Optional[bytes]:
        """S3에서 이미지 다운로드"""
        try:
            if s3_uri.startswith('s3://'):
                parts = s3_uri[5:].split('/', 1)
                bucket = parts[0]
                key = parts[1] if len(parts) > 1 else ''
                
                response = self.s3_client.get_object(Bucket=bucket, Key=key)
                return response['Body'].read()
        except Exception as e:
            print(f"S3 이미지 로드 실패: {e}")
        
        return None
    
    def log_interaction(self, message: str, response: Dict, session_id: str):
        """상호작용 로깅 (필요시 구현)"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "session_id": session_id,
            "message": message,
            "response_success": response.get("success", False),
            "response_length": len(response.get("content", ""))
        }
        # 로깅 구현 (CloudWatch, 파일 등)
        pass
    
    @property
    def ui_config(self) -> Dict:
        """UI 설정 반환"""
        return getattr(self.config, 'ui_config', {})
    
    def get_capabilities(self) -> List[str]:
        """에이전트 기능 목록 반환"""
        return [
            "문서 검색",
            "참조 정보 제공",
            "다국어 지원"
        ]