# ⚙️ 설정 가이드

## 📋 목차
- [환경 변수 설정](#환경-변수-설정)
- [에이전트 설정](#에이전트-설정)
- [AWS 리소스 설정](#aws-리소스-설정)
- [Streamlit 설정](#streamlit-설정)
- [개발 환경 설정](#개발-환경-설정)

## 🌍 환경 변수 설정

### `.env` 파일 생성
```bash
cp .env.example .env
```

### 필수 환경 변수

#### **AWS 기본 설정**
```bash
# AWS 리전 (고정)
AWS_REGION=us-west-2

# AWS 자격증명 (aws configure로 설정 권장)
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
```

#### **Bedrock Agent 설정**
```bash
# Plan-Execute Agent (기본)
BEDROCK_AGENT_ID=WT3ZJ25XCL
BEDROCK_AGENT_ALIAS_ID=3RWZZLJDY1
```

#### **Knowledge Base 설정**
```bash
# BDA Knowledge Base (기본)
KNOWLEDGE_BASE_ID=CDPB5AI6BH

# Claude Knowledge Base (멀티모달)
CLAUDE_KB_ID=PWRU19RDNE
```

#### **Neptune 설정**
```bash
# Neptune Analytics 그래프 ID들
NEPTUNE_BDA_GRAPH_ID=g-goxs5d7fi3      # BDA 그래프
NEPTUNE_CLAUDE_GRAPH_ID=g-ryb6suoa69   # Claude 그래프

# Neptune SPARQL 엔드포인트 (FSS 온톨로지용)
NEPTUNE_ENDPOINT=your-neptune-cluster.cluster-xxx.us-west-2.neptune.amazonaws.com
```

#### **S3 설정**
```bash
# 멀티모달 스토리지
S3_MULTIMODAL_BUCKET=claude-neptune

# 문서 스토리지 (선택적)
S3_DOCUMENT_BUCKET=your-document-bucket
```

### 환경 변수 설명

| 변수명 | 설명 | 필수 여부 | 기본값 |
|--------|------|-----------|--------|
| `AWS_REGION` | AWS 리전 | ✅ | us-west-2 |
| `BEDROCK_AGENT_ID` | 기본 Bedrock Agent ID | ✅ | WT3ZJ25XCL |
| `BEDROCK_ALIAS_ID` | 기본 Agent Alias ID | ✅ | 3RWZZLJDY1 |
| `KNOWLEDGE_BASE_ID` | 기본 Knowledge Base ID | ✅ | CDPB5AI6BH |
| `NEPTUNE_BDA_GRAPH_ID` | BDA Neptune 그래프 ID | ✅ | g-goxs5d7fi3 |
| `NEPTUNE_CLAUDE_GRAPH_ID` | Claude Neptune 그래프 ID | ✅ | g-ryb6suoa69 |
| `NEPTUNE_ENDPOINT` | Neptune SPARQL 엔드포인트 | ⚠️ | - |
| `S3_MULTIMODAL_BUCKET` | 멀티모달 S3 버킷 | ⚠️ | claude-neptune |

**범례**: ✅ 필수, ⚠️ 선택적 (기능에 따라 필요)

## 🤖 에이전트 설정

### `config/agents.yaml` 구조

```yaml
agents:
  # Plan-Execute Agent (기본)
  plan_execute:
    display_name: "⚡ Plan-Execute Agent"
    description: "AWS IDP 패턴 기반 단순화된 GraphRAG 에이전트"
    bedrock_agent_id: "WT3ZJ25XCL"
    bedrock_alias_id: "3RWZZLJDY1"
    knowledge_base_id: "CDPB5AI6BH"
    region: "us-west-2"
    enabled: true
    ui_config:
      icon: "⚡"
      color: "#FF6B35"
    
  # 미래 확장용 예시
  # future_agent:
  #   display_name: "🔮 Future Agent"
  #   description: "미래 기능을 위한 에이전트"
  #   bedrock_agent_id: "YOUR_AGENT_ID"
  #   bedrock_alias_id: "YOUR_ALIAS_ID"
  #   knowledge_base_id: "YOUR_KB_ID"
  #   region: "us-west-2"
  #   enabled: false
  #   ui_config:
  #     icon: "🔮"
  #     color: "#9B59B6"
```

### 에이전트 설정 항목 설명

#### **기본 설정**
- `display_name`: UI에 표시될 에이전트 이름
- `description`: 에이전트 설명 (사이드바에 표시)
- `enabled`: 에이전트 활성화 여부

#### **AWS 리소스**
- `bedrock_agent_id`: AWS Bedrock Agent ID
- `bedrock_alias_id`: Agent Alias ID
- `knowledge_base_id`: 연결된 Knowledge Base ID
- `region`: AWS 리전

#### **UI 설정**
- `ui_config.icon`: 에이전트 아이콘 (이모지)
- `ui_config.color`: 테마 색상 (선택적)

### 새 에이전트 추가 방법

1. **에이전트 구현**
```bash
mkdir -p agents/new_agent
touch agents/new_agent/__init__.py
touch agents/new_agent/agent.py
```

2. **에이전트 클래스 구현**
```python
# agents/new_agent/agent.py
from agents.base_agent import BaseAgent

class Agent(BaseAgent):
    def process_message(self, message: str, session_id: str, **kwargs) -> Dict:
        # 에이전트 로직 구현
        return {
            "success": True,
            "content": "응답 내용",
            "references": []
        }
```

3. **설정 추가**
```yaml
# config/agents.yaml에 추가
agents:
  new_agent:
    display_name: "🆕 New Agent"
    description: "새로운 에이전트 설명"
    bedrock_agent_id: "YOUR_AGENT_ID"
    bedrock_alias_id: "YOUR_ALIAS_ID"
    knowledge_base_id: "YOUR_KB_ID"
    enabled: true
```

## ☁️ AWS 리소스 설정

### Bedrock Agent 설정

#### **1. Agent 생성**
```bash
# AWS CLI로 확인
aws bedrock-agent get-agent --agent-id WT3ZJ25XCL --region us-west-2
```

#### **2. Knowledge Base 연결**
```bash
# BDA KB 상태 확인
aws bedrock-agent get-knowledge-base --knowledge-base-id CDPB5AI6BH --region us-west-2

# Claude KB 상태 확인
aws bedrock-agent get-knowledge-base --knowledge-base-id PWRU19RDNE --region us-west-2
```

#### **3. 필요한 IAM 권한**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeAgent",
                "bedrock:InvokeModel",
                "bedrock-agent:*",
                "bedrock-agent-runtime:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### Neptune 설정

#### **1. Neptune Analytics**
```bash
# 그래프 상태 확인
aws neptune-graph get-graph --graph-identifier g-goxs5d7fi3 --region us-west-2
```

#### **2. Neptune SPARQL (선택적)**
```bash
# 클러스터 엔드포인트 확인
aws neptune describe-db-clusters --region us-west-2
```

### S3 설정

#### **1. 멀티모달 버킷**
```bash
# 버킷 접근 확인
aws s3 ls s3://claude-neptune/ --region us-west-2
```

#### **2. 필요한 S3 권한**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::claude-neptune",
                "arn:aws:s3:::claude-neptune/*"
            ]
        }
    ]
}
```

## 🖥️ Streamlit 설정

### `.streamlit/config.toml`

```toml
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[logger]
level = "info"
```

### 설정 항목 설명

#### **서버 설정**
- `port`: 서버 포트 (기본: 8501)
- `address`: 바인딩 주소 (0.0.0.0 = 모든 인터페이스)
- `maxUploadSize`: 최대 업로드 크기 (MB)

#### **브라우저 설정**
- `gatherUsageStats`: 사용 통계 수집 (false 권장)
- `serverAddress`: 브라우저에서 접근할 주소

#### **테마 설정**
- `primaryColor`: 주요 색상 (버튼, 링크)
- `backgroundColor`: 배경 색상
- `textColor`: 텍스트 색상

## 🛠️ 개발 환경 설정

### Python 환경

#### **1. 가상환경 생성**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

#### **2. 의존성 설치**
```bash
pip install -r requirements.txt
```

#### **3. 개발 의존성 (선택적)**
```bash
pip install -r requirements-dev.txt  # 있는 경우
```

### AWS 자격증명 설정

#### **방법 1: AWS CLI (권장)**
```bash
aws configure
# AWS Access Key ID: your_access_key
# AWS Secret Access Key: your_secret_key
# Default region name: us-west-2
# Default output format: json
```

#### **방법 2: 환경변수**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

#### **방법 3: IAM Role (EC2)**
EC2 인스턴스에서 실행 시 IAM Role 사용 권장

### 개발 서버 실행

```bash
# 기본 실행
streamlit run app.py

# 포트 지정
streamlit run app.py --server.port 8502

# 디버그 모드
streamlit run app.py --logger.level debug
```

### 환경별 설정

#### **로컬 개발**
```bash
# .env.local
DEBUG=true
LOG_LEVEL=debug
STREAMLIT_SERVER_PORT=8501
```

#### **스테이징**
```bash
# .env.staging
DEBUG=false
LOG_LEVEL=info
STREAMLIT_SERVER_PORT=8501
```

#### **프로덕션**
```bash
# .env.production
DEBUG=false
LOG_LEVEL=warning
STREAMLIT_SERVER_PORT=8501
```

## 🔍 설정 검증

### 설정 확인 스크립트

```python
# check_config.py
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def check_aws_config():
    """AWS 설정 확인"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS 인증 성공: {identity['Arn']}")
    except Exception as e:
        print(f"❌ AWS 인증 실패: {e}")

def check_bedrock_agent():
    """Bedrock Agent 확인"""
    try:
        client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        agent_id = os.getenv('BEDROCK_AGENT_ID')
        print(f"✅ Bedrock Agent ID: {agent_id}")
    except Exception as e:
        print(f"❌ Bedrock Agent 확인 실패: {e}")

if __name__ == "__main__":
    check_aws_config()
    check_bedrock_agent()
```

### 실행
```bash
python check_config.py
```

## 📚 관련 문서

- **[System Overview](SYSTEM_OVERVIEW.md)**: 전체 시스템 아키텍처
- **[Agent Development](AGENT_DEVELOPMENT.md)**: 새 에이전트 개발 가이드
- **[Troubleshooting](TROUBLESHOOTING.md)**: 문제 해결 가이드
- **[doc/configuration.md](doc/configuration.md)**: 상세 설정 문서

---

**마지막 업데이트**: 2024년 11월