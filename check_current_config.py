#!/usr/bin/env python3
"""
현재 KB 설정 확인 (청킹 + 변환 함수)
"""
import boto3
import json

def check_current_config():
    print("🔍 현재 KB 설정 확인...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        kb_id = "ZGBA1R5CS0"
        
        # 각 데이터 소스 설정 확인
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        
        for ds in data_sources['dataSourceSummaries']:
            print(f"\n=== {ds['name']} ===")
            
            # 데이터 소스 상세 정보
            ds_detail = bedrock_agent.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['dataSourceId']
            )
            
            config = ds_detail['dataSource']['dataSourceConfiguration']
            
            # 1. 청킹 설정 확인
            print("1. 청킹 설정:")
            if 'chunkingConfiguration' in config:
                chunking = config['chunkingConfiguration']
                strategy = chunking['chunkingStrategy']
                print(f"   전략: {strategy}")
                
                if strategy == 'HIERARCHICAL':
                    hier_config = chunking['hierarchicalChunkingConfiguration']
                    print(f"   레벨 설정:")
                    for i, level in enumerate(hier_config['levelConfigurations'], 1):
                        print(f"     레벨 {i}: {level['maxTokens']} 토큰")
                    print(f"   오버랩: {hier_config['overlapTokens']} 토큰")
                    
                elif strategy == 'FIXED_SIZE':
                    fixed_config = chunking['fixedSizeChunkingConfiguration']
                    print(f"   청크 크기: {fixed_config['maxTokens']} 토큰")
                    print(f"   오버랩: {fixed_config['overlapPercentage']}%")
                    
            else:
                print("   ❌ 청킹 설정 없음 (기본값 사용)")
            
            # 2. 변환 함수 확인
            print("2. 변환 함수:")
            s3_config = config['s3Configuration']
            
            if 'parsingConfiguration' in s3_config:
                parsing = s3_config['parsingConfiguration']
                strategy = parsing['parsingStrategy']
                print(f"   파싱 전략: {strategy}")
                
                if strategy == 'BEDROCK_FOUNDATION_MODEL':
                    model_config = parsing['bedrockFoundationModelConfiguration']
                    print(f"   모델 ARN: {model_config['modelArn']}")
                    if 'parsingPrompt' in model_config:
                        prompt = model_config['parsingPrompt']['textPromptTemplate']
                        print(f"   프롬프트: {prompt[:100]}...")
                        
                elif strategy == 'BEDROCK_DATA_AUTOMATION':
                    automation_config = parsing['bedrockDataAutomationConfiguration']
                    if 'transformationConfiguration' in automation_config:
                        transform = automation_config['transformationConfiguration']
                        if 'transformations' in transform:
                            for i, t in enumerate(transform['transformations'], 1):
                                if 'stepToApply' in t:
                                    print(f"   변환 {i}: {t['stepToApply']}")
                                if 'transformationFunction' in t:
                                    func = t['transformationFunction']
                                    print(f"     함수 ARN: {func['transformationLambdaConfiguration']['lambdaArn']}")
                        
            else:
                print("   ❌ 파싱 설정 없음 (기본값 사용)")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 확인 실패: {e}")
        return False

if __name__ == "__main__":
    success = check_current_config()
    exit(0 if success else 1)