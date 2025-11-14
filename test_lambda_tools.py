"""
Lambda 함수 직접 호출 테스트 (Strands 없이)
"""
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_lambda_functions():
    """Lambda 함수들이 재배포 후 정상 작동하는지 테스트"""
    
    print("=" * 80)
    print("Lambda 함수 재배포 후 테스트")
    print("=" * 80)
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    
    # 1. extract_entities 테스트
    print("\n[1] extract_entities Lambda 테스트...")
    try:
        response = lambda_client.invoke(
            FunctionName='graphrag-extract-entities',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'question': '고정식 CO2 소화 시스템의 최소 용량은?'
            })
        )
        
        result = json.loads(response['Payload'].read())
        if 'errorMessage' in result:
            print(f"✗ 실패: {result['errorMessage']}")
        else:
            print(f"✓ 성공: entities={len(result.get('entities', []))}, keywords={len(result.get('keywords_ko', []))}")
            
    except Exception as e:
        print(f"✗ 호출 실패: {e}")
    
    # 2. kb_retrieve 테스트  
    print("\n[2] kb_retrieve Lambda 테스트...")
    try:
        response = lambda_client.invoke(
            FunctionName='graphrag-kb-retrieve',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'query': 'fixed CO2 system minimum capacity',
                'num_results': 5,
                'kb_id': 'CDPB5AI6BH'
            })
        )
        
        result = json.loads(response['Payload'].read())
        if 'errorMessage' in result:
            print(f"✗ 실패: {result['errorMessage']}")
        else:
            print(f"✓ 성공: retrieved={result.get('total_retrieved', 0)}, reranked={result.get('reranked', False)}")
            
    except Exception as e:
        print(f"✗ 호출 실패: {e}")
    
    print("\n" + "=" * 80)
    print("Lambda 함수 테스트 완료")
    print("=" * 80)

if __name__ == "__main__":
    test_lambda_functions()