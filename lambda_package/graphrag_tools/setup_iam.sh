#!/bin/bash

# GraphRAG Lambda IAM 역할 및 정책 설정 스크립트
# 사용법: ./setup_iam.sh [ACCOUNT_ID] [ROLE_NAME]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 인자 확인
if [ $# -lt 2 ]; then
    echo -e "${RED}사용법: ./setup_iam.sh [ACCOUNT_ID] [ROLE_NAME]${NC}"
    echo "예시: ./setup_iam.sh 123456789012 graphrag-lambda-execution-role"
    exit 1
fi

ACCOUNT_ID=$1
ROLE_NAME=$2
POLICY_NAME="${ROLE_NAME}-policy"
REGION="us-west-2"

echo -e "${GREEN}GraphRAG Lambda IAM 설정 시작${NC}"
echo "Account ID: ${ACCOUNT_ID}"
echo "Role Name: ${ROLE_NAME}"
echo "Policy Name: ${POLICY_NAME}"
echo "Region: ${REGION}"
echo ""

# 1. IAM 역할 생성
echo -e "${YELLOW}[1/3] IAM 역할 생성 중...${NC}"

# 역할이 이미 존재하는지 확인
if aws iam get-role --role-name ${ROLE_NAME} 2>/dev/null; then
    echo -e "${BLUE}역할이 이미 존재합니다: ${ROLE_NAME}${NC}"
else
    echo "새 역할 생성 중..."
    aws iam create-role \
        --role-name ${ROLE_NAME} \
        --assume-role-policy-document file://iam_trust_policy.json \
        --description "GraphRAG Lambda 함수 실행 역할"
    
    echo -e "${GREEN}✓ IAM 역할 생성 완료${NC}"
fi
echo ""

# 2. 실행 정책 생성 및 연결
echo -e "${YELLOW}[2/3] 실행 정책 생성 및 연결 중...${NC}"

# 정책이 이미 존재하는지 확인
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"
if aws iam get-policy --policy-arn ${POLICY_ARN} 2>/dev/null; then
    echo -e "${BLUE}정책이 이미 존재합니다: ${POLICY_NAME}${NC}"
    
    # 기존 정책 버전 확인 및 업데이트
    echo "정책 업데이트 중..."
    
    # 기존 버전 삭제 (최대 5개까지만 유지 가능)
    VERSIONS=$(aws iam list-policy-versions --policy-arn ${POLICY_ARN} --query 'Versions[?IsDefaultVersion==`false`].VersionId' --output text)
    for VERSION in $VERSIONS; do
        aws iam delete-policy-version --policy-arn ${POLICY_ARN} --version-id ${VERSION} 2>/dev/null || true
    done
    
    # 새 버전 생성
    aws iam create-policy-version \
        --policy-arn ${POLICY_ARN} \
        --policy-document file://iam_execution_policy.json \
        --set-as-default
    
    echo -e "${GREEN}✓ 정책 업데이트 완료${NC}"
else
    echo "새 정책 생성 중..."
    aws iam create-policy \
        --policy-name ${POLICY_NAME} \
        --policy-document file://iam_execution_policy.json \
        --description "GraphRAG Lambda 함수 실행 정책 (Bedrock, KB, CloudWatch)"
    
    echo -e "${GREEN}✓ 정책 생성 완료${NC}"
fi

# 역할에 정책 연결
echo "역할에 정책 연결 중..."
aws iam attach-role-policy \
    --role-name ${ROLE_NAME} \
    --policy-arn ${POLICY_ARN} 2>/dev/null || echo -e "${BLUE}정책이 이미 연결되어 있습니다${NC}"

echo -e "${GREEN}✓ 정책 연결 완료${NC}"
echo ""

# 3. 권한 요약 출력
echo -e "${YELLOW}[3/3] 설정 완료 요약${NC}"
echo ""
echo -e "${GREEN}생성된 리소스:${NC}"
echo "  - IAM 역할: ${ROLE_NAME}"
echo "  - IAM 정책: ${POLICY_NAME}"
echo "  - 역할 ARN: arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo "  - 정책 ARN: ${POLICY_ARN}"
echo ""

echo -e "${GREEN}부여된 권한:${NC}"
echo "  ✓ Bedrock InvokeModel (Claude 3.5 Sonnet)"
echo "  ✓ Bedrock Retrieve (Knowledge Base: ZGBA1R5CS0)"
echo "  ✓ CloudWatch Logs (로그 그룹: /aws/lambda/graphrag-*)"
echo ""

echo -e "${YELLOW}다음 단계:${NC}"
echo "1. Lambda 함수 배포: ./deploy.sh ${ACCOUNT_ID} ${ROLE_NAME}"
echo "2. Reranker 모델 ARN 설정 (kb_retrieve Lambda 환경 변수)"
echo ""

echo -e "${GREEN}IAM 설정 완료!${NC}"
