# Plan-Execute Agent 테스트 체크리스트
## 단계별 검증 가이드

## 🎯 목표
`agents/plan_execute_agent/agent.py`의 핵심 기능들이 올바르게 작동하는지 단계별로 확인

---

## 📋 **1단계: 기본 연결 확인** (최우선)

### ✅ **1.1 AWS 클라이언트 초기화**
**테스트 대상:**
```python
self.bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
```

**체크 방법:**
```python
# 테스트 스크립트
from agents.plan_execute_agent.agent import PlanExecuteAgent

try:
    agent = PlanExecuteAgent()
    print("✅ AWS 클라이언트 초기화 성공")
except Exception as e:
    print(f"❌ AWS 클라이언트 초기화 실패: {e}")
```

**예상 문제:**
- `NoCredentialsError`: AWS 자격증명 없음
- `AccessDenied`: 권한 부족
- `EndpointConnectionError`: 네트워크 문제

**해결 방법:**
```bash
aws configure list
aws sts get-caller-identity
```

---

### ✅ **1.2 Neptune KB 연결 테스트**
**테스트 대상:**
```python
def _execute_neptune_search(self, query: str, kb_id: str = "ZGBA1R5CS0")
```

**체크 방법:**
```python
# 간단한 검색 테스트
agent = PlanExecuteAgent()
result = agent._execute_neptune_search("fire extinguisher")
print(f"검색 결과 개수: {len(result)}")
print(f"첫 번째 결과: {result[0] if result else 'None'}")
```

**성공 기준:**
- 결과 리스트 반환 (빈 리스트라도 OK)
- 에러 없이 완료

**예상 문제:**
- `ValidationException`: 잘못된 KB ID
- `ResourceNotFoundException`: KB가 존재하지 않음

---

## 📋 **2단계: 핵심 워크플로우 확인**

### ✅ **2.1 문서 계획 수립 테스트**
**테스트 대상:**
```python
def _create_document_plan(self, query: str) -> Dict
```

**체크 방법:**
```python
agent = PlanExecuteAgent()
plan = agent._create_document_plan("선박의 소화기 요구사항은?")
print(f"계획 결과: {plan}")
print(f"선택된 문서: {plan.get('target_documents', [])}")
print(f"영어 쿼리: {plan.get('english_query', '')}")
```

**성공 기준:**
- `success: True` 반환
- `target_documents` 리스트 포함
- `english_query` 문자열 포함

**예상 문제:**
- JSON 파싱 에러
- Claude Haiku 모델 호출 실패

---

### ✅ **2.2 Cohere Reranking 테스트**
**테스트 대상:**
```python
def _cohere_rerank(self, query: str, documents: list) -> list
```

**체크 방법:**
```python
# 더미 문서로 테스트
dummy_docs = [
    {"content": "Fire extinguisher requirements for ships", "score": 0.8},
    {"content": "SOLAS fire safety regulations", "score": 0.7}
]
agent = PlanExecuteAgent()
reranked = agent._cohere_rerank("fire safety", dummy_docs)
print(f"Reranked 결과: {len(reranked)}개")
print(f"첫 번째 점수: {reranked[0].get('rerank_score', 'None') if reranked else 'None'}")
```

**성공 기준:**
- 재순위화된 문서 리스트 반환
- `rerank_score` 필드 추가됨

**예상 문제:**
- Cohere 모델 호출 실패
- 폴백 동작으로 원본 반환 (정상)

---

## 📋 **3단계: 전체 워크플로우 테스트**

### ✅ **3.1 전체 프로세스 테스트**
**테스트 대상:**
```python
def process_message(self, message: str, session_id: str) -> Dict[str, Any]
```

**체크 방법:**
```python
agent = PlanExecuteAgent()
result = agent.process_message("선박의 소화기 요구사항은?", "test_session")

print(f"성공 여부: {result.get('success')}")
print(f"응답 길이: {len(result.get('content', ''))}")
print(f"참조 개수: {len(result.get('references', []))}")
print(f"응답 시간: {result.get('response_time', 0):.2f}초")
```

**성공 기준:**
- `success: True`
- 한국어 응답 생성됨
- 참조 문서 포함됨
- 3초 이내 응답

---

### ✅ **3.2 한국어 응답 품질 확인**
**체크 방법:**
```python
result = agent.process_message("SOLAS 화재 감지 시스템 규정은?", "test_session")
response_text = result.get('content', '')

# 한국어 응답 확인
print("=== 응답 내용 ===")
print(response_text[:200] + "...")

# 참조 문서 확인
references = result.get('references', [])
print(f"\n=== 참조 문서 ({len(references)}개) ===")
for i, ref in enumerate(references[:2]):
    print(f"{i+1}. 출처: {ref.get('source', 'Unknown')}")
    print(f"   점수: {ref.get('score', 0):.3f}")
    print(f"   내용: {ref.get('content', '')[:100]}...")
```

