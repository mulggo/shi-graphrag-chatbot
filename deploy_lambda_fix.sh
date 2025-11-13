#!/bin/bash
# Lambda 함수 개별 배포 스크립트

echo "================================"
echo "Lambda 함수 배포 시작"
echo "================================"

# extract_entities 배포
echo ""
echo "[1/2] extract_entities 배포 중..."
cd lambda_package/graphrag_tools/extract_entities
zip lambda_function.zip lambda_function.py
aws lambda update-function-code \
  --function-name graphrag-extract-entities \
  --zip-file fileb://lambda_function.zip
rm lambda_function.zip
cd ../../..

# kb_retrieve 배포
echo ""
echo "[2/2] kb_retrieve 배포 중..."
cd lambda_package/graphrag_tools/kb_retrieve
zip lambda_function.zip lambda_function.py
aws lambda update-function-code \
  --function-name graphrag-kb-retrieve \
  --zip-file fileb://lambda_function.zip
rm lambda_function.zip
cd ../../..

echo ""
echo "================================"
echo "✓ 배포 완료!"
echo "================================"
echo ""
echo "5초 후 테스트를 실행합니다..."
sleep 5

python test_simple.py
