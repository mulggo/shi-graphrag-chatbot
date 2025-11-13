# extract_entities Lambda Function

질문에서 주요 엔티티, 개념, 키워드를 추출하는 Lambda 함수입니다.

## 기능

사용자 질문에서 다음 정보를 추출합니다:
- **entities**: 주요 엔티티 (시스템, 장비, 구조물 등)
- **concepts**: 핵심 개념 (용량, 요구사항, 절차 등)
- **keywords_ko**: 한국어 검색 키워드
- **keywords_en**: 영어 검색 키워드
- **related_docs**: 관련 가능성이 높은 문서 유형

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
  "entities": ["고정식 CO2 소화 시스템", "CO2 system", "fixed installation"],
  "concepts": ["최소 용량", "minimum capacity", "요구사항"],
  "keywords_ko": ["고정식 CO2", "이산화탄소", "용량", "소화 시스템"],
  "keywords_en": ["fixed CO2 system", "minimum capacity", "fire fighting"],
  "related_docs": ["FSS Code", "SOLAS Chapter II-2"]
}
```

## 배포

```bash
# 패키징
cd lambda_package/graphrag_tools/extract_entities
zip -r extract_entities.zip lambda_function.py

# 배포
aws lambda create-function \
  --function-name graphrag-extract-entities \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --zip-file fileb://extract_entities.zip \
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
