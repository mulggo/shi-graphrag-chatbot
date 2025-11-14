#!/usr/bin/env python3
"""
Plan-Execute Agent의 이미지 URI 설정 디버깅
"""

import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

from agents.plan_execute_agent.agent import PlanExecuteAgent

def debug_image_uri():
    """이미지 URI 설정 디버깅"""
    
    agent = PlanExecuteAgent(kb_id='PWRU19RDNE')
    
    # 테스트 질문
    result = agent.process_message("선박의 소화기 요구사항은?", "test_session")
    
    print("🔍 Plan-Execute Agent 이미지 URI 디버깅\n")
    
    references = result.get('references', [])
    
    for i, ref in enumerate(references):
        print(f"--- 참조 {i+1} ---")
        print(f"source_file: {ref.get('source_file', 'N/A')}")
        print(f"page_number: {ref.get('page_number', 'N/A')}")
        print(f"has_multimodal: {ref.get('has_multimodal', 'N/A')}")
        print(f"image_uri: {ref.get('image_uri', 'N/A')}")
        print(f"data_source_id: {ref.get('data_source_id', 'N/A')}")
        
        # 메타데이터 확인
        metadata = ref.get('metadata', {})
        print(f"metadata keys: {list(metadata.keys())}")
        print(f"x-amz-bedrock-kb-data-source-id: {metadata.get('x-amz-bedrock-kb-data-source-id', 'N/A')}")
        print()

if __name__ == "__main__":
    debug_image_uri()