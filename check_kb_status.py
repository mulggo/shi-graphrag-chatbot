#!/usr/bin/env python3
"""
Neptune KB 상태 점검 스크립트
"""
import boto3
import json

def check_kb_status():
    print("🔍 Neptune KB 상태 점검 시작...")
    
    try:
        # Bedrock Agent 클라이언트
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        kb_id = "ZGBA1R5CS0"
        
        # 1. KB 기본 정보 확인
        print("\n=== 1. KB 기본 정보 ===")
        kb_info = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        kb = kb_info['knowledgeBase']
        
        print(f"KB ID: {kb['knowledgeBaseId']}")
        print(f"이름: {kb['name']}")
        print(f"상태: {kb['status']}")
        print(f"생성일: {kb['createdAt']}")
        print(f"업데이트일: {kb['updatedAt']}")
        
        # 2. 데이터 소스 확인
        print("\n=== 2. 데이터 소스 확인 ===")
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        
        for i, ds in enumerate(data_sources['dataSourceSummaries'], 1):
            print(f"{i}. 데이터 소스 ID: {ds['dataSourceId']}")
            print(f"   이름: {ds['name']}")
            print(f"   상태: {ds['status']}")
            print(f"   업데이트일: {ds['updatedAt']}")
            
            # 데이터 소스 상세 정보
            ds_detail = bedrock_agent.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['dataSourceId']
            )
            
            s3_config = ds_detail['dataSource']['dataSourceConfiguration']['s3Configuration']
            print(f"   S3 버킷: {s3_config['bucketArn']}")
            if 'inclusionPrefixes' in s3_config:
                print(f"   포함 경로: {s3_config['inclusionPrefixes']}")
        
        # 3. 검색 테스트 (다양한 쿼리)
        print("\n=== 3. 검색 테스트 ===")
        test_queries = [
            "fire",
            "extinguisher", 
            "SOLAS",
            "safety",
            "ship",
            "소화기",
            "화재"
        ]
        
        for query in test_queries:
            try:
                response = bedrock_runtime.retrieve(
                    knowledgeBaseId=kb_id,
                    retrievalQuery={'text': query},
                    retrievalConfiguration={
                        'vectorSearchConfiguration': {
                            'numberOfResults': 5
                        }
                    }
                )
                
                results = response['retrievalResults']
                print(f"'{query}': {len(results)}개 결과")
                
                if results:
                    first_result = results[0]
                    print(f"  - 첫 번째 점수: {first_result.get('score', 0):.3f}")
                    print(f"  - 소스: {first_result.get('metadata', {}).get('source', 'Unknown')}")
                    
            except Exception as e:
                print(f"'{query}': 검색 실패 - {e}")
        
        # 4. KB 통계 정보 (가능한 경우)
        print("\n=== 4. KB 통계 정보 ===")
        try:
            # 빈 쿼리로 전체 문서 수 추정
            response = bedrock_runtime.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': ' '},  # 공백 쿼리
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 100
                    }
                }
            )
            print(f"전체 문서 청크 수 (추정): {len(response['retrievalResults'])}개 이상")
            
        except Exception as e:
            print(f"통계 정보 조회 실패: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ KB 상태 점검 실패: {e}")
        print(f"   에러 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = check_kb_status()
    exit(0 if success else 1)