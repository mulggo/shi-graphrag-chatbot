#!/bin/bash

# GraphRAG Lambda 함수 배포 스크립트
# 사용법: ./deploy.sh [ACCOUNT_ID] [ROLE_NAME]
#
# 사전 요구사항:
#   1. AWS CLI 설치 및 구성
#   2. IAM 역할 생성 (./setup_iam.sh 실행)
#   3. 적절한 AWS 권한
#
# 예시:
#   ./deploy.sh 123456789012 graphrag-lambda-execution-role

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 인자 확인
if [ $# -lt 2 ]; then
    echo -e "${RED}사용법: ./deploy.sh [ACCOUNT_ID] [ROLE_NAME]${NC}"
    echo ""
    echo "예시: ./deploy.sh 123456789012 graphrag-lambda-execution-role"
    echo ""
    echo -e "${YELLOW}사전 요구사항:${NC}"
    echo "  1. IAM 역할이 생성되어 있어야 합니다"
    echo "     → ./setup_iam.sh [ACCOUNT_ID] [ROLE_NAME] 실행"
    echo "  2. AWS CLI가 구성되어 있어야 합니다"
    echo "     → aws configure"
    exit 1
fi

ACCOUNT_ID=$1
ROLE_NAME=$2
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
REGION="us-west-2"
BEDROCK_MODEL_ID="anthropic.claude-3-5-sonnet-20240620-v1:0"
KB_ID="ZGBA1R5CS0"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GraphRAG Lambda 함수 배포${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Account ID: ${ACCOUNT_ID}"
echo "Role: ${ROLE_NAME}"
echo "Region: ${REGION}"
echo "KB ID: ${KB_ID}"
echo ""

# IAM 역할 존재 확인
echo -e "${BLUE}IAM 역할 확인 중...${NC}"
if ! aws iam get-role --role-name ${ROLE_NAME} >/dev/null 2>&1; then
    echo -e "${RED}오류: IAM 역할 '${ROLE_NAME}'이 존재하지 않습니다${NC}"
    echo ""
    echo "다음 명령으로 IAM 역할을 먼저 생성하세요:"
    echo "  ./setup_iam.sh ${ACCOUNT_ID} ${ROLE_NAME}"
    exit 1
fi
echo -e "${GREEN}✓ IAM 역할 확인 완료${NC}"
echo ""

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_DIR}"

# 1. classify_query Lambda 배포
echo -e "${YELLOW}[1/3] classify_query Lambda 배포 중...${NC}"
cd classify_query
zip -q -r classify_query.zip lambda_function.py

# 함수 존재 확인
if aws lambda get-function --function-name graphrag-classify-query --region ${REGION} 2>/dev/null; then
    echo "기존 함수 업데이트 중..."
    aws lambda update-function-code \
        --function-name graphrag-classify-query \
        --zip-file fileb://classify_query.zip \
        --region ${REGION}
    
    aws lambda update-function-configuration \
        --function-name graphrag-classify-query \
        --environment Variables="{BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID}}" \
        --region ${REGION}
else
    echo "새 함수 생성 중..."
    aws lambda create-function \
        --function-name graphrag-classify-query \
        --runtime python3.11 \
        --handler lambda_function.lambda_handler \
        --role ${ROLE_ARN} \
        --zip-file fileb://classify_query.zip \
        --timeout 30 \
        --memory-size 512 \
        --environment Variables="{BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID}}" \
        --region ${REGION}
fi

rm classify_query.zip
cd ..
echo -e "${GREEN}✓ classify_query Lambda 배포 완료${NC}"
echo ""

# 2. extract_entities Lambda 배포
echo -e "${YELLOW}[2/3] extract_entities Lambda 배포 중...${NC}"
cd extract_entities
zip -q -r extract_entities.zip lambda_function.py

if aws lambda get-function --function-name graphrag-extract-entities --region ${REGION} 2>/dev/null; then
    echo "기존 함수 업데이트 중..."
    aws lambda update-function-code \
        --function-name graphrag-extract-entities \
        --zip-file fileb://extract_entities.zip \
        --region ${REGION}
    
    aws lambda update-function-configuration \
        --function-name graphrag-extract-entities \
        --environment Variables="{BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID}}" \
        --region ${REGION}
else
    echo "새 함수 생성 중..."
    aws lambda create-function \
        --function-name graphrag-extract-entities \
        --runtime python3.11 \
        --handler lambda_function.lambda_handler \
        --role ${ROLE_ARN} \
        --zip-file fileb://extract_entities.zip \
        --timeout 30 \
        --memory-size 512 \
        --environment Variables="{BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID}}" \
        --region ${REGION}
fi

rm extract_entities.zip
cd ..
echo -e "${GREEN}✓ extract_entities Lambda 배포 완료${NC}"
echo ""

# 3. kb_retrieve Lambda 배포
echo -e "${YELLOW}[3/3] kb_retrieve Lambda 배포 중...${NC}"
cd kb_retrieve
zip -q -r kb_retrieve.zip lambda_function.py

# Reranker 모델 ARN (사용자가 설정해야 함)
echo -e "${YELLOW}주의: RERANKER_MODEL_ARN 환경 변수를 수동으로 설정해야 합니다${NC}"

if aws lambda get-function --function-name graphrag-kb-retrieve --region ${REGION} 2>/dev/null; then
    echo "기존 함수 업데이트 중..."
    aws lambda update-function-code \
        --function-name graphrag-kb-retrieve \
        --zip-file fileb://kb_retrieve.zip \
        --region ${REGION}
    
    aws lambda update-function-configuration \
        --function-name graphrag-kb-retrieve \
        --environment Variables="{BEDROCK_KB_ID=${KB_ID}}" \
        --region ${REGION}
else
    echo "새 함수 생성 중..."
    aws lambda create-function \
        --function-name graphrag-kb-retrieve \
        --runtime python3.11 \
        --handler lambda_function.lambda_handler \
        --role ${ROLE_ARN} \
        --zip-file fileb://kb_retrieve.zip \
        --timeout 60 \
        --memory-size 1024 \
        --environment Variables="{BEDROCK_KB_ID=${KB_ID}}" \
        --region ${REGION}
fi

rm kb_retrieve.zip
cd ..
echo -e "${GREEN}✓ kb_retrieve Lambda 배포 완료${NC}"
echo ""

# Lambda 함수 ARN 출력
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}배포 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}Lambda 함수 ARN:${NC}"
echo ""

