#!/bin/bash
echo "kb_retrieve Lambda 재배포 중..."
cd lambda_package/graphrag_tools/kb_retrieve
zip lambda_function.zip lambda_function.py
aws lambda update-function-code --function-name graphrag-kb-retrieve --zip-file fileb://lambda_function.zip > /dev/null
rm lambda_function.zip
cd ../../..

echo "5초 대기 후 테스트 시작..."
sleep 5

python test_simple.py
