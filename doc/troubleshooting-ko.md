# 🚨 문제 해결 가이드

## 📋 목차
- [일반적인 문제](#일반적인-문제)
- [AWS 관련 문제](#aws-관련-문제)
- [에이전트 관련 문제](#에이전트-관련-문제)
- [지식 그래프 문제](#지식-그래프-문제)
- [성능 문제](#성능-문제)
- [디버깅 도구](#디버깅-도구)

## 🔧 일반적인 문제

### 1. **애플리케이션이 시작되지 않음**

#### 증상
```bash
streamlit run app.py
# ModuleNotFoundError: No module named 'xxx'
```

#### 해결 방법
```bash
# 1. 가상환경 활성화 확인
source venv/bin/activate

# 2. 의존성 재설치
pip install -r requirements.txt

# 3. Python 경로 확인
python -c "import sys; print(sys.path)"
```

### 2. **환경 변수 로드 실패**

#### 증상
- 설정값이 None으로 표시
- AWS 리소스 접근 실패

#### 해결 방법
```bash
# 1. .env 파일 존재 확인
ls -la .env

# 2. .env 파일 내용 확인
cat .env

# 3. 환경 변수 로드 테스트
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AWS_REGION'))"
```

### 3. **포트 충돌**

#### 증상
```bash
OSError: [Errno 48] Address already in use
```

#### 해결 방법
```bash
# 1. 포트 사용 프로세스 확인
lsof -i :8501

# 2. 프로세스 종료
kill -9 <PID>

# 3. 다른 포트 사용
streamlit run app.py --server.port 8502
```

## ☁️ AWS 관련 문제

### 1. **AWS 자격증명 문제**

#### 증상
```
NoCredentialsError: Unable to locate credentials
```

#### 해결 방법
```bash
# 1. AWS CLI 설정 확인
aws configure list

# 2. 자격증명 상태 확인
aws sts get-caller-identity

# 3. 자격증명 재설정
aws configure
```

#### 권한 확인
```bash
# Bedrock 권한 확인
aws bedrock list-foundation-models --region us-west-2

# Neptune 권한 확인
aws neptune-graph list-graphs --region us-west-2

# S3 권한 확인
aws s3 ls s3://claude-neptune/
```

### 2. **Bedrock Agent 접근 실패**

#### 증상
```
AccessDeniedException: User is not authorized to perform: bedrock-agent:InvokeAgent
```

#### 해결 방법
```bash
# 1. Agent 상태 확인
aws bedrock-agent get-agent --agent-id WT3ZJ25XCL --region us-west-2

# 2. Agent Alias 확인
aws bedrock-agent get-agent-alias --agent-id WT3ZJ25XCL --agent-alias-id 3RWZZLJDY1 --region us-west-2

# 3. 필요한 IAM 정책 추가
```

#### 필요한 IAM 정책
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agent:InvokeAgent",
                "bedrock-agent-runtime:InvokeAgent",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. **Knowledge Base 접근 실패**

#### 증상
```
ValidationException: Knowledge base ZGBA1R5CS0 not found
```

#### 해결 방법
```bash
# 1. KB 존재 확인
aws bedrock-agent get-knowledge-base --knowledge-base-id ZGBA1R5CS0 --region us-west-2

# 2. KB 상태 확인
aws bedrock-agent list-knowledge-bases --region us-west-2

# 3. KB 동기화 상태 확인
aws bedrock-agent get-knowledge-base --knowledge-base-id ZGBA1R5CS0 --region us-west-2 | grep status
```

### 4. **Neptune 연결 실패**

#### 증상
```
EndpointConnectionError: Could not connect to the endpoint URL
```

#### 해결 방법
```bash
# 1. Neptune 그래프 상태 확인
aws neptune-graph get-graph --graph-identifier g-goxs5d7fi3 --region us-west-2

# 2. 네트워크 연결 확인
curl -I https://neptune-graph.us-west-2.amazonaws.com

# 3. VPC 설정 확인 (필요한 경우)
aws ec2 describe-vpcs --region us-west-2
```

## 🤖 에이전트 관련 문제

### 1. **에이전트 로드 실패**

#### 증상
- 사이드바에 에이전트가 표시되지 않음
- "사용 가능한 에이전트가 없습니다" 메시지

#### 해결 방법
```python
# 1. 에이전트 설정 확인
import yaml
with open('config/agents.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print(config)

# 2. 에이전트 클래스 임포트 테스트
from agents.plan_execute_agent.agent import Agent
agent = Agent()
print("✅ 에이전트 로드 성공")

# 3. Agent Manager 테스트
from core.agent_manager import AgentManager
manager = AgentManager()
agents = manager.get_available_agents()
print(f"로드된 에이전트: {[a.name for a in agents]}")
```

### 2. **메시지 처리 실패**

#### 증상
```
AttributeError: 'Agent' object has no attribute 'process_message'
```

#### 해결 방법
```python
# 1. 베이스 클래스 상속 확인
from agents.base_agent import BaseAgent

class Agent(BaseAgent):  # BaseAgent 상속 필수
    def process_message(self, message: str, session_id: str, **kwargs):
        # 구현 필수
        pass

# 2. 메서드 시그니처 확인
# 올바른 시그니처: process_message(self, message: str, session_id: str, **kwargs) -> Dict[str, Any]
```

### 3. **응답 형식 오류**

#### 증상
- UI에서 응답이 제대로 표시되지 않음
- 참조 문서가 나타나지 않음

#### 해결 방법
```python
# 올바른 응답 형식
def process_message(self, message: str, session_id: str, **kwargs) -> Dict[str, Any]:
    return {
        "success": True,                    # 필수: bool
        "content": "응답 내용",              # 필수: str
        "references": [                     # 선택적: List[Dict]
            {
                "source": "문서명",
                "content": "참조 내용",
                "score": 0.95,
                "metadata": {}
            }
        ],
        "metadata": {                       # 선택적: Dict
            "agent": "agent_name",
            "response_time": 1.23,
            "model_used": "claude-3-haiku"
        }
    }
```

## 🕸️ 지식 그래프 문제

### 1. **그래프가 로드되지 않음**

#### 증상
- "데이터 없음" 노드만 표시
- 그래프 로드 실패 메시지

#### 해결 방법
```python
# 1. Neptune 연결 테스트
import boto3
client = boto3.client('neptune-graph', region_name='us-west-2')

try:
    response = client.execute_query(
        graphIdentifier='g-goxs5d7fi3',
        queryString='MATCH (n) RETURN count(n) as count LIMIT 1',
        language='OPEN_CYPHER'
    )
    print("✅ Neptune 연결 성공")
except Exception as e:
    print(f"❌ Neptune 연결 실패: {e}")

# 2. 쿼리 결과 확인
import json
data = json.loads(response['payload'].read().decode('utf-8'))
print(f"노드 개수: {data}")
```

### 2. **그래프 렌더링 느림**

#### 증상
- 그래프 로딩이 10초 이상 소요
- 브라우저가 응답하지 않음

#### 해결 방법
```python
# 1. 노드 수 제한 조정
nodes_query = "MATCH (n) RETURN ... LIMIT 1000"  # 2000 → 1000으로 감소

# 2. 물리 엔진 설정 조정
net.set_options("""
var options = {
  "physics": {
    "enabled": true,
    "stabilization": {"iterations": 50}  # 100 → 50으로 감소
  }
}
""")
```

### 3. **FSS GraphDB 연결 실패**

#### 증상
```
❌ FSS 데이터를 가져올 수 없습니다.
```

#### 해결 방법
```bash
# 1. Neptune SPARQL 엔드포인트 확인
aws neptune describe-db-clusters --region us-west-2

# 2. 환경 변수 설정
export NEPTUNE_ENDPOINT=your-cluster.cluster-xxx.us-west-2.neptune.amazonaws.com

# 3. SPARQL 쿼리 테스트
curl -X POST "https://${NEPTUNE_ENDPOINT}:8182/sparql" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
```

## ⚡ 성능 문제

### 1. **응답 시간 느림 (>5초)**

#### 원인 분석
```python
# 성능 프로파일링
import time
import cProfile

def profile_agent():
    agent = PlanExecuteAgent()
    
    def test_message():
        return agent.process_message("테스트 메시지", "test_session")
    
    # 프로파일링 실행
    cProfile.run('test_message()', 'profile_output.prof')
    
    # 결과 분석
    import pstats
    stats = pstats.Stats('profile_output.prof')
    stats.sort_stats('cumulative').print_stats(10)
```

#### 해결 방법
```python
# 1. 타임아웃 설정
from botocore.config import Config

config = Config(
    read_timeout=10,
    connect_timeout=5,
    retries={'max_attempts': 2}
)

client = boto3.client('bedrock-agent-runtime', config=config)

# 2. 병렬 처리
import asyncio
import concurrent.futures

async def parallel_search():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [
            executor.submit(search_kb1, query),
            executor.submit(search_kb2, query)
        ]
        results = [task.result() for task in tasks]
    return results
```

### 2. **메모리 사용량 증가**

#### 증상
- 시간이 지날수록 메모리 사용량 증가
- 시스템이 느려짐

#### 해결 방법
```python
# 1. 세션 상태 정리
def cleanup_session():
    # 오래된 메시지 제거
    if len(st.session_state.messages) > 50:
        st.session_state.messages = st.session_state.messages[-20:]
    
    # 캐시 정리
    st.cache_data.clear()
    st.cache_resource.clear()

# 2. 메모리 모니터링
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"메모리 사용량: {memory_mb:.1f} MB")
```

## 🛠️ 디버깅 도구

### 1. **로그 레벨 설정**

```python
# 로깅 설정
import logging

# 개발 환경
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 프로덕션 환경
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### 2. **Streamlit 디버그 모드**

```bash
# 디버그 모드로 실행
streamlit run app.py --logger.level debug

# 개발자 도구에서 네트워크 탭 확인
# 브라우저 콘솔에서 에러 메시지 확인
```

### 3. **AWS 리소스 상태 확인 스크립트**

```python
# debug_aws_resources.py
import boto3
import json

def check_all_resources():
    """모든 AWS 리소스 상태 확인"""
    
    # Bedrock Agent
    try:
        client = boto3.client('bedrock-agent', region_name='us-west-2')
        agent = client.get_agent(agentId='WT3ZJ25XCL')
        print(f"✅ Bedrock Agent: {agent['agent']['agentStatus']}")
    except Exception as e:
        print(f"❌ Bedrock Agent: {e}")
    
    # Knowledge Base
    try:
        kb = client.get_knowledge_base(knowledgeBaseId='ZGBA1R5CS0')
        print(f"✅ Knowledge Base: {kb['knowledgeBase']['status']}")
    except Exception as e:
        print(f"❌ Knowledge Base: {e}")
    
    # Neptune Analytics
    try:
        neptune_client = boto3.client('neptune-graph', region_name='us-west-2')
        graph = neptune_client.get_graph(graphIdentifier='g-goxs5d7fi3')
        print(f"✅ Neptune Graph: {graph['status']}")
    except Exception as e:
        print(f"❌ Neptune Graph: {e}")

if __name__ == "__main__":
    check_all_resources()
```

### 4. **에이전트 응답 디버깅**

```python
# debug_agent_response.py
from agents.plan_execute_agent.agent import PlanExecuteAgent
import json

def debug_agent_step_by_step():
    """에이전트 단계별 디버깅"""
    agent = PlanExecuteAgent()
    query = "선박의 소화기 요구사항은?"
    
    print("=== 1단계: 문서 계획 수립 ===")
    plan = agent._create_document_plan(query)
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    
    print("\n=== 2단계: Neptune 검색 ===")
    if plan.get('success'):
        english_query = plan.get('english_query', query)
        search_results = agent._execute_neptune_search(english_query)
        print(f"검색 결과: {len(search_results)}개")
        
        print("\n=== 3단계: Cohere 재순위화 ===")
        if search_results:
            reranked = agent._cohere_rerank(english_query, search_results)
            print(f"재순위화 결과: {len(reranked)}개")
            
            if reranked:
                print(f"최고 점수: {reranked[0].get('rerank_score', 'N/A')}")

if __name__ == "__main__":
    debug_agent_step_by_step()
```

## 📊 성능 모니터링

### 시스템 메트릭 확인

```python
# monitor_system.py
import psutil
import time
from datetime import datetime

def monitor_performance():
    """시스템 성능 모니터링"""
    
    while True:
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        print(f"[{datetime.now()}] CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent}%")
        
        # 임계값 확인
        if cpu_percent > 80:
            print("⚠️ CPU 사용률 높음")
        if memory_percent > 80:
            print("⚠️ 메모리 사용률 높음")
        
        time.sleep(10)

if __name__ == "__main__":
    monitor_performance()
```

## 🆘 긴급 복구 절차

### 1. **시스템 전체 재시작**

```bash
# 1. Streamlit 프로세스 종료
pkill -f streamlit

# 2. 가상환경 재활성화
source venv/bin/activate

# 3. 의존성 확인
pip check

# 4. 애플리케이션 재시작
streamlit run app.py
```

### 2. **설정 초기화**

```bash
# 1. 환경 변수 백업
cp .env .env.backup

# 2. 기본 설정으로 복원
cp .env.example .env

# 3. 필수 값만 설정
echo "AWS_REGION=us-west-2" >> .env
echo "BEDROCK_AGENT_ID=WT3ZJ25XCL" >> .env
echo "BEDROCK_ALIAS_ID=3RWZZLJDY1" >> .env
```

### 3. **Git 상태 복원**

```bash
# 1. 현재 상태 백업
git stash

# 2. 마지막 안정 버전으로 복원
git log --oneline -5
git reset --hard <안정_버전_해시>

# 3. 변경사항 재적용 (필요한 경우)
git stash pop
```

## 📞 지원 요청

### 문제 보고 시 포함할 정보

1. **환경 정보**
   - OS 및 Python 버전
   - 설치된 패키지 버전 (`pip freeze`)
   - AWS 리전 및 리소스 ID

2. **에러 로그**
   - 전체 에러 스택 트레이스
   - Streamlit 로그 (`streamlit.log`)
   - 브라우저 콘솔 에러

3. **재현 단계**
   - 문제 발생 전 수행한 작업
   - 입력한 메시지나 설정
   - 예상 결과 vs 실제 결과

### 로그 수집 스크립트

```bash
# collect_logs.sh
#!/bin/bash

echo "=== 시스템 정보 ===" > debug_info.txt
python --version >> debug_info.txt
pip freeze >> debug_info.txt

echo -e "\n=== 환경 변수 ===" >> debug_info.txt
env | grep -E "(AWS|BEDROCK|NEPTUNE)" >> debug_info.txt

echo -e "\n=== Streamlit 로그 ===" >> debug_info.txt
tail -100 streamlit.log >> debug_info.txt 2>/dev/null || echo "streamlit.log 없음" >> debug_info.txt

echo -e "\n=== 에이전트 설정 ===" >> debug_info.txt
cat config/agents.yaml >> debug_info.txt

echo "디버그 정보가 debug_info.txt에 저장되었습니다."
```

## 📚 관련 문서

- **[System Overview](../SYSTEM_OVERVIEW.md)**: 전체 시스템 아키텍처
- **[Configuration Guide](configuration-ko.md)**: 설정 가이드
- **[Agent Development](../AGENT_DEVELOPMENT.md)**: 에이전트 개발 가이드
- **[Multi-Agent System](multi_agent_system-ko.md)**: 멀티 에이전트 시스템
- **[Testing Utilities](testing_utilities-ko.md)**: 테스트 유틸리티

---

**마지막 업데이트**: 2024년 11월