CLASSIFY_ARN=$(aws lambda get-function --function-name graphrag-classify-query --region ${REGION} --query 'Configuration.FunctionArn' --output text)
EXTRACT_ARN=$(aws lambda get-function --function-name graphrag-extract-entities --region ${REGION} --query 'Configuration.FunctionArn' --output text)
KB_RETRIEVE_ARN=$(aws lambda get-function --function-name graphrag-kb-retrieve --region ${REGION} --query 'Configuration.FunctionArn' --output text)

echo "1. classify_query:"
echo "   ${CLASSIFY_ARN}"
echo ""
echo "2. extract_entities:"
echo "   ${EXTRACT_ARN}"
echo ""
echo "3. kb_retrieve:"
echo "   ${KB_RETRIEVE_ARN}"
echo ""

# .env 파일 예시 생성
echo -e "${YELLOW}환경 변수 설정 예시 (.env 파일):${NC}"
echo ""
cat << EOF
# GraphRAG Lambda 함수 ARN
LAMBDA_CLASSIFY_QUERY_ARN=${CLASSIFY_ARN}
LAMBDA_EXTRACT_ENTITIES_ARN=${EXTRACT_ARN}
LAMBDA_KB_RETRIEVE_ARN=${KB_RETRIEVE_ARN}

# Bedrock 설정
BEDROCK_KB_ID=${KB_ID}
BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID}
AWS_REGION=${REGION}

# Reranker 모델 ARN (설정 필요)
RERANKER_MODEL_ARN=arn:aws:bedrock:${REGION}::foundation-model/[YOUR_RERANKER_MODEL]
EOF
echo ""

echo -e "${YELLOW}다음 단계:${NC}"
echo ""
echo "1. ${BLUE}Reranker 모델 ARN 설정${NC}"
echo "   kb_retrieve Lambda 함수의 RERANKER_MODEL_ARN 환경 변수를 설정하세요:"
echo "   aws lambda update-function-configuration \\"
echo "     --function-name graphrag-kb-retrieve \\"
echo "     --environment Variables=\"{BEDROCK_KB_ID=${KB_ID},AWS_REGION=${REGION},RERANKER_MODEL_ARN=arn:aws:bedrock:${REGION}::foundation-model/[YOUR_MODEL]}\" \\"
echo "     --region ${REGION}"
echo ""
echo "2. ${BLUE}config/agents.yaml 업데이트${NC}"
echo "   위의 Lambda ARN을 config/agents.yaml 파일에 추가하세요"
echo ""
echo "3. ${BLUE}.env 파일 생성${NC}"
echo "   위의 환경 변수 예시를 .env 파일에 추가하세요"
echo ""
echo "4. ${BLUE}Lambda 함수 테스트${NC}"
echo "   각 Lambda 함수를 테스트하여 정상 작동을 확인하세요"
echo ""

echo -e "${GREEN}배포 스크립트 완료!${NC}"
