#!/bin/bash

# GraphRAG Lambda 함수 배포 테스트 스크립트
# 사용법: ./test_deployment.sh

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

REGION="us-west-2"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GraphRAG Lambda 함수 테스트${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 임시 파일 생성
RESPONSE_FILE=$(mktemp)
trap "rm -f ${RESPONSE_FILE}" EXIT

# 테스트 결과 추적
TESTS_PASSED=0
TESTS_FAILED=0

# 테스트 함수
test_lambda() {
    local function_name=$1
    local payload=$2
    local test_name=$3
    
    echo -e "${YELLOW}테스트: ${test_name}${NC}"
    echo "함수: ${function_name}"
    echo "입력: ${payload}"
    
    if aws lambda invoke \
        --function-name ${function_name} \
        --payload "${payload}" \
        --region ${REGION} \
        ${RESPONSE_FILE} >/dev/null 2>&1; then
        
        echo -e "${BLUE}응답:${NC}"
        cat ${RESPONSE_FILE} | python3 -m json.tool 2>/dev/null || cat ${RESPONSE_FILE}
        echo ""
        
        # 에러 메시지 확인
        if grep -q "errorMessage" ${RESPONSE_FILE}; then
            echo -e "${RED}✗ 실패: Lambda 함수가 에러를 반환했습니다${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        else
            echo -e "${GREEN}✓ 성공${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        fi
    else
        echo -e "${RED}✗ 실패: Lambda 함수 호출 실패${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    echo ""
    echo "----------------------------------------"
    echo ""
}

# 1. classify_query 테스트
echo -e "${BLUE}[1/6] classify_query Lambda 테스트${NC}"
echo ""

test_lambda \
    "graphrag-classify-query" \
    '{"question": "고정식 CO2 소화 시스템의 최소 용량은?"}' \
    "사실 확인 질문 분류"

test_lambda \
    "graphrag-classify-query" \
    '{"question": "배관 지지대 설계 가이드와 실제 시공 방법을 비교해줘"}' \
    "비교 분석 질문 분류"

# 2. extract_entities 테스트
echo -e "${BLUE}[2/6] extract_entities Lambda 테스트${NC}"
echo ""

test_lambda \
    "graphrag-extract-entities" \
    '{"question": "배관 관통부의 단열재 요구사항은?"}' \
    "엔티티 추출 - 배관 관통부"

test_lambda \
    "graphrag-extract-entities" \
    '{"question": "IGC Code에 따른 가스 운반선의 소화 시스템은?"}' \
    "엔티티 추출 - IGC Code"

# 3. kb_retrieve 테스트
echo -e "${BLUE}[3/6] kb_retrieve Lambda 테스트${NC}"
echo ""

test_lambda \
    "graphrag-kb-retrieve" \
    '{"query": "CO2 system minimum capacity", "num_results": 5, "rerank": false}' \
    "KB 검색 - reranking 없음"

test_lambda \
    "graphrag-kb-retrieve" \
    '{"query": "pipe penetration insulation", "num_results": 5, "rerank": true}' \
    "KB 검색 - reranking 포함"

# 테스트 결과 요약
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}테스트 결과 요약${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "총 테스트: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}성공: ${TESTS_PASSED}${NC}"
echo -e "${RED}실패: ${TESTS_FAILED}${NC}"
echo ""

if [ ${TESTS_FAILED} -eq 0 ]; then
    echo -e "${GREEN}모든 테스트 통과! ✓${NC}"
    echo ""
    echo -e "${YELLOW}다음 단계:${NC}"
    echo "1. config/agents.yaml에 Lambda ARN 추가"
    echo "2. .env 파일에 환경 변수 설정"
    echo "3. Streamlit 애플리케이션에서 GraphRAG 에이전트 테스트"
    exit 0
else
    echo -e "${RED}일부 테스트 실패${NC}"
    echo ""
    echo -e "${YELLOW}문제 해결:${NC}"
    echo "1. CloudWatch Logs 확인:"
    echo "   aws logs tail /aws/lambda/graphrag-classify-query --follow --region ${REGION}"
    echo "   aws logs tail /aws/lambda/graphrag-extract-entities --follow --region ${REGION}"
    echo "   aws logs tail /aws/lambda/graphrag-kb-retrieve --follow --region ${REGION}"
    echo ""
    echo "2. Lambda 함수 구성 확인:"
    echo "   aws lambda get-function-configuration --function-name [FUNCTION_NAME] --region ${REGION}"
    echo ""
    echo "3. IAM 권한 확인"
    echo "4. Bedrock 모델 접근 권한 확인"
    exit 1
fi
