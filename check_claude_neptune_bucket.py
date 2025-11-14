#!/usr/bin/env python3
"""
claude-neptune 버킷의 실제 파일 구조와 내용 확인
"""

import boto3
import json

def check_bucket_structure():
    """claude-neptune 버킷 구조 분석"""
    
    s3_client = boto3.client('s3', region_name='us-west-2')
    bucket_name = 'claude-neptune'
    
    try:
        print(f"🔍 {bucket_name} 버킷 분석 중...")
        
        # 전체 객체 리스트 조회
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=50  # 처음 50개만
        )
        
        if 'Contents' not in response:
            print("❌ 버킷이 비어있거나 접근할 수 없습니다.")
            return
        
        print(f"📁 총 객체 수: {response.get('KeyCount', 0)}개")
        print("\n📋 파일 구조 분석:")
        
        file_types = {}
        sample_files = []
        
        for obj in response['Contents']:
            key = obj['Key']
            size = obj['Size']
            
            # 파일 확장자별 분류
            if '.' in key:
                ext = key.split('.')[-1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            
            # 샘플 파일 수집
            if len(sample_files) < 10:
                sample_files.append({
                    'key': key,
                    'size': size,
                    'size_mb': round(size / 1024 / 1024, 2)
                })
        
        # 파일 타입 분석
        print("\n📊 파일 타입별 분포:")
        for ext, count in sorted(file_types.items()):
            print(f"  .{ext}: {count}개")
        
        # 샘플 파일들
        print(f"\n📄 샘플 파일들 (처음 10개):")
        for file_info in sample_files:
            print(f"  {file_info['key']} ({file_info['size_mb']} MB)")
        
        # 파일명 패턴 분석
        print(f"\n🔍 파일명 패턴 분석:")
        analyze_filename_patterns(sample_files)
        
        return sample_files
        
    except Exception as e:
        print(f"❌ 버킷 분석 실패: {e}")
        return []

def analyze_filename_patterns(files):
    """파일명 패턴 분석"""
    
    patterns = {
        'page_number': 0,
        'document_id': 0,
        'date_format': 0,
        'uuid_like': 0,
        'other': 0
    }
    
    import re
    
    for file_info in files:
        key = file_info['key']
        
        # 페이지 번호 패턴
        if re.search(r'page[-_]?\d+|p\d+|\d+\.', key, re.IGNORECASE):
            patterns['page_number'] += 1
            print(f"    📄 페이지 패턴: {key}")
        
        # 문서 ID 패턴
        elif re.search(r'[a-zA-Z]+[-_][a-zA-Z0-9]+', key):
            patterns['document_id'] += 1
            print(f"    📚 문서 ID 패턴: {key}")
        
        # 날짜 패턴
        elif re.search(r'\d{4}[-_]\d{2}[-_]\d{2}', key):
            patterns['date_format'] += 1
            print(f"    📅 날짜 패턴: {key}")
        
        # UUID 패턴
        elif re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', key):
            patterns['uuid_like'] += 1
            print(f"    🔑 UUID 패턴: {key}")
        
        else:
            patterns['other'] += 1
            print(f"    ❓ 기타 패턴: {key}")

def check_sample_file_content():
    """샘플 파일의 실제 내용 확인"""
    
    s3_client = boto3.client('s3', region_name='us-west-2')
    bucket_name = 'claude-neptune'
    
    try:
        # 첫 번째 이미지 파일 찾기
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=20
        )
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        sample_key = None
        
        for obj in response.get('Contents', []):
            key = obj['Key']
            if any(key.lower().endswith(ext) for ext in image_extensions):
                sample_key = key
                break
        
        if not sample_key:
            print("❌ 이미지 파일을 찾을 수 없습니다.")
            return
        
        print(f"\n🖼️  샘플 파일 메타데이터 확인: {sample_key}")
        
        # 객체 메타데이터 조회
        metadata_response = s3_client.head_object(
            Bucket=bucket_name,
            Key=sample_key
        )
        
        print("📋 S3 메타데이터:")
        metadata = metadata_response.get('Metadata', {})
        if metadata:
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        else:
            print("  메타데이터 없음")
        
        print(f"📏 파일 크기: {metadata_response['ContentLength']} bytes")
        print(f"📅 수정일: {metadata_response['LastModified']}")
        
    except Exception as e:
        print(f"❌ 샘플 파일 확인 실패: {e}")

if __name__ == "__main__":
    print("🚀 claude-neptune 버킷 분석 시작\n")
    
    # 1. 버킷 구조 확인
    sample_files = check_bucket_structure()
    
    # 2. 샘플 파일 내용 확인
    if sample_files:
        check_sample_file_content()
    
    print("\n✅ 분석 완료")
    print("\n💡 결론:")
    print("1. 파일명 패턴으로 document_id/page_number 추출 가능 여부 확인")
    print("2. 실제 이미지가 페이지 OCR용인지 확인")
    print("3. 메타데이터에 추가 정보가 있는지 확인")