"""
간단한 GraphRAG Agent 테스트
"""
import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("GraphRAG Agent 메타데이터 분석 테스트")
print("=" * 80)

# 1. 모듈 import 테스트
print("\n[1단계] 모듈 import 테스트...")
try:
    from agents.plan_execute_agent.agent import PlanExecuteAgent
    print("✓ PlanExecuteAgent import 성공")
except Exception as e:
    print(f"✗ Import 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 환경 변수 확인
print("\n[2단계] 환경 변수 확인...")
aws_region = os.getenv("AWS_REGION", "us-west-2")
kb_id = os.getenv("KNOWLEDGE_BASE_ID", "PWRU19RDNE")

print(f"✓ AWS Region: {aws_region}")
print(f"✓ KB ID: {kb_id}")

# 3. Agent 초기화
print("\n[3단계] Agent 초기화...")
try:
    agent = PlanExecuteAgent(kb_id=kb_id)
    print("✓ PlanExecuteAgent 초기화 성공")
except Exception as e:
    print(f"✗ Agent 초기화 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. AWS 서비스 연결 확인
print("\n[4단계] AWS 서비스 연결 확인...")
try:
    import boto3
    bedrock_client = boto3.client('bedrock-agent-runtime', region_name=aws_region)
    print("✓ Bedrock Agent Runtime 연결 성공")
    
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region)
    print("✓ Bedrock Runtime 연결 성공")
    
    # DynamoDB는 PWRU19RDNE KB에서만 필요
    if kb_id == "PWRU19RDNE":
        dynamodb = boto3.resource('dynamodb', region_name=aws_region)
        print("✓ DynamoDB 연결 성공 (PWRU19RDNE용)")
    else:
        print("✓ DynamoDB 연결 생략 (CDPB5AI6BH는 메타데이터 사용)")
except Exception as e:
    print(f"✗ AWS 서비스 연결 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. KB 메타데이터 검사
print("\n[5단계] KB 메타데이터 검사...")
try:
    # 간단한 검색으로 메타데이터 구조 확인
    search_results = agent._execute_neptune_search("fire safety", kb_id)
    
    if search_results:
        print(f"\n✓ 검색 결과: {len(search_results)}개 문서")
        
        # 첫 번째 결과의 메타데이터 상세 분석
        first_result = search_results[0]
        metadata = first_result.get('metadata', {})
        
        print(f"\n📋 KB {kb_id} 메타데이터 구조:")
        print("-" * 60)
        for key, value in metadata.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")
        
        # content 필드 분석 (벡터 검색에 사용되는 데이터)
        content_text = first_result.get('content', '')
        print(f"\n🔍 content 필드 분석 (벡터 검색용):")
        print("-" * 60)
        print(f"  길이: {len(content_text)}자")
        if content_text:
            print(f"  내용 (처음 200자): {content_text[:200]}...")
            
            # content와 description 비교
            description = metadata.get('x-amz-bedrock-kb-description', '')
            if description:
                print(f"\n🔄 content vs description 비교:")
                print(f"  - content 길이: {len(content_text)}자")
                print(f"  - description 길이: {len(description)}자")
                
                # 내용 유사성 확인
                if content_text[:100] == description[:100]:
                    print(f"  - 내용: 동일")
                else:
                    print(f"  - 내용: 다름")
                    print(f"    content: {content_text[:100]}...")
                    print(f"    description: {description[:100]}...")
        else:
            print(f"  내용: 비어있음")
        
        print(f"\n📄 데이터 소스 정보:")
        print(f"  - 소스 파일: {first_result.get('source_file', 'N/A')}")
        print(f"  - 페이지 번호: {first_result.get('page_number', 'N/A')}")
        print(f"  - 이미지 URI: {'있음' if first_result.get('image_uri') else '없음'}")
        print(f"  - 멀티모달: {first_result.get('has_multimodal', False)}")
        
        # KB별 특성 확인
        if kb_id == "CDPB5AI6BH":
            print(f"\n🔍 CDPB5AI6BH 특성:")
            print(f"  - OCR 텍스트 소스: 메타데이터 (x-amz-bedrock-kb-description)")
            print(f"  - 이미지 소스: 메타데이터 (x-amz-bedrock-kb-byte-content-source)")
        elif kb_id == "PWRU19RDNE":
            print(f"\n🔍 PWRU19RDNE 특성:")
            print(f"  - OCR 텍스트 소스: DynamoDB 조회")
            print(f"  - 이미지 소스: DynamoDB 조회")
            
            # DynamoDB 연결 테스트
            doc_id = agent._extract_document_id_from_source(metadata.get('x-amz-bedrock-kb-source-uri', ''))
            page_num = str(int(metadata.get('x-amz-bedrock-kb-document-page-number', 1)))
            
            ocr_text = agent._get_ocr_from_dynamodb(doc_id, page_num)
            image_url = agent._get_image_url_from_dynamodb(doc_id, page_num)
            
            print(f"  - DynamoDB OCR: {'성공' if ocr_text else '실패'}")
            print(f"  - DynamoDB 이미지: {'성공' if image_url else '실패'}")
    
    else:
        print("\n✗ 검색 결과 없음")
        
except Exception as e:
    print(f"\n✗ 메타데이터 검사 실패: {e}")
    import traceback
    traceback.print_exc()

# 6. 질문 처리 테스트
print("\n[6단계] 질문 처리 테스트...")
question = "선박에 반드시 갖춰야 하는 소화설비 기본 구성을 알려줘"
print(f"질문: {question}")

try:
    print("\n워크플로우 실행 중...")
    result = agent.process_message(question, session_id="test-session")
    
    print(f"\n✓ 성공 여부: {result.get('success', False)}")
    
    if result.get('success'):
        content = result.get('content', '')
        print(f"\n답변 (처음 300자):")
        print("-" * 80)
        print(content[:300] + "..." if len(content) > 300 else content)
        print("-" * 80)
        
        references = result.get('references', [])
        print(f"\n✓ 참조 문서 수: {len(references)}개")
        
        # 참조 문서의 데이터 소스 확인
        if references:
            print(f"\n📚 참조 문서 데이터 소스:")
            for i, ref in enumerate(references[:2]):
                print(f"  [{i+1}] {ref.get('source_file', 'N/A')} (페이지 {ref.get('page_number', 'N/A')})")
                print(f"      이미지: {'있음' if ref.get('image_uri') else '없음'}")
                print(f"      멀티모달: {ref.get('has_multimodal', False)}")
        
        response_time = result.get('response_time', 0)
        print(f"\n✓ 응답 시간: {response_time:.2f}초")
        
        print("\n" + "=" * 80)
        print("✓ 테스트 성공!")
        print("=" * 80)
    else:
        error = result.get('content', 'Unknown error')
        print(f"\n✗ 실패: {error}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ 워크플로우 실행 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 7. 다른 KB로 테스트 (선택사항)
other_kb = "PWRU19RDNE" if kb_id == "CDPB5AI6BH" else "CDPB5AI6BH"
print(f"\n[7단계] 다른 KB ({other_kb}) 비교 테스트...")
try:
    other_agent = PlanExecuteAgent(kb_id=other_kb)
    other_results = other_agent._execute_neptune_search("fire safety", other_kb)
    
    if other_results:
        other_metadata = other_results[0].get('metadata', {})
        print(f"\n📋 KB {other_kb} 메타데이터 키:")
        print(f"  - 키 개수: {len(other_metadata)}개")
        print(f"  - 주요 키: {list(other_metadata.keys())[:5]}")
        
        # 차이점 비교
        current_keys = set(search_results[0].get('metadata', {}).keys()) if search_results else set()
        other_keys = set(other_metadata.keys())
        
        unique_to_current = current_keys - other_keys
        unique_to_other = other_keys - current_keys
        
        if unique_to_current:
            print(f"\n🔍 {kb_id}에만 있는 키: {list(unique_to_current)}")
        if unique_to_other:
            print(f"🔍 {other_kb}에만 있는 키: {list(unique_to_other)}")
    
except Exception as e:
    print(f"\n⚠️ 다른 KB 테스트 실패: {e}")
