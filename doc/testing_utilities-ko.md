# 테스트 유틸리티 문서

## 개요

이 프로젝트는 챗봇 시스템의 테스트 및 디버깅을 위한 여러 유틸리티 스크립트를 포함합니다. 이러한 도구는 기능 확인, 참조 추출, 시스템 동작 분석에 도움이 됩니다.

## 테스트 스크립트

### 1. test_agent_trace.py

**목적**: 상세한 추적 분석을 통한 Bedrock Agent의 포괄적인 테스트입니다.

#### 기능
- **전체 추적 분석**: Bedrock Agent의 모든 추적 이벤트 캡처 및 분석
- **참조 추출**: Knowledge Base 참조 식별 및 표시
- **이벤트 구조 분석**: 추적 이벤트의 구조 검사
- **디버그 출력**: Agent 상호작용 흐름의 상세한 로깅

#### 주요 기능
```python
# 메인 테스트 함수
def test_agent_with_trace():
    # 추적이 활성화된 상태로 Agent 호출
    response = client.invoke_agent(
        agentId='WT3ZJ25XCL',
        agentAliasId='3RWZZLJDY1',
        sessionId=session_id,
        inputText='선박 설계시 firefighting 규칙에 대해 알려주세요',
        enableTrace=True
    )
```

#### 출력 분석
- **완료 텍스트**: 최종 Agent 응답
- **추적 이벤트**: 각 추적 이벤트의 상세한 분석
- **Knowledge Base 조회**: 검색 중 발견된 참조
- **오케스트레이션 흐름**: 단계별 Agent 추론 과정

#### 사용법
```bash
python test_agent_trace.py
```

### 2. extract_references.py

**목적**: Agent 응답에서 참조 정보를 추출하고 분석합니다.

#### 기능
- **참조 파싱**: Agent 추적 데이터에서 참조 추출
- **콘텐츠 분석**: 참조 콘텐츠 및 메타데이터 분석
- **Base64 디코딩**: 참조의 바이트 콘텐츠 처리
- **구조화된 출력**: 참조 정보의 체계적인 표시

#### 참조 데이터 구조
```python
ref_data = {
    'content': content_text,
    'source_file': ref.get('metadata', {}).get('x-amz-bedrock-kb-source-uri', ''),
    'page_number': ref.get('metadata', {}).get('x-amz-bedrock-kb-document-page-number', 0),
    'description': ref.get('metadata', {}).get('x-amz-bedrock-kb-description', '')
}
```

#### 콘텐츠 처리
- **텍스트 콘텐츠**: 참조에서 직접 텍스트 추출
- **바이트 콘텐츠**: 바이너리 콘텐츠를 위한 Base64 디코딩
- **오류 처리**: 디코드 오류의 우아한 처리
- **콘텐츠 미리보기**: 각 참조의 처음 500자 표시

#### 사용법
```bash
python extract_references.py
```

### 3. get_kb_text.py

**목적**: Knowledge Base 검색 기능의 직접 테스트입니다.

#### 기능
- **직접 KB 액세스**: Agent를 우회하여 Knowledge Base를 직접 테스트
- **벡터 검색**: 벡터 검색 구성 사용
- **결과 분석**: 검색 결과의 상세한 분석
- **메타데이터 추출**: 사용 가능한 모든 메타데이터 추출

#### 검색 구성
```python
response = client.retrieve(
    knowledgeBaseId='ZGBA1R5CS0',
    retrievalQuery={
        'text': 'firefighting 고정식 소화 시스템'
    },
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 3
        }
    }
)
```

#### 결과 처리
- **점수 분석**: 각 결과의 관련성 점수 표시
- **콘텐츠 추출**: 결과에서 텍스트 콘텐츠 표시
- **위치 정보**: S3 위치 세부사항
- **OCR 텍스트**: 문서 메타데이터에서 추출된 OCR 텍스트
- **이미지 URI**: 원본 문서 이미지 위치

#### 사용법
```bash
python get_kb_text.py
```

## 테스트 데이터 파일

### payload.txt
Lambda 함수 테스트를 위한 샘플 입력 페이로드를 포함합니다.

### test_payload.json
구조화된 테스트를 위한 JSON 형식의 테스트 페이로드입니다.

### response.json
참조 및 비교를 위한 샘플 응답 데이터입니다.

## 디버깅 기능

