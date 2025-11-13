# GraphRAG Tools - Lambda Functions

GraphRAG 멀티 에이전트 시스템을 위한 Lambda 함수 모음입니다.

## 📚 배포 문서

- **[QUICK_START.md](./QUICK_START.md)** - 5분 빠른 배포 가이드
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - 상세 배포 가이드 및 문제 해결
- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - 단계별 배포 체크리스트

## 개요

이 디렉토리는 Strands Agents 기반 GraphRAG 시스템에서 사용하는 3개의 Lambda 함수를 포함합니다:

1. **classify_query**: 질문 유형 분류
2. **extract_entities**: 엔티티 및 키워드 추출
3. **kb_retrieve**: Knowledge Base 검색 및 reranking

## 디렉토리 구조

```
graphrag_tools/
├── classify_query/
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── README.md
├── extract_entities/
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── README.md
├── kb_retrieve/
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── README.md
├── deploy.sh
└── README.md (이 파일)
```

## 빠른 시작

### 자동 배포 (권장)

```bash
# 1. IAM 역할 생성
./setup_iam.sh [ACCOUNT_ID] graphrag-lambda-execution-role

# 2. Lambda 함수 배포
./deploy.sh [ACCOUNT_ID] graphrag-lambda-execution-role

# 3. 배포 테스트
./test_deployment.sh
```

자세한 내용은 [QUICK_START.md](./QUICK_START.md)를 참조하세요.

### 수동 배포

#### 1. IAM 역할 생성

Lambda 실행을 위한 IAM 역할을 생성합니다:

```bash
# 신뢰 정책 파일 생성
cat > trust-policy.json << EOF
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

# IAM 역할 생성
aws iam create-role \
  --role-name graphrag-lambda-execution-role \
  --assume-role-policy-document file://trust-policy.json

# 권한 정책 연결
aws iam attach-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### 2. Bedrock 권한 추가

```bash
# Bedrock 권한 정책 파일 생성
cat > bedrock-policy.json << EOF
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

# 정책 생성 및 연결
aws iam put-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-name BedrockAccess \
  --policy-document file://bedrock-policy.json
```

### 3. Lambda 함수 배포

```bash
# 배포 스크립트 실행
cd lambda_package/graphrag_tools
./deploy.sh [YOUR_ACCOUNT_ID] graphrag-lambda-execution-role
```

### 4. Reranker 모델 ARN 설정

kb_retrieve Lambda 함수에 Reranker 모델 ARN을 설정합니다:

```bash
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,AWS_REGION=us-west-2,RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0}"
```

## 함수 상세 정보

### classify_query

**목적**: 질문 유형 분류 (factual, relational, multi_doc, comparative)

**리소스**:
- 메모리: 512MB
- 타임아웃: 30초
- 런타임: Python 3.11

**환경 변수**:
- `BEDROCK_MODEL_ID`: Claude 3.5 Sonnet 모델 ID
- `AWS_REGION`: us-west-2

[상세 문서](classify_query/README.md)

### extract_entities

**목적**: 엔티티, 개념, 키워드 추출

**리소스**:
- 메모리: 512MB
- 타임아웃: 30초
- 런타임: Python 3.11

**환경 변수**:
- `BEDROCK_MODEL_ID`: Claude 3.5 Sonnet 모델 ID
- `AWS_REGION`: us-west-2

[상세 문서](extract_entities/README.md)

### kb_retrieve

**목적**: Knowledge Base 검색 및 reranking

**리소스**:
- 메모리: 1024MB
- 타임아웃: 60초
- 런타임: Python 3.11

**환경 변수**:
- `BEDROCK_KB_ID`: ZGBA1R5CS0
- `RERANKER_MODEL_ARN`: Reranker 모델 ARN
- `AWS_REGION`: us-west-2

[상세 문서](kb_retrieve/README.md)

## 테스트

각 Lambda 함수를 개별적으로 테스트할 수 있습니다:

```bash
# classify_query 테스트
aws lambda invoke \
  --function-name graphrag-classify-query \
  --payload '{"question":"고정식 CO2 소화 시스템의 최소 용량은?"}' \
  response.json

# extract_entities 테스트
aws lambda invoke \
  --function-name graphrag-extract-entities \
  --payload '{"question":"고정식 CO2 소화 시스템의 최소 용량은?"}' \
  response.json

# kb_retrieve 테스트
aws lambda invoke \
  --function-name graphrag-kb-retrieve \
  --payload '{"query":"fixed CO2 system minimum capacity","num_results":5}' \
  response.json
```

## 모니터링

CloudWatch Logs에서 각 함수의 로그를 확인할 수 있습니다:

```bash
# 로그 그룹 확인
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/graphrag

# 최근 로그 스트림 확인
aws logs tail /aws/lambda/graphrag-classify-query --follow
aws logs tail /aws/lambda/graphrag-extract-entities --follow
aws logs tail /aws/lambda/graphrag-kb-retrieve --follow
```

## 비용 예상

Lambda 함수 실행 비용 (us-west-2 기준):

- **classify_query**: ~$0.0000083 per invocation
- **extract_entities**: ~$0.0000083 per invocation
- **kb_retrieve**: ~$0.0000167 per invocation

월 1,000회 실행 시 총 비용: ~$0.03

추가 비용:
- Bedrock InvokeModel: ~$0.003 per 1K input tokens
- Bedrock Retrieve: ~$0.0025 per query
- Reranking: ~$0.001 per query

## 문제 해결

### Lambda 함수가 Bedrock에 접근할 수 없음

IAM 역할에 Bedrock 권한이 있는지 확인:

```bash
aws iam get-role-policy \
  --role-name graphrag-lambda-execution-role \
  --policy-name BedrockAccess
```

### KB 검색이 실패함

1. Knowledge Base ID가 올바른지 확인
2. Lambda 함수에 Bedrock Retrieve 권한이 있는지 확인
3. Reranker 모델 ARN이 올바른지 확인

### 타임아웃 발생

Lambda 함수의 타임아웃을 늘립니다:

```bash
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --timeout 90
```

## 다음 단계

1. Lambda 함수 ARN을 `config/agents.yaml`에 추가
2. `.env` 파일에 환경 변수 설정
3. Strands 도구 래퍼 구현 (`agents/graphrag_agent/tools.py`)
4. 워크플로우 에이전트 구현

## 참고 자료

- [AWS Lambda 문서](https://docs.aws.amazon.com/lambda/)
- [Bedrock Runtime API](https://docs.aws.amazon.com/bedrock/latest/APIReference/)
- [Strands Agents 문서](https://docs.strands.ai/)
