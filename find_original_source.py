#!/usr/bin/env python3
"""
PWRU19RDNE KB의 원본 소스 파일 찾기
KB 생성 전 업로드된 원본 PDF/이미지 파일들
"""

import boto3
import json

def find_kb_data_source():
    """KB 데이터 소스 정보 조회"""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
    kb_id = 'PWRU19RDNE'
    
    try:
        # KB 정보 조회
        kb_response = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        kb_info = kb_response['knowledgeBase']
        
        print(f"📚 KB 정보: {kb_info['name']}")
        print(f"📝 설명: {kb_info.get('description', 'N/A')}")
        
        # 데이터 소스 조회
        ds_response = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        
        print(f"\n📁 데이터 소스 ({len(ds_response['dataSourceSummaries'])}개):")
        
        for ds in ds_response['dataSourceSummaries']:
            ds_id = ds['dataSourceId']
            ds_name = ds['name']
            
            print(f"\n🔍 데이터 소스: {ds_name} ({ds_id})")
            
            # 상세 정보 조회
            ds_detail = bedrock_agent.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=ds_id
            )
            
            data_source_config = ds_detail['dataSource']['dataSourceConfiguration']
            s3_config = data_source_config.get('s3Configuration', {})
            
            if s3_config:
                bucket_arn = s3_config.get('bucketArn', '')
                inclusion_prefixes = s3_config.get('inclusionPrefixes', [])
                
                print(f"   📦 S3 버킷: {bucket_arn}")
                print(f"   📂 포함 경로: {inclusion_prefixes}")
                
                # 버킷명 추출
                bucket_name = bucket_arn.split(':')[-1] if bucket_arn else ''
                return bucket_name, inclusion_prefixes
        
        return None, []
        
    except Exception as e:
        print(f"❌ KB 정보 조회 실패: {e}")
        return None, []

def scan_original_source_files(bucket_name: str, prefixes: list):
    """원본 소스 파일 스캔"""
    
    if not bucket_name:
        print("❌ 버킷 정보가 없습니다.")
        return
    
    s3_client = boto3.client('s3', region_name='us-west-2')
    
    print(f"\n🔍 원본 소스 파일 스캔: s3://{bucket_name}")
    
    try:
        all_files = []
        
        for prefix in prefixes or ['']:
            print(f"\n📂 경로: {prefix}")
            
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=100
            )
            
            files = response.get('Contents', [])
            print(f"   파일 수: {len(files)}개")
            
            # 파일 타입별 분류
            file_types = {}
            sample_files = []
            
            for obj in files:
                key = obj['Key']
                size = obj['Size']
                
                # 확장자 추출
                if '.' in key:
                    ext = key.split('.')[-1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                
                # 샘플 수집
                if len(sample_files) < 5:
                    sample_files.append({
                        'key': key,
                        'size_mb': round(size / 1024 / 1024, 2),
                        'modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M')
                    })
            
            # 파일 타입 분포
            print(f"   📊 파일 타입:")
            for ext, count in sorted(file_types.items()):
                print(f"      .{ext}: {count}개")
            
            # 샘플 파일들
            print(f"   📄 샘플 파일:")
            for file_info in sample_files:
                print(f"      {file_info['key']} ({file_info['size_mb']} MB, {file_info['modified']})")
            
            all_files.extend(files)
        
        return all_files
        
    except Exception as e:
        print(f"❌ 파일 스캔 실패: {e}")
        return []

def check_original_file_structure(files: list):
    """원본 파일 구조 분석"""
    
    print(f"\n📋 원본 파일 구조 분석:")
    
    # PDF 파일들 찾기
    pdf_files = [f for f in files if f['Key'].lower().endswith('.pdf')]
    image_files = [f for f in files if any(f['Key'].lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])]
    
    print(f"📚 PDF 파일: {len(pdf_files)}개")
    print(f"🖼️  이미지 파일: {len(image_files)}개")
    
    # PDF 파일명 패턴 분석
    if pdf_files:
        print(f"\n📚 PDF 파일들:")
        for pdf in pdf_files[:10]:  # 처음 10개만
            key = pdf['Key']
            size_mb = round(pdf['Size'] / 1024 / 1024, 2)
            print(f"   {key} ({size_mb} MB)")
    
    return pdf_files, image_files

if __name__ == "__main__":
    print("🔍 PWRU19RDNE KB 원본 소스 찾기\n")
    
    # 1. KB 데이터 소스 정보 조회
    bucket_name, prefixes = find_kb_data_source()
    
    if bucket_name:
        # 2. 원본 파일 스캔
        files = scan_original_source_files(bucket_name, prefixes)
        
        if files:
            # 3. 파일 구조 분석
            pdf_files, image_files = check_original_file_structure(files)
            
            print(f"\n💡 결론:")
            print(f"   - 원본 소스 버킷: s3://{bucket_name}")
            print(f"   - PDF 파일: {len(pdf_files)}개 (페이지별 OCR 추출 가능)")
            print(f"   - 이미지 파일: {len(image_files)}개")
        else:
            print("❌ 파일을 찾을 수 없습니다.")
    else:
        print("❌ KB 데이터 소스를 찾을 수 없습니다.")