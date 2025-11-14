#!/usr/bin/env python3
"""
처리 실패한 문서들 상세 분석
"""
import boto3

def check_failed_documents():
    print("🔍 처리 실패 문서 상세 분석...")
    
    try:
        s3 = boto3.client('s3')
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        bucket_name = 'shi-kb-bucket'
        kb_id = "ZGBA1R5CS0"
        
        # 각 데이터 소스별 S3 파일과 처리 결과 비교
        data_source_configs = [
            {"name": "dnv-ru", "prefix": "documents/dnv-ru/", "id": "21W9PJ3VJR"},
            {"name": "design-guidances", "prefix": "documents/design/", "id": "DUATA0SRUU"},
            {"name": "fss-solas-igc", "prefix": "documents/fss-solas-igc/", "id": "HMXCQNXT1V"},
            {"name": "pipes", "prefix": "documents/pipes/", "id": "VDXB3NKJ0O"}
        ]
        
        for config in data_source_configs:
            print(f"\n=== {config['name']} 분석 ===")
            
            # S3 파일 목록
            try:
                response = s3.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=config['prefix']
                )
                
                if 'Contents' in response:
                    s3_files = [obj for obj in response['Contents'] if not obj['Key'].endswith('/')]
                    print(f"S3 파일 수: {len(s3_files)}개")
                    
                    for i, obj in enumerate(s3_files, 1):
                        size_mb = obj['Size'] / (1024 * 1024)
                        print(f"  {i}. {obj['Key'].split('/')[-1]} ({size_mb:.2f}MB)")
                        
                        # 파일 크기 체크
                        if size_mb > 50:
                            print(f"     ⚠️ 대용량 파일 (>50MB)")
                        elif size_mb < 0.1:
                            print(f"     ⚠️ 소용량 파일 (<0.1MB)")
                else:
                    s3_files = []
                    print("S3 파일 없음")
                
            except Exception as e:
                print(f"S3 파일 확인 실패: {e}")
                continue
            
            # 동기화 작업 결과
            try:
                ingestion_jobs = bedrock_agent.list_ingestion_jobs(
                    knowledgeBaseId=kb_id,
                    dataSourceId=config['id'],
                    maxResults=1
                )
                
                if ingestion_jobs['ingestionJobSummaries']:
                    latest_job = ingestion_jobs['ingestionJobSummaries'][0]
                    job_id = latest_job['ingestionJobId']
                    
                    job_detail = bedrock_agent.get_ingestion_job(
                        knowledgeBaseId=kb_id,
                        dataSourceId=config['id'],
                        ingestionJobId=job_id
                    )
                    
                    stats = job_detail['ingestionJob'].get('statistics', {})
                    
                    scanned = stats.get('numberOfDocumentsScanned', 0)
                    processed = stats.get('numberOfNewDocumentsIndexed', 0)
                    failed = stats.get('numberOfDocumentsFailed', 0)
                    
                    print(f"동기화 결과:")
                    print(f"  - 스캔: {scanned}개")
                    print(f"  - 처리: {processed}개") 
                    print(f"  - 실패: {failed}개")
                    
                    # 불일치 분석
                    s3_file_count = len(s3_files)
                    if scanned != s3_file_count:
                        print(f"  ⚠️ 스캔 불일치: S3({s3_file_count}) vs 스캔({scanned})")
                    
                    if processed < scanned:
                        missing = scanned - processed
                        print(f"  ❌ 처리 누락: {missing}개 문서가 처리되지 않음")
                        
                        # 가능한 원인 추정
                        print(f"  가능한 원인:")
                        print(f"    - PDF 파싱 실패")
                        print(f"    - 텍스트 추출 실패") 
                        print(f"    - 파일 형식 문제")
                        print(f"    - 권한 문제")
                
            except Exception as e:
                print(f"동기화 작업 확인 실패: {e}")
        
        # 전체 요약
        print(f"\n=== 전체 요약 ===")
        
        # 각 데이터 소스별 처리율 계산
        total_s3_files = 0
        total_processed = 0
        
        for config in data_source_configs:
            try:
                # S3 파일 수
                response = s3.list_objects_v2(Bucket=bucket_name, Prefix=config['prefix'])
                s3_count = len([obj for obj in response.get('Contents', []) if not obj['Key'].endswith('/')])
                
                # 처리된 문서 수
                ingestion_jobs = bedrock_agent.list_ingestion_jobs(
                    knowledgeBaseId=kb_id,
                    dataSourceId=config['id'],
                    maxResults=1
                )
                
                processed_count = 0
                if ingestion_jobs['ingestionJobSummaries']:
                    job_id = ingestion_jobs['ingestionJobSummaries'][0]['ingestionJobId']
                    job_detail = bedrock_agent.get_ingestion_job(
                        knowledgeBaseId=kb_id,
                        dataSourceId=config['id'],
                        ingestionJobId=job_id
                    )
                    processed_count = job_detail['ingestionJob'].get('statistics', {}).get('numberOfNewDocumentsIndexed', 0)
                
                total_s3_files += s3_count
                total_processed += processed_count
                
                if s3_count > 0:
                    success_rate = (processed_count / s3_count) * 100
                    print(f"{config['name']}: {processed_count}/{s3_count} ({success_rate:.1f}%)")
                
            except Exception as e:
                print(f"{config['name']}: 확인 실패 - {e}")
        
        overall_rate = (total_processed / total_s3_files) * 100 if total_s3_files > 0 else 0
        print(f"\n전체 처리율: {total_processed}/{total_s3_files} ({overall_rate:.1f}%)")
        
        if overall_rate < 80:
            print("❌ 처리율이 80% 미만으로 문제 있음")
        else:
            print("✅ 처리율 양호")
        
        return True
        
    except Exception as e:
        print(f"❌ 실패 문서 분석 실패: {e}")
        return False

if __name__ == "__main__":
    success = check_failed_documents()
    exit(0 if success else 1)