#!/usr/bin/env python3
"""
Plan-Execute Agent가 KB에서 가져오는 메타데이터 분석
참조 정보의 차이점 원인 파악
"""

import boto3
import json
from typing import Dict, List

def debug_kb_retrieve_metadata(kb_id: str, query: str):
    """KB 검색 결과의 메타데이터 상세 분석"""
    
    bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5
                }
            }
        )
        
        print(f"🔍 KB 검색 결과 분석: {kb_id}")
        print(f"📝 쿼리: {query}")
        print(f"📊 결과 수: {len(response.get('retrievalResults', []))}")
        
        for i, result in enumerate(response.get('retrievalResults', [])):
            print(f"\n--- 결과 {i+1} ---")
            
            # 기본 정보
            score = result.get('score', 0)
            print(f"점수: {score:.4f}")
            
            # 콘텐츠 분석
            content = result.get('content', {})
            text = content.get('text', '')
            print(f"콘텐츠 길이: {len(text)} 문자")
            print(f"콘텐츠 미리보기: {text[:200]}...")
            
            # 콘텐츠 타입 분석
            if text.startswith('I understand. I will not reproduce'):
                print("🤖 타입: AI 대화형 응답")
            elif text.startswith('#') or 'This document covers' in text:
                print("📋 타입: 구조화된 문서 요약")
            else:
                print("❓ 타입: 기타")
            
            # 메타데이터 상세 분석
            metadata = result.get('metadata', {})
            print(f"메타데이터 키: {list(metadata.keys())}")
            
            for key, value in metadata.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}... (길이: {len(value)})")
                else:
                    print(f"  {key}: {value}")
            
            # Location 정보 분석
            location = result.get('location', {})
            print(f"Location 정보:")
            
            if 's3Location' in location:
                s3_loc = location['s3Location']
                print(f"  S3 URI: {s3_loc.get('uri', 'N/A')}")
            
            if 'confluenceLocation' in location:
                print(f"  Confluence: {location['confluenceLocation']}")
            
            if 'salesforceLocation' in location:
                print(f"  Salesforce: {location['salesforceLocation']}")
            
            if 'sharePointLocation' in location:
                print(f"  SharePoint: {location['sharePointLocation']}")
            
            if 'webLocation' in location:
                print(f"  Web: {location['webLocation']}")
            
            print("-" * 50)
        
        return response
        
    except Exception as e:
        print(f"❌ KB 검색 실패: {e}")
        return None

def compare_kb_responses():
    """두 KB의 응답 비교"""
    
    query = "선박 소화기 요구사항"
    
    print("🔍 KB 응답 비교 분석\n")
    
    # CDPB5AI6BH KB 분석
    print("=" * 60)
    print("CDPB5AI6BH KB (OCR 메타데이터 포함)")
    print("=" * 60)
    cdpb_response = debug_kb_retrieve_metadata('CDPB5AI6BH', query)
    
    print("\n" + "=" * 60)
    print("PWRU19RDNE KB (멀티모달)")
    print("=" * 60)
    pwru_response = debug_kb_retrieve_metadata('PWRU19RDNE', query)
    
    # 차이점 분석
    print("\n" + "🔍 차이점 분석:")
    
    if cdpb_response and pwru_response:
        cdpb_results = cdpb_response.get('retrievalResults', [])
        pwru_results = pwru_response.get('retrievalResults', [])
        
        print(f"CDPB5AI6BH 결과 수: {len(cdpb_results)}")
        print(f"PWRU19RDNE 결과 수: {len(pwru_results)}")
        
        # 메타데이터 키 비교
        if cdpb_results and pwru_results:
            cdpb_keys = set(cdpb_results[0].get('metadata', {}).keys())
            pwru_keys = set(pwru_results[0].get('metadata', {}).keys())
            
            print(f"\nCDPB5AI6BH 메타데이터 키: {cdpb_keys}")
            print(f"PWRU19RDNE 메타데이터 키: {pwru_keys}")
            print(f"공통 키: {cdpb_keys & pwru_keys}")
            print(f"CDPB5AI6BH만 있는 키: {cdpb_keys - pwru_keys}")
            print(f"PWRU19RDNE만 있는 키: {pwru_keys - cdpb_keys}")

if __name__ == "__main__":
    compare_kb_responses()