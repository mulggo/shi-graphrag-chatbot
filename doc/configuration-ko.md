# 구성 문서

## 개요

이 문서는 선박 소화 규칙 챗봇 프로젝트에서 사용되는 구성 파일과 설정을 설명합니다.

## 구성 파일

### 1. strands_tool_schema.json

**목적**: Bedrock Agent와 Strands ReAct 검색 도구 통합을 위한 OpenAPI 스키마 정의입니다.

#### 스키마 구조
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Strands ReAct Search",
    "version": "1.0.0",
    "description": "Advanced ReAct search tool"
  }
}
```

#### API 엔드포인트 정의
- **경로**: `/search`
- **메서드**: POST
- **Operation ID**: `strandsReactSearch`
- **설명**: "기본 검색이 관련 정보를 찾지 못할 때 사용"

#### 요청 스키마
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "검색 쿼리"
    }
  },
  "required": ["query"]
}
```

#### 응답 스키마
```json
{
  "type": "object",
  "properties": {
    "result": {
      "type": "string",
      "description": "검색 결과"
    }
  }
}
```

#### Bedrock Agent에서의 사용
1. Bedrock Agent Action Group에 스키마 업로드
2. Lambda 함수와 연결
3. 향상된 검색 기능을 위한 도구로 구성

### 2. lambda_trust_policy.json

**목적**: Lambda 함수 실행 역할을 위한 IAM 신뢰 정책입니다.

#### 정책 구조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

#### 주요 구성 요소
- **버전**: 정책 언어 버전 (2012-10-17)
- **효과**: 액세스 허용
- **주체**: AWS Lambda 서비스
- **액션**: 역할 가정 권한

#### 사용법
1. Lambda 함수를 위한 IAM 역할 생성
2. 역할에 이 신뢰 정책 연결
3. 필요한 실행 정책 추가 (Bedrock, S3, CloudWatch)

### 3. requirements.txt (Lambda 패키지)

**목적**: Lambda 함수 배포를 위한 Python 의존성입니다.

#### 의존성
```
strands-agents
boto3
```

#### 패키지 세부사항
- **strands-agents**: ReAct 패턴 구현을 위한 Strands 프레임워크
- **boto3**: Python용 AWS SDK

#### 설치
```bash
pip install -r requirements.txt
```

## AWS 리소스 구성

### Bedrock Agent 구성

#### Agent 설정
- **Agent ID**: `WT3ZJ25XCL`
- **Agent Alias ID**: `3RWZZLJDY1`
- **리전**: `us-west-2`
- **모델**: Claude 3.5 Sonnet

#### Action Group 구성
- **이름**: Strands ReAct Search
- **스키마**: `strands_tool_schema.json`
- **Lambda 함수**: Strands 도구 구현
- **설명**: 고급 검색 기능

### Knowledge Base 구성

#### Knowledge Base 설정
- **Knowledge Base ID**: `ZGBA1R5CS0`
- **리전**: `us-west-2`
- **벡터 데이터베이스**: Amazon OpenSearch Serverless
- **임베딩 모델**: Amazon Titan Embeddings

#### 데이터 소스 구성
- **소스 유형**: S3 버킷
- **문서 형식**: PDF 파일
- **처리**: 이미지 추출을 위한 OCR 활성화
- **청킹 전략**: 의미론적 청킹

### Lambda 함수 구성

#### 런타임 설정
- **런타임**: Python 3.11
- **아키텍처**: x86_64
- **메모리**: 512MB - 1GB (권장)
- **타임아웃**: 30-60초

#### 환경 변수
특정 환경 변수는 필요하지 않습니다. AWS 자격 증명은 IAM 역할을 통해 처리됩니다.

#### 레이어 구성
- **레이어 1**: Strands agents 및 의존성
- **레이어 2**: 추가 Python 패키지
- **총 크기**: 콜드 스타트 성능에 최적화

## 애플리케이션 구성

### Streamlit 구성

#### 페이지 설정
```python
st.set_page_config(
    page_title="선박 Firefighting 규칙 챗봇",
    page_icon="🚢",
    layout="wide"
)
```

