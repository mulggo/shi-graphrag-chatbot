#!/usr/bin/env python3
"""
S3 claude-neptune 버킷 이미지 정보 확인 테스트
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import json

def test_s3_access():
    """S3 버킷 접근 테스트"""
    try:
        s3_client = boto3.client('s3', region_name='us-west-2')
        
        # 버킷 존재 확인
        print("🔍 S3 버킷 접근 테스트...")
        response = s3_client.list_objects_v2(
            Bucket='claude-neptune',
            MaxKeys=10
        )
        
        objects = response.get('Contents', [])
        print(f"✅ 버킷 접근 성공: {len(objects)}개 객체 발견")
        
        # 이미지 파일 찾기
        image_files = []
        for obj in objects:
            key = obj['Key']
            if any(key.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']):
                image_files.append({
                    'key': key,
                    'size': obj['Size'],
                    'modified': obj['LastModified'].isoformat()
                })
        
        print(f"\n📸 이미지 파일: {len(image_files)}개")
        for img in image_files[:5]:  # 최대 5개만 표시
            print(f"  - {img['key']} ({img['size']} bytes)")
        
        return True, image_files
        
    except NoCredentialsError:
        print("❌ AWS 자격증명이 설정되지 않음")
        return False, []
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print("❌ 버킷이 존재하지 않음")
        elif error_code == 'AccessDenied':
            print("❌ 버킷 접근 권한 없음")
        else:
            print(f"❌ S3 에러: {error_code}")
        return False, []
    except Exception as e:
        print(f"❌ 예상치 못한 에러: {e}")
        return False, []

def test_bedrock_agent_multimodal():
    """Bedrock Agent 멀티모달 설정 확인"""
    try:
        bedrock_client = boto3.client('bedrock-agent', region_name='us-west-2')
        
        print("\n🤖 Bedrock Agent 설정 확인...")
        agent_info = bedrock_client.get_agent(agentId='PWRU19RDNE')
        
        agent = agent_info['agent']
        print(f"✅ Agent 이름: {agent.get('agentName', 'Unknown')}")
        print(f"✅ Agent 상태: {agent.get('agentStatus', 'Unknown')}")
        
        # 멀티모달 설정 확인
        if 'foundationModel' in agent:
            print(f"✅ 기본 모델: {agent['foundationModel']}")
        
        return True
        
    except ClientError as e:
        print(f"❌ Bedrock Agent 접근 실패: {e.response['Error']['Code']}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 에러: {e}")
        return False

def main():
    print("=" * 50)
    print("🚢 멀티모달 S3 버킷 테스트")
    print("=" * 50)
    
    # S3 접근 테스트
    s3_success, image_files = test_s3_access()
    
    # Bedrock Agent 테스트
    agent_success = test_bedrock_agent_multimodal()
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    print(f"S3 버킷 접근: {'✅ 성공' if s3_success else '❌ 실패'}")
    print(f"Bedrock Agent: {'✅ 성공' if agent_success else '❌ 실패'}")
    
    if s3_success and image_files:
        print(f"이미지 파일: {len(image_files)}개 발견")
        print("🎯 멀티모달 기능 테스트 준비 완료!")
    elif s3_success:
        print("⚠️  버킷 접근 가능하지만 이미지 파일 없음")
    else:
        print("❌ 멀티모달 기능 테스트 불가")

if __name__ == "__main__":
    main()