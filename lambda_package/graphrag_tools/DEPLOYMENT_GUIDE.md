# GraphRAG Lambda Functions - 배포 가이드

## 목차

1. [개요](#개요)
2. [사전 준비](#사전-준비)
3. [배포 방법](#배포-방법)
4. [구성 및 설정](#구성-및-설정)
5. [테스트 및 검증](#테스트-및-검증)
6. [문제 해결](#문제-해결)
7. [모니터링](#모니터링)
8. [업데이트 및 유지보수](#업데이트-및-유지보수)

## 개요

이 가이드는 GraphRAG 멀티 에이전트 시스템의 Lambda 함수를 AWS에 배포하는 전체 과정을 설명합니다.

### 배포할 Lambda 함수

1. **graphrag-classify-query**: 질문 유형 분류
2. **graphrag-extract-entities**: 엔티티 및 키워드 추출
3. **graphrag-kb-retrieve**: Knowledge Base 검색 및 reranking

### 배포 시간

- 자동 배포: 약 10-15분
- 수동 배포: 약 30-45분

## 사전 준비

### 1. AWS 계정 및 권한

필요한 AWS 권한:
- Lambda 함수 생성 및 관리
- IAM 역할 생성 및 정책 연결
- Bedrock 서비스 접근
- CloudWatch Logs 접근

### 2. AWS CLI 설치 및 구성

```bash
# AWS CLI 설치 확인
aws --version

# AWS 자격 증명 구성
aws configure
# AWS Access Key ID: [YOUR_ACCESS_KEY]
# AWS Secret Access Key: [YOUR_SECRET_KEY]
# Default region name: us-west-2
# Default output format: json
```

### 3. 필요한 정보 수집

배포 전에 다음 정보를 준비하세요:

- **AWS Account ID**: `aws sts get-caller-identity --query Account --output text`
- **Bedrock KB ID**: `ZGBA1R5CS0`
- **Bedrock Model ID**: `anthropic.claude-3-5-sonnet-20240620-v1:0`
- **Reranker Model ARN**: `arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0`

### 4. 디렉토리 구조 확인

```bash
cd lambda_package/graphrag_tools
ls -la

# 다음 파일들이 있어야 합니다:
# - deploy.sh
# - setup_iam.sh
# - test_deployment.sh
# - classify_query/
# - extract_entities/
# - kb_retrieve/
```

## 배포 방법

### 방법 1: 자동 배포 (권장)

#### Step 1: IAM 역할 생성

```bash
# 실행 권한 부여
chmod +x setup_iam.sh

# IAM 역할 생성
./setup_iam.sh [YOUR_ACCOUNT_ID] graphrag-lambda-execution-role
```

**출력 예시**:
```
✓ IAM trust policy created
✓ IAM role created: graphrag-lambda-execution-role
✓ Basic execution policy attached
✓ Bedrock access policy created and attached
✓ IAM role setup complete!

Role ARN: arn:aws:iam::123456789012:role/graphrag-lambda-execution-role
```

#### Step 2: Lambda 함수 배포

```bash
# 실행 권한 부여
chmod +x deploy.sh

# Lambda 함수 배포
./deploy.sh [YOUR_ACCOUNT_ID] graphrag-lambda-execution-role
```

**배포 과정**:
1. 각 Lambda 함수 디렉토리로 이동
2. 의존성 설치 및 패키징
3. Lambda 함수 생성 또는 업데이트
4. 환경 변수 설정
5. 배포 완료 확인

**출력 예시**:
```
Deploying Lambda functions...

[1/3] Deploying classify_query...
✓ Dependencies installed
✓ Package created
✓ Lambda function deployed
✓ Environment variables configured

[2/3] Deploying extract_entities...
✓ Dependencies installed
✓ Package created
✓ Lambda function deployed
✓ Environment variables configured

[3/3] Deploying kb_retrieve...
✓ Dependencies installed
✓ Package created
✓ Lambda function deployed
✓ Environment variables configured

All Lambda functions deployed successfully!
```

#### Step 3: 배포 검증

```bash
# 실행 권한 부여
chmod +x test_deployment.sh

# 배포 테스트
./test_deployment.sh
```

**테스트 결과**:
```
Testing Lambda deployments...

[1/3] Testing classify_query...
✓ Function exists
✓ Function invoked successfully
✓ Response valid

[2/3] Testing extract_entities...
✓ Function exists
✓ Function invoked successfully
✓ Response valid

[3/3] Testing kb_retrieve...
✓ Function exists
✓ Function invoked successfully
✓ Response valid

All tests passed!
```

### 방법 2: 수동 배포

#### Step 1: IAM 역할 생성

```bash
# 1. 신뢰 정책 파일 생성
cat > iam_trust_policy.json << 'EOF'
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
EOF

# 2. IAM 역할 생성
aws iam create-role \
  --role-name graphrag-lambda-execution-role \
  --assume-role-policy-document file://iam_trust_policy.json

# 3. 기본 실행 정책 연결
aws iam attach-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# 4. Bedrock 권한 정책 생성
cat > iam_execution_policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-west-2::foundation-model/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve"
      ],
      "Resource": "arn:aws:bedrock:us-west-2:*:knowledge-base/ZGBA1R5CS0"
    }
  ]
}
EOF

# 5. Bedrock 권한 정책 연결
aws iam put-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-name BedrockAccess \
  --policy-document file://iam_execution_policy.json
```

#### Step 2: classify_query Lambda 배포

```bash
cd classify_query

# 1. 의존성 설치
pip install -r requirements.txt -t .

# 2. 패키지 생성
zip -r ../classify_query.zip .

# 3. Lambda 함수 생성
cd ..
aws lambda create-function \
  --function-name graphrag-classify-query \
  --runtime python3.11 \
  --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/graphrag-lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://classify_query.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0,AWS_REGION=us-west-2}"

# 4. 정리
rm classify_query.zip
```

#### Step 3: extract_entities Lambda 배포

```bash
cd extract_entities

# 1. 의존성 설치
pip install -r requirements.txt -t .

# 2. 패키지 생성
zip -r ../extract_entities.zip .

# 3. Lambda 함수 생성
cd ..
aws lambda create-function \
  --function-name graphrag-extract-entities \
  --runtime python3.11 \
  --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/graphrag-lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://extract_entities.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0,AWS_REGION=us-west-2}"

# 4. 정리
rm extract_entities.zip
```

#### Step 4: kb_retrieve Lambda 배포

```bash
cd kb_retrieve

# 1. 의존성 설치
pip install -r requirements.txt -t .

# 2. 패키지 생성
zip -r ../kb_retrieve.zip .

# 3. Lambda 함수 생성
cd ..
aws lambda create-function \
  --function-name graphrag-kb-retrieve \
  --runtime python3.11 \
  --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/graphrag-lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://kb_retrieve.zip \
  --timeout 60 \
  --memory-size 1024 \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,AWS_REGION=us-west-2,RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0}"

# 4. 정리
rm kb_retrieve.zip
```

## 구성 및 설정

### Lambda 함수 ARN 확인

배포 후 각 Lambda 함수의 ARN을 확인합니다:

```bash
# classify_query ARN
aws lambda get-function --function-name graphrag-classify-query \
  --query 'Configuration.FunctionArn' --output text

# extract_entities ARN
aws lambda get-function --function-name graphrag-extract-entities \
  --query 'Configuration.FunctionArn' --output text

# kb_retrieve ARN
aws lambda get-function --function-name graphrag-kb-retrieve \
  --query 'Configuration.FunctionArn' --output text
```

### 환경 변수 설정

프로젝트 루트의 `.env` 파일에 Lambda ARN을 추가합니다:

```bash
# .env 파일 편집
cat >> ../../.env << 'EOF'

# GraphRAG Lambda Functions
LAMBDA_CLASSIFY_QUERY_ARN=arn:aws:lambda:us-west-2:[ACCOUNT_ID]:function:graphrag-classify-query
LAMBDA_EXTRACT_ENTITIES_ARN=arn:aws:lambda:us-west-2:[ACCOUNT_ID]:function:graphrag-extract-entities
LAMBDA_KB_RETRIEVE_ARN=arn:aws:lambda:us-west-2:[ACCOUNT_ID]:function:graphrag-kb-retrieve
EOF
```

### config/agents.yaml 업데이트

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

### 개별 Lambda 함수 테스트

#### classify_query 테스트

```bash
aws lambda invoke \
  --function-name graphrag-classify-query \
  --payload '{"question":"고정식 CO2 소화 시스템의 최소 용량은?"}' \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json
```

**예상 출력**:
```json
{
  "question_type": "factual",
  "confidence": 0.95
}
```

#### extract_entities 테스트

```bash
aws lambda invoke \
  --function-name graphrag-extract-entities \
  --payload '{"question":"고정식 CO2 소화 시스템의 최소 용량은?"}' \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json
```

**예상 출력**:
```json
{
  "entities": ["CO2 system", "capacity", "fixed installation"],
  "keywords": ["fixed CO2 system", "minimum capacity", "고정식 CO2", "용량"]
}
```

#### kb_retrieve 테스트

```bash
aws lambda invoke \
  --function-name graphrag-kb-retrieve \
  --payload '{"query":"fixed CO2 system minimum capacity","num_results":5}' \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json
```

**예상 출력**:
```json
{
  "chunks": [
    {
      "text": "The minimum capacity shall be...",
      "score": 0.95,
      "source": "s3://bucket/SOLAS_Chapter_II-2.pdf",
      "page": 45
    }
  ],
  "total_retrieved": 5,
  "reranked": true
}
```

### 통합 테스트

Streamlit 애플리케이션을 실행하여 전체 시스템을 테스트합니다:

```bash
cd ../../
streamlit run app.py
```

1. 사이드바에서 "🕸️ GraphRAG 검색" 선택
2. 테스트 질문 입력: "고정식 CO2 소화 시스템의 최소 용량은?"
3. 답변 및 참조 확인

## 문제 해결

### 일반적인 문제

#### 1. Lambda 함수 생성 실패

**증상**:
```
An error occurred (InvalidParameterValueException) when calling the CreateFunction operation
```

**원인**: IAM 역할이 아직 전파되지 않음

**해결**:
```bash
# 30초 대기 후 재시도
sleep 30
aws lambda create-function ...
```

#### 2. Bedrock 접근 권한 오류

**증상**:
```
AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel
```

**해결**:
```bash
# IAM 정책 확인
aws iam get-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-name BedrockAccess

# 정책이 없으면 다시 연결
aws iam put-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-name BedrockAccess \
  --policy-document file://iam_execution_policy.json
```

#### 3. Lambda 타임아웃

**증상**:
```
Task timed out after 30.00 seconds
```

**해결**:
```bash
# 타임아웃 증가
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --timeout 90
```

#### 4. 메모리 부족

**증상**:
```
Runtime exited with error: signal: killed
```

**해결**:
```bash
# 메모리 증가
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --memory-size 2048
```

#### 5. 환경 변수 누락

**증상**:
```
KeyError: 'BEDROCK_KB_ID'
```

**해결**:
```bash
# 환경 변수 확인
aws lambda get-function-configuration \
  --function-name graphrag-kb-retrieve \
  --query 'Environment.Variables'

# 환경 변수 설정
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,AWS_REGION=us-west-2,RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0}"
```

### 디버깅 팁

#### CloudWatch Logs 확인

```bash
# 최근 로그 확인
aws logs tail /aws/lambda/graphrag-classify-query --follow

# 특정 시간대 로그 확인
aws logs filter-log-events \
  --log-group-name /aws/lambda/graphrag-classify-query \
  --start-time $(date -u -d '10 minutes ago' +%s)000
```

#### Lambda 함수 상태 확인

```bash
# 함수 구성 확인
aws lambda get-function-configuration \
  --function-name graphrag-classify-query

# 함수 코드 확인
aws lambda get-function \
  --function-name graphrag-classify-query
```

## 모니터링

### CloudWatch 대시보드 생성

```bash
# 대시보드 생성 (선택사항)
aws cloudwatch put-dashboard \
  --dashboard-name GraphRAG-Lambda-Dashboard \
  --dashboard-body file://dashboard.json
```

### 알람 설정

```bash
# 에러율 알람
aws cloudwatch put-metric-alarm \
  --alarm-name graphrag-kb-retrieve-errors \
  --alarm-description "Alert when kb_retrieve error rate is high" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=graphrag-kb-retrieve

# 타임아웃 알람
aws cloudwatch put-metric-alarm \
  --alarm-name graphrag-kb-retrieve-duration \
  --alarm-description "Alert when kb_retrieve duration is high" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 50000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=graphrag-kb-retrieve
```

### 주요 메트릭

모니터링할 주요 메트릭:
- **Invocations**: 호출 횟수
- **Duration**: 실행 시간
- **Errors**: 에러 발생 횟수
- **Throttles**: 제한 발생 횟수
- **ConcurrentExecutions**: 동시 실행 수

## 업데이트 및 유지보수

### Lambda 함수 코드 업데이트

```bash
# 1. 코드 수정
cd classify_query
# ... 코드 수정 ...

# 2. 재패키징
pip install -r requirements.txt -t .
zip -r ../classify_query.zip .

# 3. 업데이트
cd ..
aws lambda update-function-code \
  --function-name graphrag-classify-query \
  --zip-file fileb://classify_query.zip

# 4. 정리
rm classify_query.zip
```

### 환경 변수 업데이트

```bash
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --environment Variables="{BEDROCK_KB_ID=NEW_KB_ID,AWS_REGION=us-west-2,RERANKER_MODEL_ARN=NEW_ARN}"
```

### Lambda 함수 삭제

```bash
# 개별 함수 삭제
aws lambda delete-function --function-name graphrag-classify-query
aws lambda delete-function --function-name graphrag-extract-entities
aws lambda delete-function --function-name graphrag-kb-retrieve

# IAM 역할 삭제
aws iam delete-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-name BedrockAccess

aws iam detach-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role --role-name graphrag-lambda-execution-role
```

## 비용 최적화

### Lambda 함수 최적화

1. **메모리 최적화**: 필요한 최소 메모리 사용
2. **타임아웃 최적화**: 적절한 타임아웃 설정
3. **예약된 동시성**: 필요한 경우에만 사용
4. **코드 최적화**: 불필요한 의존성 제거

### 비용 모니터링

```bash
# Lambda 비용 확인 (Cost Explorer 사용)
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://lambda-filter.json
```

## 체크리스트

배포 완료 후 다음 항목을 확인하세요:

- [ ] IAM 역할 생성 완료
- [ ] 3개 Lambda 함수 배포 완료
- [ ] 환경 변수 설정 완료
- [ ] Lambda ARN을 .env에 추가 완료
- [ ] config/agents.yaml 업데이트 완료
- [ ] 개별 Lambda 함수 테스트 통과
- [ ] 통합 테스트 통과
- [ ] CloudWatch Logs 확인 가능
- [ ] 모니터링 설정 완료 (선택사항)

## 다음 단계

1. [GraphRAG Agent 문서](../../doc/graphrag_agent-ko.md) 읽기
2. Streamlit 애플리케이션에서 GraphRAG 에이전트 사용
3. 프롬프트 커스터마이징
4. 성능 모니터링 및 최적화

## 참고 자료

- [AWS Lambda 문서](https://docs.aws.amazon.com/lambda/)
- [AWS Bedrock 문서](https://docs.aws.amazon.com/bedrock/)
- [AWS CLI 참조](https://docs.aws.amazon.com/cli/)
- [QUICK_START.md](./QUICK_START.md) - 빠른 시작 가이드
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 상세 배포 문서

## 지원

문제가 발생하면:
1. [문제 해결](#문제-해결) 섹션 확인
2. CloudWatch Logs 확인
3. GitHub Issues에 문의
