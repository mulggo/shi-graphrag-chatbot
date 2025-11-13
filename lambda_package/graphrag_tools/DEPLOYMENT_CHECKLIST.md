# GraphRAG Lambda 배포 체크리스트

이 체크리스트를 사용하여 GraphRAG Lambda 함수 배포를 단계별로 진행하세요.

## 배포 전 준비

### ☐ 1. AWS CLI 설정 확인

```bash
# AWS CLI 버전 확인
aws --version

# 자격 증명 확인
aws sts get-caller-identity

# 출력 예시:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/username"
# }
```

**Account ID 기록**: `_________________`

### ☐ 2. 필요한 권한 확인

다음 권한이 있는지 확인:
- [ ] IAM 역할 생성 권한
- [ ] IAM 정책 생성 및 연결 권한
- [ ] Lambda 함수 생성 및 업데이트 권한
- [ ] Bedrock 모델 접근 권한
- [ ] Knowledge Base 접근 권한

### ☐ 3. Bedrock 모델 접근 활성화

```bash
# Bedrock 콘솔에서 다음 모델 활성화 확인:
# - Claude 3.5 Sonnet
# - Cohere Rerank v3.5 (또는 다른 reranker 모델)
```

### ☐ 4. Knowledge Base 확인

```bash
# KB 상태 확인
aws bedrock-agent get-knowledge-base \
  --knowledge-base-id ZGBA1R5CS0 \
  --region us-west-2
```

## IAM 설정

### ☐ 5. IAM 역할 이름 결정

**역할 이름**: `_________________` (예: `graphrag-lambda-execution-role`)

### ☐ 6. IAM 역할 및 정책 생성

```bash
cd lambda_package/graphrag_tools

# IAM 설정 스크립트 실행
./setup_iam.sh [ACCOUNT_ID] [ROLE_NAME]
```

**실행 명령**:
```bash
./setup_iam.sh _________________ _________________
```

### ☐ 7. IAM 역할 생성 확인

```bash
# 역할 확인
aws iam get-role --role-name [ROLE_NAME]

# 연결된 정책 확인
aws iam list-attached-role-policies --role-name [ROLE_NAME]
```

**역할 ARN 기록**: `_________________`

## Lambda 함수 배포

### ☐ 8. Lambda 함수 배포 실행

```bash
# 배포 스크립트 실행
./deploy.sh [ACCOUNT_ID] [ROLE_NAME]
```

**실행 명령**:
```bash
./deploy.sh _________________ _________________
```

### ☐ 9. Lambda ARN 기록

배포 완료 후 출력된 ARN을 기록:

**classify_query ARN**:
```
_________________________________________________________________
```

**extract_entities ARN**:
```
_________________________________________________________________
```

**kb_retrieve ARN**:
```
_________________________________________________________________
```

### ☐ 10. Reranker 모델 ARN 설정

```bash
# kb_retrieve Lambda에 Reranker 모델 ARN 설정
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,AWS_REGION=us-west-2,RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0}" \
  --region us-west-2
```

**Reranker 모델 ARN**: `_________________`

## 배포 테스트

### ☐ 11. Lambda 함수 개별 테스트

```bash
# 테스트 스크립트 실행
./test_deployment.sh
```

**테스트 결과**:
- [ ] classify_query: 성공
- [ ] extract_entities: 성공
- [ ] kb_retrieve (rerank=false): 성공
- [ ] kb_retrieve (rerank=true): 성공

### ☐ 12. CloudWatch Logs 확인

```bash
# 각 함수의 로그 확인
aws logs tail /aws/lambda/graphrag-classify-query --follow --region us-west-2
aws logs tail /aws/lambda/graphrag-extract-entities --follow --region us-west-2
aws logs tail /aws/lambda/graphrag-kb-retrieve --follow --region us-west-2
```

**로그 상태**:
- [ ] 에러 없음
- [ ] 정상 실행 확인

## 애플리케이션 통합

### ☐ 13. .env 파일 업데이트

프로젝트 루트의 `.env` 파일에 Lambda ARN 추가:

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
RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0

