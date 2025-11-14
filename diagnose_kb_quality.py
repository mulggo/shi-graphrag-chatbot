#!/usr/bin/env python3
"""
KB 데이터 품질 문제 진단
"""
import boto3
import json

def diagnose_kb_quality():
    print("🔍 KB 데이터 품질 문제 진단...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        kb_id = "ZGBA1R5CS0"
        
        # 1. KB 설정 확인
        print("\n=== 1. KB 설정 확인 ===")
        kb_info = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        kb = kb_info['knowledgeBase']
        
        # 벡터 설정 확인
        vector_config = kb['knowledgeBaseConfiguration']['vectorKnowledgeBaseConfiguration']
        print(f"임베딩 모델: {vector_config['embeddingModelArn']}")
        
        # 2. 각 데이터 소스별 상세 설정 확인
        print("\n=== 2. 데이터 소스 설정 확인 ===")
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        
        for ds in data_sources['dataSourceSummaries']:
            print(f"\n--- {ds['name']} ---")
            
            # 데이터 소스 상세 정보
            ds_detail = bedrock_agent.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['dataSourceId']
            )
            
            ds_config = ds_detail['dataSource']
            
            # 청킹 설정 확인
            if 'chunkingConfiguration' in ds_config['dataSourceConfiguration']:
                chunking = ds_config['dataSourceConfiguration']['chunkingConfiguration']
                print(f"청킹 전략: {chunking['chunkingStrategy']}")
                
                if chunking['chunkingStrategy'] == 'FIXED_SIZE':
                    fixed_config = chunking['fixedSizeChunkingConfiguration']
                    print(f"  - 청크 크기: {fixed_config['maxTokens']} 토큰")
                    print(f"  - 오버랩: {fixed_config['overlapPercentage']}%")
            else:
                print("청킹 설정: 기본값 사용")
            
            # 최근 동기화 작업 상세 분석
            ingestion_jobs = bedrock_agent.list_ingestion_jobs(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['dataSourceId'],
                maxResults=1
            )
            
            if ingestion_jobs['ingestionJobSummaries']:
                latest_job = ingestion_jobs['ingestionJobSummaries'][0]
                job_id = latest_job['ingestionJobId']
                
                # 동기화 작업 상세 정보
                job_detail = bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds['dataSourceId'],
                    ingestionJobId=job_id
                )
                
                job = job_detail['ingestionJob']
                stats = job.get('statistics', {})
                
                print(f"최근 동기화 ({latest_job['status']}):")
                print(f"  - 스캔된 문서: {stats.get('numberOfDocumentsScanned', 0)}개")
                print(f"  - 처리된 문서: {stats.get('numberOfNewDocumentsIndexed', 0)}개")
                print(f"  - 수정된 문서: {stats.get('numberOfModifiedDocumentsIndexed', 0)}개")
                print(f"  - 삭제된 문서: {stats.get('numberOfDocumentsDeleted', 0)}개")
                print(f"  - 실패한 문서: {stats.get('numberOfDocumentsFailed', 0)}개")
                
                # 실패 원인 확인
                if stats.get('numberOfDocumentsFailed', 0) > 0:
                    print("  ⚠️ 문서 처리 실패 발생!")
                
                # 처리 시간 확인
                if 'startedAt' in job and 'updatedAt' in job:
                    duration = (job['updatedAt'] - job['startedAt']).total_seconds()
                    print(f"  - 처리 시간: {duration:.1f}초")
        
        # 3. 실제 검색 성능 분석
        print("\n=== 3. 검색 성능 분석 ===")
        bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        # 다양한 검색 설정으로 테스트
        test_configs = [
            {"numberOfResults": 5, "name": "기본(5개)"},
            {"numberOfResults": 20, "name": "확장(20개)"},
            {"numberOfResults": 50, "name": "최대(50개)"}
        ]
        
        test_query = "piping"  # 가장 성공적인 검색어
        
        for config in test_configs:
            try:
                response = bedrock_runtime.retrieve(
                    knowledgeBaseId=kb_id,
                    retrievalQuery={'text': test_query},
                    retrievalConfiguration={
                        'vectorSearchConfiguration': config
                    }
                )
                
                results = response['retrievalResults']
                print(f"{config['name']}: {len(results)}개 결과")
                
                if results:
                    scores = [r.get('score', 0) for r in results]
                    print(f"  - 점수 범위: {min(scores):.3f} ~ {max(scores):.3f}")
                    
                    # 소스 분포 확인
                    sources = {}
                    for r in results:
                        source_uri = r.get('metadata', {}).get('x-amz-bedrock-kb-source-uri', 'Unknown')
                        if source_uri != 'Unknown':
                            filename = source_uri.split('/')[-1]
                            sources[filename] = sources.get(filename, 0) + 1
                    
                    print(f"  - 소스 분포: {dict(list(sources.items())[:3])}")
                
            except Exception as e:
                print(f"{config['name']}: 실패 - {e}")
        
        # 4. 문제 진단 요약
        print("\n=== 4. 문제 진단 요약 ===")
        
        # 총 처리된 문서 수 계산
        total_processed = 0
        total_failed = 0
        
        for ds in data_sources['dataSourceSummaries']:
            ingestion_jobs = bedrock_agent.list_ingestion_jobs(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['dataSourceId'],
                maxResults=1
            )
            
            if ingestion_jobs['ingestionJobSummaries']:
                latest_job = ingestion_jobs['ingestionJobSummaries'][0]
                job_id = latest_job['ingestionJobId']
                
                job_detail = bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds['dataSourceId'],
                    ingestionJobId=job_id
                )
                
                stats = job_detail['ingestionJob'].get('statistics', {})
                total_processed += stats.get('numberOfNewDocumentsIndexed', 0)
                total_failed += stats.get('numberOfDocumentsFailed', 0)
        
        print(f"총 처리된 문서: {total_processed}개")
        print(f"총 실패한 문서: {total_failed}개")
        
        # 문제 진단
        issues = []
        
        if total_processed < 10:
            issues.append("❌ 처리된 문서 수가 너무 적음 (< 10개)")
        
        if total_failed > 0:
            issues.append(f"❌ 문서 처리 실패 발생 ({total_failed}개)")
        
        # S3 파일 수와 비교
        s3 = boto3.client('s3')
        bucket_name = 'shi-kb-bucket'
        
        total_s3_files = 0
        prefixes = ['documents/dnv-ru/', 'documents/design/', 'documents/fss-solas-igc/', 'documents/pipes/']
        
        for prefix in prefixes:
            try:
                response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
                if 'Contents' in response:
                    # 폴더 제외하고 실제 파일만 카운트
                    files = [obj for obj in response['Contents'] if not obj['Key'].endswith('/')]
                    total_s3_files += len(files)
            except:
                pass
        
        if total_processed < total_s3_files:
            issues.append(f"❌ S3 파일({total_s3_files}개) vs 처리된 문서({total_processed}개) 불일치")
        
        if not issues:
            print("✅ 주요 문제 없음")
        else:
            print("발견된 문제들:")
            for issue in issues:
                print(f"  {issue}")
        
        return True
        
    except Exception as e:
        print(f"❌ KB 품질 진단 실패: {e}")
        return False

if __name__ == "__main__":
    success = diagnose_kb_quality()
    exit(0 if success else 1)