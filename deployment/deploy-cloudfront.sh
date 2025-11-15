#!/bin/bash

# CloudFront 배포 스크립트
# 선박 소방 규정 챗봇용 CloudFront 설정

set -e

# 변수 설정
STACK_NAME="ship-firefighting-chatbot-cloudfront"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="$SCRIPT_DIR/cloudfront-simple.yaml"
REGION="us-west-2"
STREAMLIT_DOMAIN="streamlit-alb-1809216659.us-west-2.elb.amazonaws.com"
STREAMLIT_PORT="80"

echo "🚀 CloudFront 배포 시작..."
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Streamlit Origin: $STREAMLIT_DOMAIN:$STREAMLIT_PORT"

# CloudFormation 스택 배포
aws cloudformation deploy \
    --template-file $TEMPLATE_FILE \
    --stack-name $STACK_NAME \
    --region $REGION \
    --parameter-overrides \
        StreamlitOriginIP=$STREAMLIT_DOMAIN \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

echo "✅ CloudFormation 스택 배포 완료"

# CloudFront 정보 출력
echo "📋 CloudFront 정보 조회 중..."

DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
    --output text)

CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
    --output text)

CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
    --output text)

echo ""
echo "🎉 CloudFront 배포 완료!"
echo "=================================="
echo "Distribution ID: $DISTRIBUTION_ID"
echo "CloudFront Domain: $CLOUDFRONT_DOMAIN"
echo "CloudFront URL: $CLOUDFRONT_URL"
echo "=================================="
echo ""
echo "📝 참고사항:"
echo "- CloudFront 배포는 15-20분 정도 소요됩니다"
echo "- 배포 상태 확인: aws cloudfront get-distribution --id $DISTRIBUTION_ID"
echo "- 캐시 무효화: aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths '/*'"
echo ""
echo "🌐 접속 URL: $CLOUDFRONT_URL"