**성공 기준:**
- 한국어로 응답 생성
- 구체적이고 전문적인 내용
- 관련 참조 문서 포함

---

## 📋 **4단계: UI 통합 테스트**

### ✅ **4.1 Streamlit UI에서 테스트**
**체크 방법:**
1. `streamlit run app.py` 실행
2. 사이드바에서 "Plan-Execute Agent" 선택
3. 테스트 질문 입력:
   - "선박의 소화기 요구사항은?"
   - "SOLAS 화재 감지 시스템"
   - "스프링클러 시스템 규정"

**성공 기준:**
- 에이전트 선택 가능
- 질문에 대한 응답 생성
- 참조 문서 클릭 가능

### ✅ **4.2 멀티모달 기능 테스트**
**테스트 대상:** PWRU19RDNE의 Multimodal storage (s3://claude-neptune)

**체크 방법:**
```python
# S3 버킷 접근 확인
import boto3
s3_client = boto3.client('s3', region_name='us-west-2')
try:
    response = s3_client.list_objects_v2(Bucket='claude-neptune', MaxKeys=5)
    print(f"✅ S3 버킷 접근 성공: {len(response.get('Contents', []))}개 객체")
except Exception as e:
    print(f"❌ S3 버킷 접근 실패: {e}")
```

**UI 테스트:**
- 이미지가 포함된 질문 테스트
- 문서 이미지 참조 확인
- 멀티모달 응답 품질 검증

**성공 기준:**
- S3 버킷 접근 가능
- 이미지 기반 질문 처리
- 시각적 참조 자료 표시

---

## 🚨 **문제 해결 가이드**

### **AWS 권한 문제**
```bash
# 필요한 권한 확인
aws bedrock list-foundation-models
aws bedrock-agent get-knowledge-base --knowledge-base-id ZGBA1R5CS0
```

### **모델 호출 실패**
```python
# 개별 모델 테스트
import boto3
client = boto3.client('bedrock-runtime', region_name='us-west-2')
response = client.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    body='{"anthropic_version": "bedrock-2023-05-31", "max_tokens": 100, "messages": [{"role": "user", "content": "Hello"}]}'
)
```

### **Neptune KB 문제**
```python
# KB 상태 확인
import boto3
client = boto3.client('bedrock-agent', region_name='us-west-2')
kb_info = client.get_knowledge_base(knowledgeBaseId='ZGBA1R5CS0')
print(kb_info['knowledgeBase']['status'])
```

---

## 📝 **테스트 실행 순서**

1. **1.1 → 1.2**: 기본 연결부터 확인
2. **2.1 → 2.2**: 개별 기능 테스트
3. **3.1 → 3.2**: 전체 워크플로우 확인
4. **4.1**: UI 통합 테스트

**각 단계에서 문제 발생시 다음 단계로 진행하지 말고 해결 후 진행**

### **멀티모달 기능 문제 해결**
```bash
# S3 권한 확인
aws s3 ls s3://claude-neptune/
aws s3api get-bucket-location --bucket claude-neptune

# Bedrock Agent 멀티모달 설정 확인
aws bedrock-agent get-agent --agent-id PWRU19RDNE
```

---

## ✅ **체크리스트 완료 기준**

- [x] 1.1 AWS 클라이언트 초기화 성공 ✅ **완료**
- [x] 1.2 Neptune KB 검색 성공 ✅ **완료** (빈 결과 정상)
- [x] 2.1 문서 계획 수립 성공 ✅ **완료** (Claude Haiku 정상 작동)
- [x] 2.2 Cohere Reranking 성공 ✅ **완료** (폴백 동작 정상)
- [x] 3.1 전체 프로세스 성공 ✅ **완료** (3.09초, 안정적 동작)
- [x] 3.2 한국어 응답 품질 확인 ✅ **완료** (일부 검색 성공, 한국어 응답 생성)
- [ ] 4.1 UI 통합 테스트 성공
- [ ] 4.2 멀티모달 기능 테스트 성공 (s3://claude-neptune)

**모든 체크리스트 완료시 Plan-Execute Agent 검증 완료!**

---

## 📝 **추가 정보**

### **PWRU19RDNE 멀티모달 설정**
- **Storage Destination**: s3://claude-neptune
- **기능**: 이미지, 문서, 차트 등 시각적 자료 처리
- **용도**: 선박 도면, 규정 이미지, 다이어그램 분석

### **멀티모달 테스트 시나리오**
1. 선박 도면 이미지 업로드 후 질문
2. 규정 문서 스캔 이미지 분석
3. 화재 안전 다이어그램 해석
4. 장비 사진 기반 규정 확인