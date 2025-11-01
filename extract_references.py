#!/usr/bin/env python3
import boto3
import json
import uuid
import base64

def extract_references_from_agent():
    client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    session_id = str(uuid.uuid4())
    
    try:
        response = client.invoke_agent(
            agentId='H5YNZKKNSW',
            agentAliasId='FD3LV7TEN4',
            sessionId=session_id,
            inputText='선박 설계시 firefighting 규칙에 대해 알려주세요',
            enableTrace=True
        )
        
        completion = ""
        references = []
        
        for event in response.get("completion", []):
            if 'chunk' in event:
                chunk = event["chunk"]
                completion += chunk["bytes"].decode()
            
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
                                        # content 구조 확인
                                        content_text = ""
                                        if 'content' in ref:
                                            content = ref['content']
                                            if 'text' in content:
                                                content_text = content['text']
                                            elif 'byteContent' in content:
                                                # byteContent 처리
                                                try:
                                                    byte_data = content['byteContent']
                                                    if isinstance(byte_data, str):
                                                        content_text = base64.b64decode(byte_data).decode('utf-8')
                                                    else:
                                                        content_text = byte_data.decode('utf-8') if hasattr(byte_data, 'decode') else str(byte_data)
                                                except Exception as e:
                                                    print(f"ByteContent decode error: {e}")
                                                    content_text = f"[Binary content - type: {content.get('type', 'unknown')}]"
                                            else:
                                                print(f"Content keys: {list(content.keys())}")
                                        
                                        ref_data = {
                                            'content': content_text,
                                            'source_file': ref.get('metadata', {}).get('x-amz-bedrock-kb-source-uri', ''),
                                            'page_number': ref.get('metadata', {}).get('x-amz-bedrock-kb-document-page-number', 0),
                                            'description': ref.get('metadata', {}).get('x-amz-bedrock-kb-description', '')
                                        }
                                        references.append(ref_data)
        
        print("=== AGENT RESPONSE ===")
        print(completion)
        
        print(f"\n=== EXTRACTED REFERENCES ({len(references)}) ===")
        for i, ref in enumerate(references, 1):
            print(f"\n[{i}] 참조 문서:")
            print(f"파일: {ref['source_file'].split('/')[-1]}")
            print(f"페이지: {ref['page_number']}")
            if ref['content']:
                print(f"참조 텍스트 (처음 500자):")
                print(f"{ref['content'][:500]}...")
                print(f"총 길이: {len(ref['content'])} 문자")
            else:
                print("참조 텍스트: 비어있음")
            print("-" * 50)
        
        return completion, references
        
    except Exception as e:
        print(f"Error: {e}")
        return "", []

if __name__ == "__main__":
    response, refs = extract_references_from_agent()