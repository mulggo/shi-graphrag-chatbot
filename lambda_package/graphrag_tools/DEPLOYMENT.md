# GraphRAG Lambda 함수 배포 가이드

이 문서는 GraphRAG 멀티 에이전트 시스템의 Lambda 함수를 AWS에 배포하는 방법을 설명합니다.

## 목차

1. [사전 요구사항](#사전-요구사항)
2. [배포 단계](#배포-단계)
3. [IAM 설정](#iam-설정)
4. [Lambda 함수 배포](#lambda-함수-배포)
5. [환경 변수 설정](#환경-변수-설정)
6. [테스트 및 검증](#테스트-및-검증)
7. [문제 해결](#문제-해결)

## 사전 요구사항

### 1. AWS CLI 설치 및 구성

```bash
# AWS CLI 설치 확인
aws --version

# AWS 자격 증명 구성
aws configure
```

필요한 정보:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-west-2`
- Default output format: `json`

### 2. 필요한 권한

배포를 수행하는 IAM 사용자/역할은 다음 권한이 필요합니다:

- `iam:CreateRole`
- `iam:CreatePolicy`
- `iam:AttachRolePolicy`
- `lambda:CreateFunction`
- `lambda:UpdateFunctionCode`
- `lambda:UpdateFunctionConfiguration`
- `lambda:GetFunction`

### 3. AWS 계정 정보

- AWS Account ID
- 배포할 리전 (기본값: `us-west-2`)
- Knowledge Base ID: `ZGBA1R5CS0`

## 배포 단계

### 단계 1: IAM 역할 및 정책 생성

```bash
cd lambda_package/graphrag_tools

# IAM 역할 생성 스크립트 실행
./setup_iam.sh [ACCOUNT_ID] [ROLE_NAME]

# 예시
./setup_iam.sh 123456789012 graphrag-lambda-execution-role
```

이 스크립트는 다음을 수행합니다:
- Lambda 실행 역할 생성
- Bedrock 및 Knowledge Base 접근 권한 부여
- CloudWatch Logs 권한 부여

### 단계 2: Lambda 함수 배포

```bash
# Lambda 함수 배포 스크립트 실행
./deploy.sh [ACCOUNT_ID] [ROLE_NAME]

# 예시
./deploy.sh 123456789012 graphrag-lambda-execution-role
```

이 스크립트는 다음 3개의 Lambda 함수를 배포합니다:
1. `graphrag-classify-query`: 질문 유형 분류
2. `graphrag-extract-entities`: 엔티티 추출
3. `graphrag-kb-retrieve`: Knowledge Base 검색 및 reranking

### 단계 3: Reranker 모델 ARN 설정

kb_retrieve Lambda 함수에 Reranker 모델 ARN을 설정합니다:

```bash
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,AWS_REGION=us-west-2,RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/[YOUR_RERANKER_MODEL]}" \
  --region us-west-2
```

## IAM 설정

### Trust Policy

Lambda 함수가 AWS 서비스에 의해 실행될 수 있도록 허용합니다.

**파일**: `iam_trust_policy.json`

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

### Execution Policy

Lambda 함수가 필요한 AWS 서비스에 접근할 수 있도록 권한을 부여합니다.

**파일**: `iam_execution_policy.json`

주요 권한:
- **Bedrock InvokeModel**: Claude 3.5 Sonnet 모델 호출
- **Bedrock Retrieve**: Knowledge Base 검색
- **CloudWatch Logs**: 로그 기록

## Lambda 함수 배포

### 함수별 설정

#### 1. classify_query

- **Function Name**: `graphrag-classify-query`
- **Runtime**: Python 3.11
- **Handler**: `lambda_function.lambda_handler`
- **Timeout**: 30초
- **Memory**: 512MB
- **Environment Variables**:
  - `BEDROCK_MODEL_ID`: `anthropic.claude-3-5-sonnet-20240620-v1:0`
  - `AWS_REGION`: `us-west-2`

#### 2. extract_entities

- **Function Name**: `graphrag-extract-entities`
- **Runtime**: Python 3.11
- **Handler**: `lambda_function.lambda_handler`
- **Timeout**: 30초
- **Memory**: 512MB
- **Environment Variables**:
  - `BEDROCK_MODEL_ID`: `anthropic.claude-3-5-sonnet-20240620-v1:0`
  - `AWS_REGION`: `us-west-2`

#### 3. kb_retrieve

- **Function Name**: `graphrag-kb-retrieve`
- **Runtime**: Python 3.11
- **Handler**: `lambda_function.lambda_handler`
- **Timeout**: 60초
- **Memory**: 1024MB
- **Environment Variables**:
  - `BEDROCK_KB_ID`: `ZGBA1R5CS0`
  - `AWS_REGION`: `us-west-2`
  - `RERANKER_MODEL_ARN`: (수동 설정 필요)

## 환경 변수 설정

### 프로젝트 .env 파일

배포 후 프로젝트 루트의 `.env` 파일에 Lambda ARN을 추가합니다:

```bash
# GraphRAG Lambda 함수 ARN
LAMBDA_CLASSIFY_QUERY_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-classify-query
LAMBDA_EXTRACT_ENTITIES_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-extract-entities
LAMBDA_KB_RETRIEVE_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-kb-retrieve

# Bedrock 설정
BEDROCK_KB_ID=ZGBA1R5CS0
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_REGION=us-west-2

# Reranker 모델 ARN
RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/[YOUR_RERANKER_MODEL]
```

### config/agents.yaml 업데이트

`config/agents.yaml` 파일에 Lambda 함수 이름을 추가합니다:

```yaml
graphrag:
  display_name: "GraphRAG 검색"
  description: "지능형 그래프 기반 문서 검색 전문가"
  module_path: "agents.graphrag_agent.agent"
  knowledge_base_id: "ZGBA1R5CS0"
  lambda_function_names:
    classify_query: "graphrag-classify-query"
    extract_entities: "graphrag-extract-entities"
    kb_retrieve: "graphrag-kb-retrieve"
  enabled: true
```

## 테스트 및 검증

### 1. Lambda 함수 개별 테스트

#### classify_query 테스트

```bash
aws lambda invoke \
  --function-name graphrag-classify-query \
  --payload '{"question": "고정식 CO2 소화 시스템의 최소 용량은?"}' \
  --region us-west-2 \
  response.json

cat response.json
```

예상 출력:
```json
{
  "question_type": "factual",
  "confidence": 0.95,
  "reasoning": "특정 요구사항을 묻는 사실 확인 질문"
}
```

#### extract_entities 테스트

```bash
aws lambda invoke \
  --function-name graphrag-extract-entities \
  --payload '{"question": "배관 관통부의 단열재 요구사항은?"}' \
  --region us-west-2 \
  response.json

cat response.json
```

#### kb_retrieve 테스트

```bash
aws lambda invoke \
  --function-name graphrag-kb-retrieve \
  --payload '{"query": "CO2 system minimum capacity", "num_results": 5, "rerank": true}' \
  --region us-west-2 \
  response.json

cat response.json
```

### 2. CloudWatch Logs 확인

```bash
# 최근 로그 확인
aws logs tail /aws/lambda/graphrag-classify-query --follow --region us-west-2
aws logs tail /aws/lambda/graphrag-extract-entities --follow --region us-west-2
aws logs tail /aws/lambda/graphrag-kb-retrieve --follow --region us-west-2
```

### 3. 통합 테스트

프로젝트의 테스트 스크립트를 실행하여 전체 워크플로우를 테스트합니다:

```bash
cd ../../..  # 프로젝트 루트로 이동
python -m pytest agents/graphrag_agent/test_agent.py -v
```

## 문제 해결

### 일반적인 문제

#### 1. IAM 권한 오류

**증상**: `AccessDeniedException` 또는 권한 관련 오류

**해결**:
```bash
# IAM 역할 정책 확인
aws iam list-attached-role-policies --role-name graphrag-lambda-execution-role

# 정책 재설정
./setup_iam.sh [ACCOUNT_ID] [ROLE_NAME]
```

#### 2. Lambda 타임아웃

**증상**: Lambda 함수가 시간 초과로 실패

**해결**:
```bash
# 타임아웃 증가 (예: 60초)
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --timeout 60 \
  --region us-west-2
```

#### 3. Bedrock 모델 접근 오류

**증상**: `ResourceNotFoundException` 또는 모델 접근 불가

**해결**:
1. Bedrock 콘솔에서 모델 접근 권한 확인
2. 리전이 올바른지 확인 (`us-west-2`)
3. 모델 ID가 정확한지 확인

#### 4. Knowledge Base 검색 실패

**증상**: KB 검색 시 오류 발생

**해결**:
```bash
# KB 상태 확인
aws bedrock-agent get-knowledge-base \
  --knowledge-base-id ZGBA1R5CS0 \
  --region us-west-2

# KB 접근 권한 확인
aws iam get-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-name graphrag-lambda-execution-role-policy
```

#### 5. Reranker 모델 미설정

**증상**: kb_retrieve에서 reranking이 작동하지 않음

**해결**:
```bash
# Reranker 모델 ARN 설정
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,AWS_REGION=us-west-2,RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/[YOUR_MODEL]}" \
  --region us-west-2
```

### 로그 분석

CloudWatch Logs에서 다음 정보를 확인합니다:

```bash
# 에러 로그 검색
aws logs filter-log-events \
  --log-group-name /aws/lambda/graphrag-kb-retrieve \
  --filter-pattern "ERROR" \
  --region us-west-2
```

### 함수 재배포

문제가 지속되면 함수를 재배포합니다:

```bash
# 특정 함수만 재배포
cd classify_query
zip -r classify_query.zip lambda_function.py
aws lambda update-function-code \
  --function-name graphrag-classify-query \
  --zip-file fileb://classify_query.zip \
  --region us-west-2
rm classify_query.zip
cd ..
```

## 추가 리소스

- [AWS Lambda 개발자 가이드](https://docs.aws.amazon.com/lambda/)
- [AWS Bedrock 문서](https://docs.aws.amazon.com/bedrock/)
- [Strands Agents 문서](https://docs.strands.ai/)

## 지원

문제가 발생하면 다음을 확인하세요:
1. CloudWatch Logs
2. Lambda 함수 구성
3. IAM 역할 및 정책
4. Bedrock 모델 접근 권한

---

**마지막 업데이트**: 2025-01-11