### 추적 이벤트 분석
모든 테스트 유틸리티는 상세한 추적 이벤트 분석을 제공합니다:

#### 이벤트 유형
- **오케스트레이션 추적**: 메인 Agent 추론 흐름
- **Knowledge Base 조회**: 검색 작업
- **관찰 이벤트**: Agent 관찰 및 결정
- **액션 이벤트**: 도구 호출 및 응답

#### 데이터 추출
- **참조 메타데이터**: 완전한 메타데이터 추출
- **콘텐츠 처리**: 텍스트 및 바이너리 콘텐츠 처리
- **위치 추적**: S3 URI 및 문서 위치
- **점수 분석**: 관련성 점수 정보

### 오류 처리
모든 유틸리티에서 포괄적인 오류 처리:

```python
try:
    # 메인 테스트 로직
    response = client.invoke_agent(...)
    # 응답 처리
except Exception as e:
    print(f"Error: {e}")
    return "", []
```

## 출력 형식

### 콘솔 출력
모든 유틸리티는 구조화된 콘솔 출력을 제공합니다:

```
=== AGENT RESPONSE ===
[Agent 응답 텍스트]

=== EXTRACTED REFERENCES (N) ===
[1] 참조 문서:
파일: document.pdf
페이지: 1
참조 텍스트 (처음 500자):
[콘텐츠 미리보기...]
총 길이: 1234 문자
```

### JSON 출력
프로그래밍 방식 사용을 위한 구조화된 데이터 출력:

```json
{
    "completion": "Agent 응답",
    "references": [
        {
            "source_file": "document.pdf",
            "page_number": 1,
            "content": "참조 텍스트",
            "description": "OCR 추출 텍스트"
        }
    ]
}
```

## 성능 테스트

### 응답 시간 분석
- **Agent 호출 시간**: Agent 응답을 받는 시간
- **참조 처리 시간**: 참조를 추출하는 시간
- **총 처리 시간**: 종단 간 처리 시간

### 메모리 사용량
- **콘텐츠 크기 분석**: 추출된 콘텐츠의 크기
- **참조 수**: 질의당 참조 수
- **메타데이터 크기**: 메타데이터 정보의 크기

## 통합 테스트

### 종단 간 테스트
1. **Agent 호출**: 완전한 Agent 워크플로 테스트
2. **참조 추출**: 참조 처리 확인
3. **콘텐츠 표시**: 콘텐츠 렌더링 테스트
4. **오류 시나리오**: 오류 처리 테스트

### 구성 요소 테스트
1. **Knowledge Base**: 직접 KB 테스트
2. **Lambda 함수**: 개별 함수 테스트
3. **추적 처리**: 추적 이벤트 처리
4. **콘텐츠 처리**: 참조 콘텐츠 처리

## 사용 권장사항

### 개발 워크플로
1. **get_kb_text.py로 시작**: Knowledge Base 연결 테스트
2. **test_agent_trace.py 사용**: Agent 통합 확인
3. **extract_references.py 실행**: 참조 처리 테스트
4. **출력 형식 확인**: 데이터 구조 검증

### 디버깅 과정
1. **AWS 자격 증명 확인**: 적절한 인증 보장
2. **리소스 ID 확인**: Agent 및 KB ID 확인
3. **네트워크 연결 테스트**: 리전 및 엔드포인트 확인
4. **오류 메시지 분석**: 상세한 오류 출력 사용

### 성능 최적화
1. **응답 시간 모니터링**: 성능 메트릭 추적
2. **참조 수 분석**: 검색 매개변수 최적화
3. **콘텐츠 크기 확인**: 메모리 사용량 모니터링
4. **동시 사용 테스트**: 확장성 확인

## 일반적인 문제 및 해결책

### 인증 문제
- **해결책**: AWS 자격 증명 및 권한 확인
- **확인**: `aws sts get-caller-identity` 사용

### 리소스 액세스 문제
- **해결책**: 리소스 ID 및 리전 설정 확인
- **확인**: 리소스 상태를 위해 AWS 콘솔 확인

### 콘텐츠 처리 문제
- **해결책**: 인코딩 및 콘텐츠 유형 확인
- **확인**: 콘텐츠 구조 분석을 위해 디버그 출력 사용

### 성능 문제
- **해결책**: 검색 매개변수 및 결과 수 최적화
- **확인**: CloudWatch 메트릭 모니터링