#### AWS 클라이언트 구성
```python
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-agent-runtime', region_name='us-west-2')

@st.cache_resource
def get_s3_client():
    return boto3.client('s3', region_name='us-west-2')
```

### 세션 관리
- **세션 ID**: UUID 기반 고유 식별자
- **메시지 저장**: 인메모리 세션 상태
- **대화 기록**: 세션별 유지

## 보안 구성

### IAM 권한

#### Lambda 실행 역할
필요한 권한:
- `bedrock:InvokeAgent`
- `bedrock:Retrieve`
- `s3:GetObject`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

#### Bedrock Agent 역할
필요한 권한:
- `lambda:InvokeFunction`
- `bedrock:InvokeModel`
- Knowledge Base 액세스 권한

### 네트워크 구성
- **VPC**: 기본 설정에는 필요하지 않음
- **보안 그룹**: 기본 설정으로 충분
- **서브넷**: 인터넷 액세스를 위한 퍼블릭 서브넷

## 성능 구성

### 캐싱 전략
- **AWS 클라이언트**: Streamlit의 `@st.cache_resource`를 사용한 캐싱
- **세션 데이터**: 인메모리 캐싱
- **응답 캐싱**: 구현되지 않음 (실시간 응답)

### 최적화 설정
- **Lambda 메모리**: Strands 프레임워크를 위해 최소 512MB
- **Knowledge Base 결과**: 쿼리당 10개 결과로 제한
- **콘텐츠 표시**: 성능을 위해 잘림

## 모니터링 구성

### CloudWatch 로그
- **Lambda 로그**: 자동 로깅 활성화
- **애플리케이션 로그**: 콘솔에 Streamlit 로깅
- **오류 추적**: 모든 구성 요소에서 예외 로깅

### 메트릭 수집
- **Lambda 메트릭**: 지속 시간, 메모리 사용량, 오류율
- **Agent 메트릭**: 호출 수, 성공률
- **Knowledge Base 메트릭**: 쿼리 성능, 결과 품질

## 환경별 구성

### 개발 환경
- **로컬 테스트**: AWS CLI 자격 증명 사용
- **디버그 모드**: 향상된 로깅 활성화
- **테스트 데이터**: 샘플 쿼리 및 응답

### 프로덕션 환경
- **IAM 역할**: 서비스별 역할
- **모니터링**: CloudWatch 알람 구성
- **스케일링**: Lambda 함수 자동 스케일링

## 구성 모범 사례

### 보안
1. **최소 권한**: 최소 필요 권한
2. **역할 분리**: 다른 서비스를 위한 별도 역할
3. **자격 증명 관리**: 하드코딩된 자격 증명 없음

### 성능
1. **리소스 크기 조정**: 적절한 메모리 및 타임아웃 설정
2. **캐싱**: 효과적인 캐싱 메커니즘 사용
3. **연결 재사용**: 가능한 경우 지속적인 연결

### 유지보수성
1. **구성 파일**: 중앙화된 구성
2. **환경 변수**: 환경별 설정
3. **문서화**: 명확한 구성 문서

## 구성 문제 해결

### 일반적인 문제
1. **권한 오류**: IAM 역할 및 정책 확인
2. **리소스를 찾을 수 없음**: 리소스 ID 및 리전 확인
3. **타임아웃 문제**: Lambda 타임아웃 설정 조정
4. **메모리 문제**: Lambda 메모리 할당 증가

### 진단 단계
1. **AWS 자격 증명 확인**: `aws sts get-caller-identity`
2. **리소스 액세스 확인**: 개별 서비스 호출 테스트
3. **CloudWatch 로그 검토**: 오류 메시지 확인
4. **구성 테스트**: 검증을 위한 유틸리티 스크립트 사용

### 구성 검증
1. **스키마 검증**: OpenAPI 스키마 형식 확인
2. **정책 검증**: IAM 정책 구문 확인
3. **리소스 검증**: 리소스 존재 확인
4. **통합 테스트**: 종단 간 구성 테스트