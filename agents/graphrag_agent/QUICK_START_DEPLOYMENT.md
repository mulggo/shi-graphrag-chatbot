# GraphRAG Multi-Agent System - Quick Start Deployment Guide

## 🚀 5-Minute Deployment Guide

This guide provides the fastest path to deploy the GraphRAG Multi-Agent System.

---

## Prerequisites

- ✅ AWS CLI configured with appropriate credentials
- ✅ Python 3.11+ installed
- ✅ Access to AWS Bedrock and Lambda services
- ✅ Knowledge Base ID: ZGBA1R5CS0

---

## Step 1: Deploy Lambda Functions (2 minutes)

### Option A: Using Deployment Script (Recommended)

```bash
# Navigate to Lambda tools directory
cd lambda_package/graphrag_tools

# Run deployment script
./deploy.sh

# Follow prompts to deploy all 3 Lambda functions
```

### Option B: Manual Deployment

```bash
# Deploy classify_query
cd lambda_package/graphrag_tools/classify_query
zip -r function.zip lambda_function.py requirements.txt
aws lambda create-function \
  --function-name graphrag-classify-query \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 512

# Deploy extract_entities
cd ../extract_entities
zip -r function.zip lambda_function.py requirements.txt
aws lambda create-function \
  --function-name graphrag-extract-entities \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 512

# Deploy kb_retrieve
cd ../kb_retrieve
zip -r function.zip lambda_function.py requirements.txt
aws lambda create-function \
  --function-name graphrag-kb-retrieve \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --zip-file fileb://function.zip \
  --timeout 60 \
  --memory-size 1024
```

---

## Step 2: Update Configuration (1 minute)

### Update config/agents.yaml

The GraphRAG agent is already configured and enabled. If you need to update Lambda ARNs:

```yaml
graphrag:
  lambda_function_names:
    classify_query: "graphrag-classify-query"  # or full ARN
    extract_entities: "graphrag-extract-entities"
    kb_retrieve: "graphrag-kb-retrieve"
```

### Update .env (Optional)

If using environment variables instead of config file:

```bash
# Add to .env
LAMBDA_CLASSIFY_QUERY_ARN=arn:aws:lambda:us-west-2:ACCOUNT:function:graphrag-classify-query
LAMBDA_EXTRACT_ENTITIES_ARN=arn:aws:lambda:us-west-2:ACCOUNT:function:graphrag-extract-entities
LAMBDA_KB_RETRIEVE_ARN=arn:aws:lambda:us-west-2:ACCOUNT:function:graphrag-kb-retrieve
```

---

## Step 3: Verify IAM Permissions (1 minute)

Ensure your Lambda execution role has these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "arn:aws:bedrock:us-west-2::foundation-model/*"
    },
    {
      "Effect": "Allow",
      "Action": ["bedrock:Retrieve"],
      "Resource": "arn:aws:bedrock:us-west-2:*:knowledge-base/ZGBA1R5CS0"
    }
  ]
}
```

---

## Step 4: Test Lambda Functions (1 minute)

```bash
# Test classify_query
aws lambda invoke \
  --function-name graphrag-classify-query \
  --payload '{"question":"고정식 CO2 소화 시스템의 최소 용량은?"}' \
  output.json && cat output.json

# Test extract_entities
aws lambda invoke \
  --function-name graphrag-extract-entities \
  --payload '{"question":"배관 관통부의 단열재 요구사항은?"}' \
  output.json && cat output.json

# Test kb_retrieve
aws lambda invoke \
  --function-name graphrag-kb-retrieve \
  --payload '{"query":"CO2 system","num_results":5,"rerank":true,"kb_id":"ZGBA1R5CS0"}' \
  output.json && cat output.json
