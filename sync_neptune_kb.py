#!/usr/bin/env python3
"""
Neptune KB 데이터 소스 재동기화
"""
import boto3
import time

def sync_neptune_kb():
    print("🔄 Neptune KB 데이터 소스 재동기화 시작...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        # 모든 데이터 소스 조회
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId='ZGBA1R5CS0')
        
        print(f"📁 총 {len(data_sources['dataSourceSummaries'])}개 데이터 소스 발견")
        
        # 각 데이터 소스별 동기화 작업 시작
        sync_jobs = []
        
        for ds in data_sources['dataSourceSummaries']:
            ds_id = ds['dataSourceId']
            ds_name = ds['name']
            ds_status = ds['status']
            
            print(f"\n📂 데이터 소스: {ds_name}")
            print(f"   현재 상태: {ds_status}")
            
            if ds_status == 'AVAILABLE':
                try:
                    # 동기화 작업 시작
                    sync_response = bedrock_agent.start_ingestion_job(
                        knowledgeBaseId='ZGBA1R5CS0',
                        dataSourceId=ds_id,
                        description=f"Manual sync for {ds_name}"
                    )
                    
                    job_id = sync_response['ingestionJob']['ingestionJobId']
                    sync_jobs.append({
                        'job_id': job_id,
                        'data_source': ds_name,
                        'data_source_id': ds_id
                    })
                    
                    print(f"   ✅ 동기화 작업 시작됨 (Job ID: {job_id})")
                    
                except Exception as e:
                    print(f"   ❌ 동기화 작업 시작 실패: {e}")
            else:
                print(f"   ⚠️ 상태가 AVAILABLE이 아님: {ds_status}")
        
        if sync_jobs:
            print(f"\n⏳ {len(sync_jobs)}개 동기화 작업 진행 상황 모니터링...")
            
            # 동기화 작업 상태 모니터링 (최대 5분)
            max_wait_time = 300  # 5분
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                all_completed = True
                
                for job in sync_jobs:
                    try:
                        job_status = bedrock_agent.get_ingestion_job(
                            knowledgeBaseId='ZGBA1R5CS0',
                            dataSourceId=job['data_source_id'],
                            ingestionJobId=job['job_id']
                        )
                        
                        status = job_status['ingestionJob']['status']
                        
                        if status in ['IN_PROGRESS', 'STARTING']:
                            all_completed = False
                            print(f"   🔄 {job['data_source']}: {status}")
                        elif status == 'COMPLETE':
                            print(f"   ✅ {job['data_source']}: 완료")
                        elif status == 'FAILED':
                            failure_reasons = job_status['ingestionJob'].get('failureReasons', [])
                            print(f"   ❌ {job['data_source']}: 실패 - {failure_reasons}")
                        
                    except Exception as e:
                        print(f"   ⚠️ {job['data_source']} 상태 확인 실패: {e}")
                
                if all_completed:
                    print("\n🎉 모든 동기화 작업 완료!")
                    break
                
                time.sleep(10)  # 10초 대기
            
            if not all_completed:
                print(f"\n⏰ {max_wait_time//60}분 대기 시간 초과. 백그라운드에서 계속 진행됩니다.")
        
        else:
            print("\n⚠️ 시작된 동기화 작업이 없습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ Neptune KB 동기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = sync_neptune_kb()
    
    if success:
        print("\n🔍 동기화 후 검색 테스트...")
        time.sleep(5)  # 5초 대기 후 테스트
        
        try:
            sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')
            from agents.plan_execute_agent.agent import PlanExecuteAgent
            
            agent = PlanExecuteAgent()
            test_result = agent._execute_neptune_search("safety")
            print(f"✅ 동기화 후 검색 결과: {len(test_result)}개")
            
            if test_result:
                for i, result in enumerate(test_result[:2]):
                    print(f"   [{i+1}] {result.get('source', 'Unknown')}")
                    print(f"       {result.get('content', '')[:100]}...")
            
        except Exception as e:
            print(f"❌ 동기화 후 테스트 실패: {e}")
    
    exit(0 if success else 1)