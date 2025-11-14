#!/usr/bin/env python3
"""
PWRU19RDNE KB 콘텐츠 패턴 분석
다양한 쿼리로 검색하여 콘텐츠 타입 분류
"""

import boto3
import json

def analyze_pwru_content_patterns():
    """PWRU19RDNE KB 콘텐츠 패턴 분석"""
    
    bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    # 다양한 쿼리로 테스트
    queries = [
        "소화기",
        "화재 감지",
        "스프링클러",
        "안전 규정",
        "SOLAS",
        "선박 구조",
        "방화벽",
        "비상 탈출"
    ]
    
    all_results = []
    content_types = {
        'ai_conversation': 0,  # "I understand..." 타입
        'structured_summary': 0,  # "# Fire Safety..." 타입
        'other': 0
    }
    
    for query in queries:
        print(f"\n🔍 쿼리: '{query}'")
        
        try:
            response = bedrock_agent.retrieve(
                knowledgeBaseId='PWRU19RDNE',
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5
                    }
                }
            )
            
            for i, result in enumerate(response.get('retrievalResults', [])):
                content = result.get('content', {})
                text = content.get('text', '')
                page_num = result.get('metadata', {}).get('x-amz-bedrock-kb-document-page-number', 'N/A')
                
                # 콘텐츠 타입 분류
                content_type = classify_content_type(text)
                content_types[content_type] += 1
                
                print(f"  결과 {i+1} (페이지 {page_num}): {content_type}")
                print(f"    길이: {len(text)}자")
                print(f"    시작: {text[:100]}...")
                
                all_results.append({
                    'query': query,
                    'page_number': page_num,
                    'content_type': content_type,
                    'length': len(text),
                    'preview': text[:200]
                })
                
        except Exception as e:
            print(f"  ❌ 검색 실패: {e}")
    
    # 통계 출력
    print(f"\n📊 콘텐츠 타입 통계:")
    total = sum(content_types.values())
    for content_type, count in content_types.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {content_type}: {count}개 ({percentage:.1f}%)")
    
    # 페이지별 분석
    analyze_by_page(all_results)
    
    return all_results

def classify_content_type(text):
    """콘텐츠 타입 분류"""
    
    if not text:
        return 'other'
    
    # AI 대화형 응답
    if any(phrase in text for phrase in [
        "I understand. I will not reproduce",
        "I'll summarize and discuss",
        "Here is a summary of the key points"
    ]):
        return 'ai_conversation'
    
    # 구조화된 요약
    if text.startswith('#') or any(phrase in text for phrase in [
        "This document covers",
        "Key points include:",
        "## Water Supply Systems",
        "# Fire Safety"
    ]):
        return 'structured_summary'
    
    return 'other'

def analyze_by_page(results):
    """페이지별 콘텐츠 타입 분석"""
    
    page_analysis = {}
    
    for result in results:
        page_num = result['page_number']
        content_type = result['content_type']
        
        if page_num not in page_analysis:
            page_analysis[page_num] = {}
        
        if content_type not in page_analysis[page_num]:
            page_analysis[page_num][content_type] = 0
        
        page_analysis[page_num][content_type] += 1
    
    print(f"\n📄 페이지별 콘텐츠 타입:")
    for page_num in sorted(page_analysis.keys(), key=lambda x: float(x) if x != 'N/A' else 999):
        types = page_analysis[page_num]
        print(f"  페이지 {page_num}: {types}")

if __name__ == "__main__":
    print("🔍 PWRU19RDNE KB 콘텐츠 패턴 분석")
    analyze_pwru_content_patterns()