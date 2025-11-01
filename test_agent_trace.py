#!/usr/bin/env python3
import boto3
import json
import uuid

def test_agent_with_trace():
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
        
        print("=== AGENT RESPONSE ===")
        completion = ""
        traces = []
        
        for event in response.get("completion", []):
            if 'chunk' in event:
                chunk = event["chunk"]
                completion += chunk["bytes"].decode()
            
            if 'trace' in event:
                trace_event = event.get("trace")
                traces.append(trace_event)
                print(f"\n--- TRACE EVENT ---")
                print(f"Trace keys: {list(trace_event.keys())}")
                if 'trace' in trace_event:
                    trace_data = trace_event['trace']
                    print(f"Trace data keys: {list(trace_data.keys())}")
                    
                    if 'orchestrationTrace' in trace_data:
                        orch_trace = trace_data['orchestrationTrace']
                        print(f"Orchestration trace keys: {list(orch_trace.keys())}")
                        
                        # observation 내부 확인
                        if 'observation' in orch_trace:
                            obs = orch_trace['observation']
                            print(f"Observation keys: {list(obs.keys())}")
                            
                            # knowledgeBaseLookupOutput 확인
                            if 'knowledgeBaseLookupOutput' in obs:
                                kb_lookup = obs['knowledgeBaseLookupOutput']
                                print(f"*** KB Lookup Output keys: {list(kb_lookup.keys())} ***")
                                if 'retrievedReferences' in kb_lookup:
                                    refs = kb_lookup['retrievedReferences']
                                    print(f"*** Found {len(refs)} references in KB lookup ***")
                                    for i, ref in enumerate(refs[:2]):
                                        print(f"\n--- Reference {i+1} ---")
                                        print(f"Keys: {list(ref.keys())}")
                                        if 'content' in ref and 'text' in ref['content']:
                                            text = ref['content']['text'][:150] + "..."
                                            print(f"Text: {text}")
                                        if 'location' in ref:
                                            location = ref['location']
                                            print(f"Location keys: {list(location.keys())}")
                                            if 's3Location' in location:
                                                s3_loc = location['s3Location']
                                                print(f"S3 Location: {s3_loc}")
                                        if 'metadata' in ref:
                                            metadata = ref['metadata']
                                            print(f"Metadata: {metadata}")
                            
                            if 'knowledgeBaseRetrievalResult' in obs:
                                kb_result = obs['knowledgeBaseRetrievalResult']
                                print(f"*** KB Result in observation keys: {list(kb_result.keys())} ***")
                                if 'retrievedReferences' in kb_result:
                                    refs = kb_result['retrievedReferences']
                                    print(f"*** Found {len(refs)} references in observation ***")
                                    for i, ref in enumerate(refs[:1]):
                                        print(f"Ref {i+1} keys: {list(ref.keys())}")
                                        if 'content' in ref and 'text' in ref['content']:
                                            text = ref['content']['text'][:100] + "..."
                                            print(f"Text: {text}")
                                        if 'location' in ref:
                                            print(f"Location: {ref['location']}")
                        
                        # Knowledge Base 관련 정보 찾기
                        if 'knowledgeBaseRetrievalResult' in orch_trace:
                            kb_result = orch_trace['knowledgeBaseRetrievalResult']
                            print(f"KB Retrieval Result keys: {list(kb_result.keys())}")
                            
                            if 'retrievedReferences' in kb_result:
                                refs = kb_result['retrievedReferences']
                                print(f"Found {len(refs)} references")
                                for i, ref in enumerate(refs[:2]):  # 처음 2개만 출력
                                    print(f"Reference {i+1} keys: {list(ref.keys())}")
                                    if 'content' in ref:
                                        content = ref['content']
                                        print(f"Content keys: {list(content.keys())}")
                                        if 'text' in content:
                                            text = content['text'][:200] + "..." if len(content['text']) > 200 else content['text']
                                            print(f"Text preview: {text}")
                                    if 'location' in ref:
                                        location = ref['location']
                                        print(f"Location keys: {list(location.keys())}")
        
        print(f"\n=== FINAL RESPONSE ===")
        print(completion)
        
        print(f"\n=== TRACE SUMMARY ===")
        print(f"Total trace events: {len(traces)}")
        
        # Knowledge Base 관련 trace 찾기
        kb_traces = []
        for trace in traces:
            if 'trace' in trace:
                trace_data = trace['trace']
                if 'orchestrationTrace' in trace_data:
                    orch_trace = trace_data['orchestrationTrace']
                    if 'knowledgeBaseRetrievalResult' in orch_trace:
                        kb_traces.append(orch_trace['knowledgeBaseRetrievalResult'])
                    if 'observation' in orch_trace:
                        obs = orch_trace['observation']
                        if 'knowledgeBaseRetrievalResult' in obs:
                            kb_traces.append(obs['knowledgeBaseRetrievalResult'])
                        if 'knowledgeBaseLookupOutput' in obs:
                            kb_traces.append(obs['knowledgeBaseLookupOutput'])
        
        print(f"\n=== KNOWLEDGE BASE RETRIEVAL SUMMARY ===")
        print(f"Found {len(kb_traces)} KB retrieval events")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_agent_with_trace()