```

Expected: All 3 Lambda functions return successful responses.

---

## Step 5: Start Application (30 seconds)

```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Start Streamlit
streamlit run app.py
```

---

## Step 6: Test in UI (30 seconds)

1. Open browser to http://localhost:8501
2. Select "GraphRAG 검색" from agent dropdown
3. Ask a test question: "고정식 CO2 소화 시스템의 최소 용량은?"
4. Verify:
   - ✅ Response is in Korean
   - ✅ References are displayed
   - ✅ Response time < 30 seconds

---

## Verification Checklist

Run the automated verification:

```bash
python agents/graphrag_agent/test_final_verification.py
```

Expected output:
```
Total Tests: 6
Passed: 6 ✓
Failed: 0 ✗
Success Rate: 100.0%
✓ System is ready for deployment
```

---

## Common Issues & Quick Fixes

### Issue: Lambda function not found
```bash
# Check if function exists
aws lambda list-functions | grep graphrag

# If missing, redeploy (see Step 1)
```

### Issue: Permission denied
```bash
# Check IAM role
aws iam get-role --role-name lambda-execution-role

# Attach Bedrock policy
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### Issue: Import error in Streamlit
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Restart Streamlit
streamlit run app.py
```

### Issue: Timeout errors
```bash
# Increase Lambda timeout
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --timeout 90
```

---

## Performance Tuning

### For Faster Response Times:

1. **Increase Lambda Memory**
   ```bash
   aws lambda update-function-configuration \
     --function-name graphrag-kb-retrieve \
     --memory-size 2048
   ```

2. **Enable Provisioned Concurrency** (reduces cold starts)
   ```bash
   aws lambda put-provisioned-concurrency-config \
     --function-name graphrag-kb-retrieve \
     --provisioned-concurrent-executions 2
   ```

3. **Reduce Number of Results** (in config/agents.yaml)
   ```yaml
   graphrag:
     search_params:
       default_num_results: 8  # Instead of 10
   ```

---

## Monitoring

### Quick CloudWatch Check:

```bash
# View Lambda logs
aws logs tail /aws/lambda/graphrag-kb-retrieve --follow

# Check invocation count
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=graphrag-kb-retrieve \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

---

## Rollback (if needed)

```bash
# Disable GraphRAG agent
# Edit config/agents.yaml:
graphrag:
  enabled: false

# Restart Streamlit
streamlit run app.py
```

---

## Next Steps

After successful deployment:

1. ✅ Test with various question types
2. ✅ Monitor performance metrics
3. ✅ Set up CloudWatch alarms
4. ✅ Test error scenarios
5. ✅ Verify 11-document coverage

---

## Support & Documentation

- **Full Deployment Guide:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Verification Summary:** [FINAL_VERIFICATION_SUMMARY.md](FINAL_VERIFICATION_SUMMARY.md)
- **Lambda Guide:** [../../lambda_package/graphrag_tools/DEPLOYMENT_GUIDE.md](../../lambda_package/graphrag_tools/DEPLOYMENT_GUIDE.md)
- **Requirements:** [.kiro/specs/graphrag-multi-agent/requirements.md](../../.kiro/specs/graphrag-multi-agent/requirements.md)
- **Design:** [.kiro/specs/graphrag-multi-agent/design.md](../../.kiro/specs/graphrag-multi-agent/design.md)

---

## Success Criteria

✅ All Lambda functions deployed  
✅ Configuration updated  
✅ IAM permissions set  
✅ Lambda tests passed  
✅ Application starts successfully  
✅ GraphRAG agent selectable in UI  
✅ Test query returns Korean response  
✅ References display correctly  
✅ Response time < 30 seconds  

**Deployment Time:** ~5 minutes  
**Difficulty:** Easy  
**Status:** Production Ready ✅

---

## Quick Reference Commands

```bash
# Deploy all Lambda functions
cd lambda_package/graphrag_tools && ./deploy.sh

# Test all Lambda functions
./test_deployment.sh

# Run verification tests
python agents/graphrag_agent/test_final_verification.py

# Start application
streamlit run app.py

# View logs
aws logs tail /aws/lambda/graphrag-kb-retrieve --follow

# Check status
aws lambda get-function --function-name graphrag-kb-retrieve
```

---

**Ready to deploy?** Follow the 6 steps above and you'll be running in 5 minutes! 🚀
