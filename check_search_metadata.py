#!/usr/bin/env python3
"""
검색 결과의 메타데이터 상세 분석
"""
import sys
import boto3
import json
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def check_search_metadata():
    print("🔍 검색 결과 메타데이터 상세 분석...")
    
    try:
        bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        kb_id = "CDPB5AI6BH"
        
        # 원본 API 응답 확인
        response = bedrock_client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': 'fire extinguisher'},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 3
                }
            }
        )
        
        print(f"검색 결과: {len(response['retrievalResults'])}개")
        
        for i, result in enumerate(response['retrievalResults'], 1):
            print(f"\n=== 결과 {i} ===")
            print(f"점수: {result.get('score', 0):.3f}")
            
            # content 구조 확인
            content = result.get('content', {})
            print(f"Content 키들: {list(content.keys())}")
            print(f"Text 내용: '{content.get('text', '')}'")
            print(f"Text 길이: {len(content.get('text', ''))}")
            
            # metadata 구조 확인
            metadata = result.get('metadata', {})
            print(f"Metadata 키들: {list(metadata.keys())}")
            
            for key, value in metadata.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
            
            # location 정보 확인
            location = result.get('location', {})
            if location:
                print(f"Location: {location}")
        
        # 벡터 검색이 어떤 기준으로 작동하는지 확인
        print(f"\n=== 벡터 검색 분석 ===")
        print("가능한 검색 기준:")
        print("1. 파일명/경로 기반 매칭")
        print("2. 메타데이터 기반 매칭") 
        print("3. 빈 텍스트의 임베딩 벡터")
        print("4. 문서 구조/제목 정보")
        
        return True
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return False

if __name__ == "__main__":
    success = check_search_metadata()
    exit(0 if success else 1)