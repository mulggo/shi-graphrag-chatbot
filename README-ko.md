# 선박 소화 규칙 챗봇

AWS Bedrock Agent와 Strands 프레임워크를 사용한 선박 소화 규정 GraphRAG 기반 챗봇 시스템입니다.

## 개요

이 프로젝트는 선박 소화 규정, 특히 SOLAS(해상인명안전협약) 표준과 DNV-RU-SHIP 규칙에 대한 정보를 제공하는 지능형 챗봇을 구현합니다. 시스템은 AWS Bedrock Agent와 Knowledge Base 통합, 그리고 향상된 검색 기능을 위한 Strands ReAct 패턴을 사용합니다.

## 주요 기능

- **대화형 Streamlit 웹 인터페이스**: 한국어 지원이 포함된 사용자 친화적 채팅 인터페이스
- **AWS Bedrock Agent 통합**: 지능적인 응답을 위한 AWS Bedrock Agent 활용
- **Knowledge Base 검색**: 선박 소화 규정 문서에서 정보 검색
- **참조 문서 표시**: OCR 텍스트와 원본 이미지가 포함된 소스 문서 표시
- **Strands ReAct 패턴**: ReAct(추론 및 행동) 방법론을 사용한 고급 검색
- **다국어 지원**: 한국어 및 영어 문서 지원

## 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Bedrock Agent  │    │  Knowledge Base │
│   Frontend      │───▶│   (H5YNZKKNSW)   │───▶│   (ZGBA1R5CS0)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Lambda Function │
                       │  (Strands Tool)  │
                       └──────────────────┘
```

## 프로젝트 구조

```
shi-graphrag-chatbot/
├── app.py                          # 메인 Streamlit 애플리케이션
├── lambda_package/                 # Lambda 함수 패키지
│   ├── lambda_function.py         # Strands ReAct 검색 도구
│   └── requirements.txt           # Lambda 의존성
├── layer/                         # 의존성이 포함된 Lambda 레이어
├── lambda_layer/                  # 추가 Lambda 레이어
├── extract_references.py         # 참조 추출 유틸리티
├── get_kb_text.py                # Knowledge Base 테스트 유틸리티
├── test_agent_trace.py           # Agent 추적 테스트 스크립트
├── simple_lambda.py              # 간단한 테스트 Lambda
├── strands_tool_lambda.py        # Strands 도구 구현
├── strands_tool_schema.json      # Strands 도구용 OpenAPI 스키마
├── lambda_trust_policy.json      # Lambda용 IAM 신뢰 정책
└── doc/                          # 문서 디렉토리
```

## 빠른 시작

### 사전 요구사항

- Bedrock 액세스가 가능한 AWS 계정
- Python 3.11+
- Streamlit
- 구성된 AWS CLI

### 설치

1. 저장소 복제:
```bash
git clone <repository-url>
cd shi-graphrag-chatbot
```

2. 의존성 설치:
```bash
pip install streamlit boto3 strands-agents
```

3. AWS 자격 증명 구성:
```bash
aws configure
```

4. Streamlit 애플리케이션 실행:
```bash
streamlit run app.py
```

## 구성

### AWS 리소스

- **Bedrock Agent ID**: `H5YNZKKNSW`
- **Agent Alias ID**: `FD3LV7TEN4`
- **Knowledge Base ID**: `ZGBA1R5CS0`
- **리전**: `us-west-2`

### 환경 변수

추가 환경 변수는 필요하지 않습니다. AWS 자격 증명은 AWS CLI 또는 IAM 역할을 통해 구성해야 합니다.

## 사용법

1. Streamlit 웹 인터페이스 열기
2. 선박 소화 규정에 대해 한국어 또는 영어로 질문
3. 소스 문서 참조가 포함된 응답 확인
4. 참조 번호를 클릭하여 원본 문서 및 OCR 텍스트 확인
5. S3에 저장된 원본 PDF 이미지 액세스

### 예시 질문

- "선박 설계시 firefighting 규칙에 대해 알려주세요"
- "고정식 소화 시스템의 요구사항은 무엇인가요?"
- "SOLAS 규정에 따른 휴대용 소화기 배치 기준"

## 개발

### Lambda 함수 배포

1. Lambda 함수 패키징:
```bash
cd lambda_package
zip -r ../lambda_function.zip .
```

2. AWS CLI 또는 콘솔을 사용하여 배포

### 테스트

기능을 확인하기 위해 테스트 스크립트 실행:

```bash
python test_agent_trace.py
python extract_references.py
python get_kb_text.py
```

## 문서

`doc/` 디렉토리에서 자세한 문서를 확인할 수 있습니다:

- [애플리케이션 문서](doc/app-ko.md)
- [Lambda 함수](doc/lambda_functions-ko.md)
- [테스트 유틸리티](doc/testing_utilities-ko.md)
- [구성 파일](doc/configuration-ko.md)

## 기여

1. 저장소 포크
2. 기능 브랜치 생성
3. 변경사항 작성 및 테스트
4. 풀 리퀘스트 제출

## 라이선스

이 프로젝트는 MIT 라이선스 하에 라이선스가 부여됩니다.

## 지원

질문이나 문제가 있으면 개발팀에 문의하거나 저장소에 이슈를 생성해 주세요.