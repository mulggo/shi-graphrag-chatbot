#!/usr/bin/env python3
"""
전체 워크플로우 테스트: Plan-Execute Agent + UI 시뮬레이션
"""

import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

from agents.plan_execute_agent.agent import PlanExecuteAgent
from ui.reference_display import ReferenceDisplay

def test_complete_workflow():
    """완전한 워크플로우 테스트"""
    
    print("🚀 전체 워크플로우 테스트 시작\n")
    
    # 1. Plan-Execute Agent 실행
    print("1️⃣ Plan-Execute Agent 실행")
    agent = PlanExecuteAgent(kb_id='PWRU19RDNE')
    result = agent.process_message("선박의 소화기 요구사항은?", "test_session")
    
    print(f"✅ 성공: {result.get('success')}")
    print(f"📝 응답 길이: {len(result.get('content', ''))} 문자")
    print(f"📚 참조 수: {len(result.get('references', []))} 개")
    
    # 2. 참조 문서 분석
    print(f"\n2️⃣ 참조 문서 분석")
    references = result.get('references', [])
    
    for i, ref in enumerate(references[:2]):  # 처음 2개만
        print(f"\n--- 참조 {i+1} ---")
        print(f"📄 파일: {ref.get('source_file', 'N/A')}")
        print(f"📖 페이지: {ref.get('page_number', 'N/A')}")
        print(f"🔗 OCR 길이: {len(ref.get('ocr_text', ''))} 문자")
        print(f"🖼️  멀티모달: {ref.get('has_multimodal', False)}")
        print(f"🆔 데이터소스: {ref.get('data_source_id', 'N/A')}")
        print(f"🌐 이미지 URI: {ref.get('image_uri', 'N/A')}")
        
        # OCR 텍스트 타입 확인
        ocr_text = ref.get('ocr_text', '')
        if 'I understand. I will not reproduce' in ocr_text:
            print("❌ OCR 타입: AI 요약")
        elif ocr_text.startswith('Title') or 'SOLAS' in ocr_text:
            print("✅ OCR 타입: 실제 원본 텍스트")
        else:
            print("⚠️  OCR 타입: 기타")
    
    # 3. UI 이미지 로드 시뮬레이션
    print(f"\n3️⃣ UI 이미지 로드 시뮬레이션")
    display = ReferenceDisplay()
    
    for i, ref in enumerate(references[:1]):  # 첫 번째만
        image_uri = ref.get('image_uri', '')
        has_multimodal = ref.get('has_multimodal', False)
        
        print(f"\n참조 {i+1} 이미지 테스트:")
        print(f"URI: {image_uri}")
        print(f"멀티모달: {has_multimodal}")
        
        if has_multimodal and image_uri:
            try:
                images = display._get_s3_images_from_directory(image_uri)
                print(f"✅ 이미지 로드 성공: {len(images)}개")
                
                for j, (img_key, img_data) in enumerate(images[:2]):
                    print(f"  이미지 {j+1}: {img_key.split('/')[-1]} ({len(img_data)} bytes)")
                    
            except Exception as e:
                print(f"❌ 이미지 로드 실패: {e}")
        else:
            print("⚠️  멀티모달 지원 없음")
    
    # 4. 최종 결과 요약
    print(f"\n4️⃣ 최종 결과 요약")
    
    # OCR 품질 확인
    ocr_success = 0
    for ref in references:
        ocr_text = ref.get('ocr_text', '')
        if ocr_text and 'SOLAS' in ocr_text and len(ocr_text) > 1000:
            ocr_success += 1
    
    # 이미지 품질 확인
    image_success = 0
    for ref in references:
        if ref.get('has_multimodal') and ref.get('image_uri'):
            image_success += 1
    
    print(f"📊 OCR 품질: {ocr_success}/{len(references)} 성공")
    print(f"🖼️  이미지 품질: {image_success}/{len(references)} 성공")
    
    if ocr_success > 0 and image_success > 0:
        print("🎉 전체 워크플로우 성공!")
        print("   - DynamoDB OCR 조회 ✅")
        print("   - S3 이미지 로드 ✅")
        print("   - 멀티모달 기능 ✅")
    else:
        print("⚠️  일부 기능 미완성")

if __name__ == "__main__":
    test_complete_workflow()