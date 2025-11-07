# 멀티 에이전트 시스템 문서

## 개요

선박 소방 규정 챗봇은 다양한 규정 도메인을 위한 전문 AI 에이전트의 쉬운 확장과 유지보수를 가능하게 하는 모듈식 멀티 에이전트 아키텍처를 사용합니다.

## 아키텍처 구성요소

### 에이전트 매니저 (`core/agent_manager.py`)

시스템의 모든 에이전트를 관리하는 중앙 오케스트레이터입니다.

**주요 기능:**
- **동적 에이전트 로딩**: YAML 구성을 기반으로 에이전트 로드
- **메시지 라우팅**: 사용자 쿼리를 적절한 에이전트로 라우팅
- **구성 관리**: 에이전트 등록 및 생명주기 처리
- **오류 처리**: 에이전트 실패에 대한 우아한 처리

**사용법:**
```python
from core.agent_manager import AgentManager

manager = AgentManager()
result = manager.route_message('firefighting', 'Your question', 'session-id')
```

### 기본 에이전트 (`agents/base_agent.py`)

모든 에이전트가 상속받는 추상 기본 클래스로, 공통 기능을 제공합니다.

**공통 기능:**
- **AWS Bedrock 통합**: 내장된 Bedrock Agent 통신
- **참조 추출**: 문서 참조의 자동 추출
- **S3 이미지 처리**: 참조 이미지의 다운로드 및 표시
- **오류 처리**: 표준화된 오류 응답
- **로깅**: 상호작용 로깅 기능

**구현 패턴:**
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def process_message(self, message: str, session_id: str) -> Dict:
        # 사용자 정의 처리 로직
        result = self.invoke_bedrock_agent(message, session_id)
        return result
```

## 에이전트 구성

### 구성 파일 (`config/agents.yaml`)

에이전트는 쉬운 관리를 위해 YAML 형식으로 정의됩니다:

```yaml
agents:
  firefighting:
    display_name: "선박 소방 규정"
    description: "선박 소방 시스템 및 SOLAS 규정 전문가"
    module_path: "agents.firefighting_agent.agent"
    bedrock_agent_id: "WT3ZJ25XCL"
    bedrock_alias_id: "3RWZZLJDY1"
    knowledge_base_id: "ZGBA1R5CS0"
    enabled: true
    ui_config:
      icon: "🚢"
      color: "#FF6B6B"
      topics:
        - "고정식 소화 시스템"
        - "휴대용 소화기"
        - "배수 시스템"
```

### 구성 매개변수

| 매개변수 | 설명 | 필수 |
|---------|------|------|
| `display_name` | 사람이 읽을 수 있는 에이전트 이름 | 예 |
| `description` | 에이전트 설명 | 예 |
| `module_path` | 에이전트로의 Python 모듈 경로 | 예 |
| `bedrock_agent_id` | AWS Bedrock Agent ID | 예 |
| `bedrock_alias_id` | AWS Bedrock Agent Alias ID | 예 |
| `knowledge_base_id` | AWS Knowledge Base ID | 예 |
| `enabled` | 에이전트 활성화 여부 | 아니오 (기본값: true) |
| `ui_config` | UI 사용자 정의 설정 | 아니오 |

## 현재 에이전트

### 소방 에이전트 (`agents/firefighting_agent/agent.py`)

선박 소방 규정 및 SOLAS 표준을 위한 전문 에이전트입니다.

**기능:**
- SOLAS 규정 해석
- 소화 시스템 가이드
- 화재 위험 평가
- 장비 선택 지원
- 규정 준수 확인

**지식 베이스:**
- SOLAS Chapter II-2 문서
- FSS Code 규정
- DNV-RU-SHIP 규칙
- 기술 사양

## 새로운 에이전트 추가

### 1단계: 에이전트 구조 생성

```bash
mkdir -p agents/new_agent
touch agents/new_agent/__init__.py
```

### 2단계: 에이전트 클래스 구현

`agents/new_agent/agent.py` 생성:

```python
from agents.base_agent import BaseAgent
from typing import Dict