# Feature Flag
GRAPHRAG_ENABLED=true
```

### ☐ 14. config/agents.yaml 확인

`config/agents.yaml` 파일에 GraphRAG 에이전트 설정 확인:

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

### ☐ 15. Python 의존성 확인

```bash
# 프로젝트 루트에서
pip install -r requirements.txt
```

## 최종 검증

### ☐ 16. 로컬 테스트

```bash
# 프로젝트 루트에서
cd ../../..

# 에이전트 테스트
python -m pytest agents/graphrag_agent/test_agent.py -v
```

**테스트 결과**: ☐ 통과 / ☐ 실패

### ☐ 17. Streamlit 애플리케이션 실행

```bash
# Streamlit 앱 실행
streamlit run app.py
```

**확인 사항**:
- [ ] GraphRAG 에이전트가 사이드바에 표시됨
- [ ] 에이전트 선택 가능
- [ ] 질문 입력 및 응답 확인

### ☐ 18. 통합 테스트

다음 질문으로 GraphRAG 에이전트 테스트:

1. **사실 확인 질문**:
   - 질문: "고정식 CO2 소화 시스템의 최소 용량은?"
   - 결과: ☐ 성공 / ☐ 실패

2. **관계 탐색 질문**:
   - 질문: "배관 관통부의 단열재 요구사항은?"
   - 결과: ☐ 성공 / ☐ 실패

3. **다중 문서 질문**:
   - 질문: "DNV 규정에 따른 배관 지지대 설계 기준은?"
   - 결과: ☐ 성공 / ☐ 실패

4. **비교 분석 질문**:
   - 질문: "배관 지지대 설계 가이드와 실제 시공 방법을 비교해줘"
   - 결과: ☐ 성공 / ☐ 실패

## 배포 완료

### ☐ 19. 문서화

- [ ] 배포 날짜 기록: `_________________`
- [ ] 배포자 기록: `_________________`
- [ ] Lambda ARN 문서에 기록
- [ ] 문제 발생 시 대응 방법 문서화

### ☐ 20. 모니터링 설정

```bash
# CloudWatch 대시보드 생성 (선택사항)
# Lambda 함수 메트릭 모니터링 설정
```

**모니터링 항목**:
- [ ] Lambda 호출 횟수
- [ ] Lambda 에러율
- [ ] Lambda 실행 시간
- [ ] Bedrock API 호출 횟수

## 문제 해결

### 문제 발생 시 체크리스트

#### Lambda 함수 호출 실패
- [ ] IAM 역할 권한 확인
- [ ] Lambda 함수 존재 확인
- [ ] 환경 변수 설정 확인
- [ ] CloudWatch Logs 확인

#### Bedrock 접근 오류
- [ ] Bedrock 모델 활성화 확인
- [ ] IAM 정책에 Bedrock 권한 확인
- [ ] 리전 설정 확인 (us-west-2)

#### Knowledge Base 검색 실패
- [ ] KB ID 확인 (ZGBA1R5CS0)
- [ ] KB 상태 확인 (ACTIVE)
- [ ] IAM 정책에 Retrieve 권한 확인

#### Reranking 작동 안 함
- [ ] Reranker 모델 ARN 설정 확인
- [ ] Reranker 모델 활성화 확인
- [ ] Lambda 환경 변수 확인

## 롤백 절차

문제 발생 시 롤백:

```bash
# Lambda 함수 삭제
aws lambda delete-function --function-name graphrag-classify-query --region us-west-2
aws lambda delete-function --function-name graphrag-extract-entities --region us-west-2
aws lambda delete-function --function-name graphrag-kb-retrieve --region us-west-2

# IAM 역할 및 정책 삭제
aws iam detach-role-policy --role-name [ROLE_NAME] --policy-arn [POLICY_ARN]
aws iam delete-policy --policy-arn [POLICY_ARN]
aws iam delete-role --role-name [ROLE_NAME]
```

## 완료 서명

- **배포 완료 날짜**: `_________________`
- **배포자**: `_________________`
- **검증자**: `_________________`
- **승인자**: `_________________`

---

**참고 문서**:
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 상세 배포 가이드
- [README.md](./README.md) - Lambda 함수 개요
- [../../doc/lambda_functions.md](../../doc/lambda_functions.md) - Lambda 함수 문서
