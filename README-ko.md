# 🚢 선박 소방 규정 챗봇

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Neptune-orange.svg)](https://aws.amazon.com)

선박 소방 규정을 위한 정교한 멀티 에이전트 GraphRAG 기반 챗봇 시스템으로, 대화형 지식 그래프 시각화 및 실시간 데이터 탐색 기능을 제공합니다.

## 🌟 주요 기능

- **🤖 멀티 에이전트 아키텍처**: AWS Bedrock 통합 Plan-Execute 에이전트
- **🕸️ 대화형 지식 그래프**: Neptune Analytics GraphRAG + FSS SPARQL 온톨로지
- **📊 데이터 구조 가이드**: 포괄적인 시스템 아키텍처 시각화
- **💬 지능형 채팅**: 한국어/영어 지원 및 문서 참조 기능
- **🔍 고급 검색**: 엔티티 추출 기능을 갖춘 Lambda 기반 GraphRAG 도구

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.11+
- Bedrock 액세스 권한이 있는 AWS 계정
- AWS CLI 구성 완료

### 설치

```bash
# 1. 클론 및 설정
git clone <repository-url>
cd shi-graphrag-chatbot
python -m venv venv
source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 설정
cp .env.example .env
# .env 파일에 AWS 리소스 ID 입력

# 4. 애플리케이션 실행
streamlit run app.py
```

## 📁 프로젝트 구조

```
shi-graphrag-chatbot/
├── 📱 핵심 애플리케이션
│   ├── app.py                      # 메인 Streamlit 앱
│   ├── data_structure_guide.py     # 시스템 아키텍처 가이드
│   ├── knowledge_graph.py          # Neptune Analytics 뷰어
│   └── fss_full_graph.py          # FSS SPARQL 온톨로지
│
├── 🤖 멀티 에이전트 시스템
│   ├── core/agent_manager.py       # 에이전트 관리
│   ├── agents/
│   │   ├── base_agent.py           # 베이스 에이전트 클래스
│   │   └── plan_execute_agent/     # 메인 에이전트 구현
│   └── config/agents.yaml          # 에이전트 설정
│
├── 🎨 사용자 인터페이스
│   └── ui/
│       ├── sidebar.py              # 네비게이션
│       ├── chat_interface.py       # 채팅 UI
│       ├── reference_display.py    # 문서 뷰어
│       └── agent_selector.py       # 에이전트 선택
│
├── ⚡ Lambda 함수
│   └── lambda_package/
│       ├── graphrag_tools/         # GraphRAG Lambda 도구
│       └── lambda_function.py      # 메인 Lambda 핸들러
│
├── 📚 문서
│   └── doc/                        # 모든 문서 파일
│
└── 🚀 배포
    └── deployment/                 # AWS 배포 설정
```

## 🎯 사용법

### 💬 채팅 인터페이스
1. 사이드바에서 "💬 채팅" 선택
2. 드롭다운에서 에이전트 선택
3. 한국어 또는 영어로 질문
4. 참조 번호를 클릭하여 원본 문서 확인

### 🕸️ 지식 그래프
1. 사이드바에서 "🕸️ 지식 그래프" 선택
2. 다음 중 선택:
   - **GraphRAG**: Neptune Analytics (7,552개 노드)
   - **FSS 온톨로지**: SPARQL 의미 그래프 (653개 트리플)

### 📊 데이터 구조 가이드
1. 사이드바에서 "📊 데이터 구조 안내서" 선택
2. 시스템 아키텍처 및 통계 탐색

## ⚙️ 설정

### 환경 변수
```bash
# .env
AWS_REGION=us-west-2
BEDROCK_AGENT_ID=WT3ZJ25XCL
BEDROCK_ALIAS_ID=3RWZZLJDY1
KNOWLEDGE_BASE_ID=ZGBA1R5CS0
NEPTUNE_GRAPH_ID=g-goxs5d7fi3
NEPTUNE_ENDPOINT=your-neptune-endpoint
```

### 에이전트 설정
```yaml
# config/agents.yaml
agents:
  plan_execute:
    display_name: "Plan Execute Agent"
    description: "GraphRAG를 활용한 고급 추론 에이전트"
    bedrock_agent_id: "WT3ZJ25XCL"
    bedrock_alias_id: "3RWZZLJDY1"
    enabled: true
```

## 🔧 개발

### 새 에이전트 추가
1. 에이전트 디렉토리 생성: `agents/new_agent/`
2. `BaseAgent`를 확장하는 `Agent` 클래스 구현
3. `config/agents.yaml` 업데이트

### Lambda 도구
시스템에는 Lambda 기반 GraphRAG 도구가 포함되어 있습니다:
- **classify_query**: 쿼리 분류
- **extract_entities**: 엔티티 추출
- **kb_retrieve**: 지식 베이스 검색

## 🚀 배포

### 로컬 개발
```bash
streamlit run app.py --server.port 8501
```

### AWS 프로덕션
```bash
# Application Load Balancer로 배포
aws cloudformation deploy \
    --template-file deployment/alb-streamlit.yaml \
    --stack-name streamlit-alb
```

## 📊 시스템 메트릭

- **지식 베이스**: 10,000+ 문서 청크
- **Neptune Analytics**: 7,552개 노드, 11,949개 관계
- **SPARQL 온톨로지**: 653개 트리플, 42개 클래스
- **응답 시간**: 평균 3초 미만

## 📚 문서

`/doc` 폴더의 포괄적인 문서:

- **[시스템 개요](doc/SYSTEM_OVERVIEW.md)** - 아키텍처 개요
- **[설정 가이드](doc/CONFIGURATION_GUIDE.md)** - 설정 지침
- **[에이전트 개발](doc/AGENT_DEVELOPMENT.md)** - 에이전트 개발 가이드
- **[문제 해결](doc/troubleshooting-ko.md)** - 문제 해결
- **[멀티 에이전트 시스템](doc/multi_agent_system-ko.md)** - 아키텍처 세부사항

영어 버전도 제공됩니다.

## 🛠️ 테스트 및 디버깅

사용 가능한 테스트 유틸리티:
- `test_simple.py` - 기본 기능 테스트
- `test_full_workflow.py` - 엔드투엔드 테스트
- `debug_aws_resources.py` - AWS 리소스 상태 확인

## 🔒 보안

- **읽기 전용 작업**: 데이터 수정 방지
- **IAM 역할**: 최소 권한 액세스
- **입력 검증**: 쿼리 안전성 확인
- **감사 로깅**: CloudTrail 통합

## 🤝 기여

1. 저장소 포크
2. 기능 브랜치 생성: `git checkout -b feature/new-feature`
3. 코드 표준 준수 및 테스트 추가
4. 문서 업데이트
5. 풀 리퀘스트 제출

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 라이선스가 부여됩니다.

## 🆘 지원

- **이슈**: 버그에 대한 GitHub 이슈 생성
- **문서**: `/doc` 디렉토리 확인
- **문제 해결**: [문제 해결 가이드](doc/troubleshooting-ko.md) 참조

---

**해양 안전 전문가를 위해 ❤️로 제작**