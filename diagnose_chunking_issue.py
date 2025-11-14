#!/usr/bin/env python3
"""
청킹 문제 진단: 왜 청크가 적게 생성되었나?
"""
import boto3

def diagnose_chunking_issue():
    print("🔍 청킹 문제 진단...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        kb_id = "ZGBA1R5CS0"
        
        # 각 데이터 소스별 최근 동기화 작업 상세 분석
        data_sources = [
            {"name": "dnv-ru", "id": "21W9PJ3VJR"},
            {"name": "design-guidances", "id": "DUATA0SRUU"},
            {"name": "fss-solas-igc", "id": "HMXCQNXT1V"},
            {"name": "pipes", "id": "VDXB3NKJ0O"}
        ]
        
        total_processed = 0
        total_failed = 0
        
        for ds in data_sources:
            print(f"\n=== {ds['name']} 상세 분석 ===")
            
            # 최근 3개 동기화 작업 확인
            ingestion_jobs = bedrock_agent.list_ingestion_jobs(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['id'],
                maxResults=3
            )
            
            if not ingestion_jobs['ingestionJobSummaries']:
                print("동기화 작업 없음")
                continue
            
            for i, job_summary in enumerate(ingestion_jobs['ingestionJobSummaries'], 1):
                job_id = job_summary['ingestionJobId']
                status = job_summary['status']
                
                print(f"\n--- 작업 {i}: {status} ---")
                print(f"작업 ID: {job_id}")
                print(f"시작: {job_summary['startedAt']}")
                print(f"업데이트: {job_summary['updatedAt']}")
                
                # 작업 상세 정보
                try:
                    job_detail = bedrock_agent.get_ingestion_job(
                        knowledgeBaseId=kb_id,
                        dataSourceId=ds['id'],
                        ingestionJobId=job_id
                    )
                    
                    job = job_detail['ingestionJob']
                    stats = job.get('statistics', {})
                    
                    scanned = stats.get('numberOfDocumentsScanned', 0)
                    processed = stats.get('numberOfNewDocumentsIndexed', 0)
                    modified = stats.get('numberOfModifiedDocumentsIndexed', 0)
                    deleted = stats.get('numberOfDocumentsDeleted', 0)
                    failed = stats.get('numberOfDocumentsFailed', 0)
                    
                    print(f"통계:")
                    print(f"  - 스캔: {scanned}개")
                    print(f"  - 신규 처리: {processed}개")
                    print(f"  - 수정 처리: {modified}개")
                    print(f"  - 삭제: {deleted}개")
                    print(f"  - 실패: {failed}개")
                    
                    if i == 1:  # 최신 작업만 집계
                        total_processed += processed + modified
                        total_failed += failed
                    
                    # 실패 원인 분석
                    if failed > 0:
                        print(f"  ⚠️ {failed}개 문서 처리 실패!")
                        
                    if scanned > (processed + modified + failed):
                        missing = scanned - (processed + modified + failed)
                        print(f"  ❌ {missing}개 문서 처리 누락!")
                    
                    # 처리 시간 분석
                    if 'startedAt' in job and 'updatedAt' in job:
                        duration = (job['updatedAt'] - job['startedAt']).total_seconds()
                        print(f"  - 처리 시간: {duration:.1f}초")
                        
                        if duration > 600:  # 10분 이상
                            print(f"    ⚠️ 처리 시간이 길음 (>10분)")
                    
                except Exception as e:
                    print(f"  작업 상세 정보 확인 실패: {e}")
        
        print(f"\n=== 전체 요약 ===")
        print(f"총 처리된 문서: {total_processed}개")
        print(f"총 실패한 문서: {total_failed}개")
        
        # 청킹 효율성 분석
        print(f"\n=== 청킹 효율성 분석 ===")
        
        # 실제 검색으로 청크 수 추정
        bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        test_queries = ["piping", "DNV", "IGC"]
        total_chunks = 0
        
        for query in test_queries:
            try:
                response = bedrock_runtime.retrieve(
                    knowledgeBaseId=kb_id,
                    retrievalQuery={'text': query},
                    retrievalConfiguration={
                        'vectorSearchConfiguration': {
                            'numberOfResults': 50
                        }
                    }
                )
                
                chunk_count = len(response['retrievalResults'])
                total_chunks = max(total_chunks, chunk_count)
                print(f"'{query}' 검색: {chunk_count}개 청크")
                
            except Exception as e:
                print(f"'{query}' 검색 실패: {e}")
        
        print(f"\n추정 총 청크 수: ~{total_chunks}개")
        
        # 문제 진단
        print(f"\n=== 문제 진단 ===")
        
        expected_chunks_per_doc = 50  # 문서당 예상 청크 수
        expected_total = total_processed * expected_chunks_per_doc
        
        if total_chunks < expected_total * 0.1:  # 10% 미만
            print(f"❌ 심각한 청킹 문제: 예상({expected_total}) vs 실제(~{total_chunks})")
            print("가능한 원인:")
            print("  1. Lambda 함수 처리 실패")
            print("  2. PDF 파싱 실패")
            print("  3. 청킹 로직 오류")
            print("  4. 벡터 임베딩 실패")
        elif total_chunks < expected_total * 0.5:  # 50% 미만
            print(f"⚠️ 청킹 효율성 문제: 예상({expected_total}) vs 실제(~{total_chunks})")
        else:
            print(f"✅ 청킹 정상: 실제(~{total_chunks})")
        
        return True
        
    except Exception as e:
        print(f"❌ 청킹 문제 진단 실패: {e}")
        return False

if __name__ == "__main__":
    success = diagnose_chunking_issue()
    exit(0 if success else 1)