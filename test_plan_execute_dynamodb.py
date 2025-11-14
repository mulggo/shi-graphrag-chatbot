#!/usr/bin/env python3
"""
Plan-Execute Agent의 DynamoDB OCR 조회 기능 테스트
"""

import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

from agents.plan_execute_agent.agent import PlanExecuteAgent

def test_dynamodb_ocr_lookup():
    """DynamoDB OCR 조회 기능 테스트"""
    
    print("🔍 Plan-Execute Agent DynamoDB OCR 조회 테스트\n")
    
    # Plan-Execute Agent 초기화
    agent = PlanExecuteAgent(kb_id='PWRU19RDNE')
    
    # 테스트 케이스들
    test_cases = [
        ('solas_chapter2', '1'),
        ('solas_chapter2', '15'),
        ('dnv_pt4_ch6', '1'),
        ('fss_code', '1'),
        ('igc_code', '1'),
        ('invalid_doc', '999')  # 존재하지 않는 데이터
    ]
    
    print("📊 DynamoDB OCR 조회 테스트:")
    for document_id, page_number in test_cases:
        print(f"\n--- 테스트: {document_id}, 페이지 {page_number} ---")
        
        ocr_text = agent._get_ocr_from_dynamodb(document_id, page_number)
        
        if ocr_text:
            print(f"✅ 성공: {len(ocr_text)}자")
            print(f"미리보기: {ocr_text[:200]}...")
        else:
            print("❌ 데이터 없음")

def test_document_id_extraction():
    """문서 ID 추출 기능 테스트"""
    
    print("\n🔍 문서 ID 추출 테스트:")
    
    agent = PlanExecuteAgent()
    
    test_uris = [
        "s3://shi-kb-bucket/documents/all/02-2 SOLAS Chapter II-2_Construction Fire Protection, Fire Detection and Fire Extinction.pdf",
        "s3://shi-kb-bucket/documents/all/DNV-RU-SHIP-Pt4 Ch6.pdf",
        "s3://shi-kb-bucket/documents/all/FSS.pdf",
        "s3://shi-kb-bucket/documents/all/IGC_Code_latest.pdf",
        "s3://shi-kb-bucket/documents/all/Design guidance_Spoolcutting.PDF"
    ]
    
    for uri in test_uris:
        document_id = agent._extract_document_id_from_source(uri)
        filename = uri.split('/')[-1]
        print(f"파일: {filename}")
        print(f"문서 ID: {document_id}\n")

def test_full_workflow():
    """전체 워크플로우 테스트"""
    
    print("🚀 전체 워크플로우 테스트:")
    
    agent = PlanExecuteAgent(kb_id='PWRU19RDNE')
    
    # 테스트 질문
    test_query = "선박의 소화기 요구사항은?"
    
    print(f"질문: {test_query}")
    print("처리 중...")
    
    result = agent.process_message(test_query, "test_session")
    
    print(f"\n📊 결과:")
    print(f"성공: {result.get('success')}")
    print(f"응답 길이: {len(result.get('content', ''))}")
    print(f"참조 수: {len(result.get('references', []))}")
    print(f"처리 시간: {result.get('response_time', 0):.2f}초")
    
    # 첫 번째 참조의 OCR 텍스트 확인
    references = result.get('references', [])
    if references:
        first_ref = references[0]
        ocr_text = first_ref.get('ocr_text', '')
        
        print(f"\n📄 첫 번째 참조 OCR:")
        print(f"길이: {len(ocr_text)}자")
        print(f"미리보기: {ocr_text[:300]}...")
        
        # AI 요약인지 실제 OCR인지 확인
        if 'I understand. I will not reproduce' in ocr_text:
            print("❌ 타입: AI 요약 (DynamoDB 조회 실패)")
        elif ocr_text.startswith('#') or 'This document covers' in ocr_text:
            print("⚠️  타입: 구조화된 요약")
        else:
            print("✅ 타입: 실제 OCR 텍스트")

if __name__ == "__main__":
    # 1. DynamoDB 조회 테스트
    test_dynamodb_ocr_lookup()
    
    # 2. 문서 ID 추출 테스트
    test_document_id_extraction()
    
    # 3. 전체 워크플로우 테스트
    test_full_workflow()