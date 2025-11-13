# GraphRAG Lambda 배포 빠른 시작 가이드

이 가이드는 GraphRAG Lambda 함수를 빠르게 배포하는 방법을 제공합니다.

## 5분 배포 가이드

### 1단계: 사전 준비 (1분)

```bash
# AWS CLI 설정 확인
aws sts get-caller-identity

# Account ID 확인 (출력에서 "Account" 값)
# 예: 123456789012
```

### 2단계: IAM 설정 (2분)

```bash
cd lambda_package/graphrag_tools

# IAM 역할 생성 (ACCOUNT_ID를 실제 값으로 변경)
./setup_iam.sh 123456789012 graphrag-lambda-execution-role
```

### 3단계: Lambda 배포 (2분)

```bash
# Lambda 함수 배포 (ACCOUNT_ID를 실제 값으로 변경)
./deploy.sh 123456789012 graphrag-lambda-execution-role
```

### 4단계: 테스트 (선택사항)

```bash
# 배포 테스트
./test_deployment.sh
```

## 한 줄 명령어

```bash
# 전체 배포 (ACCOUNT_ID를 실제 값으로 변경)
cd lambda_package/graphrag_tools && \
./setup_iam.sh 123456789012 graphrag-lambda-execution-role && \
./deploy.sh 123456789012 graphrag-lambda-execution-role && \
./test_deployment.sh
```

## 환경 변수 설정

배포 후 프로젝트 루트의 `.env` 파일에 다음 추가:

```bash
# Lambda ARN (deploy.sh 출력에서 복사)
LAMBDA_CLASSIFY_QUERY_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-classify-query
LAMBDA_EXTRACT_ENTITIES_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-extract-entities
LAMBDA_KB_RETRIEVE_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-kb-retrieve

# Reranker 모델 ARN
RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0

# GraphRAG 활성화
GRAPHRAG_ENABLED=true
```

## Reranker 설정

```bash
# kb_retrieve Lambda에 Reranker 모델 ARN 설정
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,AWS_REGION=us-west-2,RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0}" \
  --region us-west-2
```

## 애플리케이션 실행

```bash
# 프로젝트 루트로 이동
cd ../../..

# Streamlit 앱 실행
streamlit run app.py
```

## 문제 해결

### Lambda 호출 실패

```bash
# CloudWatch Logs 확인
aws logs tail /aws/lambda/graphrag-classify-query --follow --region us-west-2
```

### IAM 권한 오류

```bash
# IAM 역할 재생성
cd lambda_package/graphrag_tools
./setup_iam.sh [ACCOUNT_ID] [ROLE_NAME]
```

### Lambda 재배포

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

## 유용한 명령어

```bash
# Lambda 함수 목록
aws lambda list-functions --region us-west-2 | grep graphrag

# Lambda 함수 상태 확인
aws lambda get-function --function-name graphrag-classify-query --region us-west-2

# Lambda 환경 변수 확인
aws lambda get-function-configuration \
  --function-name graphrag-kb-retrieve \
  --region us-west-2 \
  --query 'Environment.Variables'

# CloudWatch Logs 그룹 확인
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/graphrag --region us-west-2

# 최근 에러 로그 검색
aws logs filter-log-events \
  --log-group-name /aws/lambda/graphrag-kb-retrieve \
  --filter-pattern "ERROR" \
  --region us-west-2 \
  --max-items 10
```

## 다음 단계

1. ✅ Lambda 함수 배포 완료
2. ⬜ config/agents.yaml 확인
3. ⬜ .env 파일 설정
4. ⬜ Streamlit 앱에서 GraphRAG 에이전트 테스트
5. ⬜ 프로덕션 배포

## 추가 문서

- [DEPLOYMENT.md](./DEPLOYMENT.md) - 상세 배포 가이드
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - 배포 체크리스트
- [README.md](./README.md) - Lambda 함수 개요

---

**도움이 필요하신가요?**
- CloudWatch Logs 확인
- [DEPLOYMENT.md](./DEPLOYMENT.md)의 문제 해결 섹션 참조
