# classify_query Lambda Function

질문 유형을 분류하는 Lambda 함수입니다.

## 기능

사용자 질문을 다음 4가지 유형으로 분류합니다:
- **factual**: 특정 사실이나 요구사항을 묻는 질문
- **relational**: 개념 간 관계나 연결을 묻는 질문
- **multi_doc**: 여러 문서나 규정을 참조해야 하는 질문
- **comparative**: 두 가지 이상을 비교하는 질문

## 환경 변수

- `BEDROCK_MODEL_ID`: Bedrock 모델 ID (기본값: `anthropic.claude-3-5-sonnet-20240620-v1:0`)
- `AWS_REGION`: AWS 리전 (기본값: `us-west-2`)

## 입력 형식

```json
{
  "question": "고정식 CO2 소화 시스템의 최소 용량은?"
}
```

## 출력 형식

```json
{
  "question_type": "factual",
  "confidence": 0.95,
  "reasoning": "특정 요구사항을 묻는 사실 확인 질문"
}
```

## 배포

```bash
# 패키징
cd lambda_package/graphrag_tools/classify_query
zip -r classify_query.zip lambda_function.py

# 배포
aws lambda create-function \
  --function-name graphrag-classify-query \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --zip-file fileb://classify_query.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0,AWS_REGION=us-west-2}"
```

## IAM 권한

Lambda 실행 역할에 다음 권한이 필요합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```
