#!/usr/bin/env python3
"""
PWRU19RDNE Knowledge Base 검색 테스트
"""

import boto3
import json
from botocore.exceptions import ClientError

def test_pwru19rdne_search():
    """PWRU19RDNE KB에서 멀티모달 검색 테스트"""
    try:
        bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        print("🔍 PWRU19RDNE Knowledge Base 검색 테스트...")
        
        # 검색 실행
        response = bedrock_client.retrieve(
            knowledgeBaseId='PWRU19RDNE',
            retrievalQuery={'text': 'fire extinguisher'},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5
                }
            }
        )
        
        results = response['retrievalResults']
        print(f"✅ 검색 성공: {len(results)}개 결과")
        
        # 결과 분석
        for i, result in enumerate(results):
            print(f"\n--- 결과 {i+1} ---")
            
            # 기본 정보
            content = result.get('content', {}).get('text', '')
            score = result.get('score', 0.0)
            print(f"점수: {score:.3f}")
            print(f"내용: {content[:100]}...")
            
            # 메타데이터 분석
            metadata = result.get('metadata', {})
            print(f"메타데이터 키들: {list(metadata.keys())}")
            
            # 이미지 관련 정보 찾기
            for key, value in metadata.items():
                if 'image' in key.lower() or 'uri' in key.lower() or 'source' in key.lower():
                    print(f"  {key}: {value}")
        
        return True, results
        
    except ClientError as e:
        print(f"❌ 검색 실패: {e.response['Error']['Code']}")
        return False, []
    except Exception as e:
        print(f"❌ 예상치 못한 에러: {e}")
        return False, []

def main():
    print("=" * 50)
    print("🚢 PWRU19RDNE Knowledge Base 테스트")
    print("=" * 50)
    
    success, results = test_pwru19rdne_search()
    
    if success and results:
        print(f"\n🎯 멀티모달 데이터 발견: {len(results)}개")
        print("✅ Plan-Execute Agent에서 이 데이터를 사용할 수 있습니다!")
    else:
        print("\n❌ 검색 실패 - 멀티모달 기능 사용 불가")

if __name__ == "__main__":
    main()