class Agent(BaseAgent):
    """새로운 전문 에이전트"""
    
    def __init__(self, config):
        super().__init__(config)
        # 에이전트별 초기화
    
    def process_message(self, message: str, session_id: str) -> Dict:
        """사용자 메시지 처리"""
        # 사용자 정의 전처리
        enhanced_message = self._enhance_query(message)
        
        # Bedrock Agent 호출
        result = self.invoke_bedrock_agent(enhanced_message, session_id)
        
        # 사용자 정의 후처리
        return self._enhance_response(result)
    
    def _enhance_query(self, message: str) -> str:
        """에이전트별 쿼리 향상"""
        # 도메인별 컨텍스트 추가
        return f"도메인 컨텍스트: {message}"
    
    def _enhance_response(self, result: Dict) -> Dict:
        """에이전트별 응답 향상"""
        # 도메인별 포맷팅 추가
        return result
    
    def get_capabilities(self) -> List[str]:
        """에이전트별 기능 반환"""
        return [
            "도메인별 기능 1",
            "도메인별 기능 2"
        ]
```

### 3단계: 구성 업데이트

`config/agents.yaml`에 추가:

```yaml
agents:
  new_agent:
    display_name: "새 에이전트 이름"
    description: "에이전트 설명"
    module_path: "agents.new_agent.agent"
    bedrock_agent_id: "YOUR_BEDROCK_AGENT_ID"
    bedrock_alias_id: "YOUR_BEDROCK_ALIAS_ID"
    knowledge_base_id: "YOUR_KNOWLEDGE_BASE_ID"
    enabled: true
    ui_config:
      icon: "🔧"
      color: "#4ECDC4"
      topics:
        - "주제 1"
        - "주제 2"
```

### 4단계: 에이전트 테스트

```python
from core.agent_manager import AgentManager

manager = AgentManager()
result = manager.route_message('new_agent', '테스트 질문', 'test-session')
print(result)
```

## 모범 사례

### 에이전트 개발

1. **BaseAgent에서 상속**: 항상 기본 클래스를 확장
2. **process_message() 구현**: 메시지 처리를 위한 핵심 메서드
3. **구성 활용**: 유연성을 위해 에이전트 구성 활용
4. **우아한 오류 처리**: 구조화된 오류 응답 반환
5. **로깅 추가**: 내장 로깅 기능 사용

### 구성 관리

1. **설명적 이름 사용**: 명확한 표시 이름과 설명
2. **도메인별 구성**: 관련 에이전트를 논리적으로 그룹화
3. **버전 제어**: 구성 변경 사항 추적
4. **환경 분리**: 개발/운영용 다른 구성

### 테스트

1. **단위 테스트**: 개별 에이전트 메서드 테스트
2. **통합 테스트**: AgentManager와 함께 테스트
3. **종단간 테스트**: UI를 통한 테스트
4. **성능 테스트**: 응답 시간 모니터링

## 문제 해결

### 일반적인 문제

1. **에이전트 로딩 실패**:
   - 구성의 모듈 경로 확인
   - 에이전트 클래스 이름이 "Agent"인지 확인
   - 에이전트 코드의 구문 오류 확인

2. **Bedrock 연결 오류**:
   - AWS 자격 증명 확인
   - 에이전트 ID 및 별칭 ID 확인
   - 적절한 IAM 권한 확인

3. **구성 오류**:
   - YAML 구문 검증
   - 필수 매개변수 확인
   - 파일 경로 확인

### 디버그 모드

에이전트 매니저에서 디버그 로깅 활성화:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = AgentManager()
```

## 향후 개선사항

### 계획된 기능

1. **에이전트 협업**: 멀티 에이전트 워크플로우
2. **동적 로딩**: 런타임 에이전트 등록
3. **성능 모니터링**: 에이전트 성능 메트릭
4. **A/B 테스트**: 에이전트 버전 비교
5. **자동 확장**: 동적 에이전트 인스턴스 관리

### 확장 지점

1. **사용자 정의 도구**: 에이전트별 도구 통합
2. **미들웨어**: 요청/응답 처리 파이프라인
3. **캐싱**: 에이전트 응답 캐싱
4. **분석**: 사용량 및 성능 분석