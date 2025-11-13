# kb_retrieve Lambda Function

Bedrock Knowledge Base에서 문서를 검색하고 reranking을 수행하는 Lambda 함수입니다.

## 기능

- Bedrock KB Retrieve API를 사용한 문서 검색
- Reranker 모델을 통한 관련성 재평가
- Exponential backoff를 사용한 재시도 로직
- 구조화된 로깅 및 메트릭

## 환경 변수

- `BEDROCK_KB_ID`: Knowledge Base ID (기본값: `ZGBA1R5CS0`)
- `RERANKER_MODEL_ARN`: Reranker 모델 ARN
- `AWS_REGION`: AWS 리전 (기본값: `us-west-2`)

## 입력 형식

```json
{
  "query": "고정식 CO2 소화 시스템의 최소 용량",
  "num_results": 10,
  "rerank": true,
  "kb_id": "ZGBA1R5CS0",
  "reranker_model_arn": "arn:aws:bedrock:us-west-2::foundation-model/..."
}
```

### 필수 필드
- `query`: 검색 쿼리

### 선택 필드
- `num_results`: 검색할 청크 수 (기본값: 10)
- `rerank`: reranking 활성화 (기본값: true)
- `kb_id`: Knowledge Base ID (환경변수 사용 가능)
- `reranker_model_arn`: Reranker 모델 ARN (환경변수 사용 가능)

## 출력 형식

```json
{
  "chunks": [
    {
      "text": "The minimum capacity shall be 85% of the gross volume...",
      "score": 0.95,
      "source": "s3://bucket/path/to/document.pdf",
      "page": 45,
      "source_uri": "SOLAS_Chapter_II-2.pdf"
    }
  ],
  "total_retrieved": 10,
  "reranked": true,
  "query": "고정식 CO2 소화 시스템의 최소 용량",
  "duration": 2.34
}
```

## 에러 출력

```json
{
  "errorMessage": "Knowledge Base ID가 필요합니다",
  "errorType": "ValueError",
  "chunks": [],
  "total_retrieved": 0,
  "reranked": false
}
```

## 배포

```bash
# 패키징
cd lambda_package/graphrag_tools/kb_retrieve
zip -r kb_retrieve.zip lambda_function.py

# 배포
aws lambda create-function \
  --function-name graphrag-kb-retrieve \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --zip-file fileb://kb_retrieve.zip \
  --timeout 60 \
  --memory-size 1024 \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,RERANKER_MODEL_ARN=arn:aws:bedrock:...,AWS_REGION=us-west-2}"
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
        "bedrock:Retrieve"
      ],
      "Resource": "arn:aws:bedrock:us-west-2:*:knowledge-base/ZGBA1R5CS0"
    },
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
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## 재시도 로직

함수는 다음 에러에 대해 exponential backoff를 사용하여 최대 3회 재시도합니다:
- `TooManyRequestsException`
- `ThrottlingException`
- `ServiceUnavailable`

초기 대기 시간: 1초
백오프 배수: 2.0 (1초 → 2초 → 4초)

## 성능 고려사항

- **메모리**: 1024MB (대량 데이터 처리)
- **타임아웃**: 60초 (reranking 포함)
- **동시 실행**: Lambda 자동 스케일링
- **콜드 스타트**: boto3 클라이언트 재사용으로 최소화
