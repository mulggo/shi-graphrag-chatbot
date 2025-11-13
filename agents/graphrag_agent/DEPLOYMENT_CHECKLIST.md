# GraphRAG Multi-Agent System - Deployment Checklist

## ✅ Pre-Deployment Verification (COMPLETED)

### 1. Configuration Verification ✓
- [x] config/agents.yaml has graphrag agent configured
- [x] GraphRAG agent is enabled (enabled: true)
- [x] Knowledge Base ID is correct (ZGBA1R5CS0)
- [x] Lambda function names are configured
- [x] All required fields are present

### 2. Agent Independence ✓
- [x] GraphRAG agent does not use Bedrock Agent ID
- [x] No imports from firefighting agent
- [x] Properly inherits from BaseAgent
- [x] Independent module path (agents.graphrag_agent.agent)

### 3. System Integration ✓
- [x] All required files exist:
  - agents/graphrag_agent/__init__.py
  - agents/graphrag_agent/agent.py
  - agents/graphrag_agent/workflow_agents.py
  - agents/graphrag_agent/tools.py
  - agents/graphrag_agent/prompts.py
  - agents/graphrag_agent/metrics.py
- [x] GraphRAG agent can be imported
- [x] Workflow agents can be imported (QueryAnalysisAgent, RetrievalAgent, SynthesisAgent)
- [x] All 3 workflow tasks are defined
- [x] Tools can be imported (classify_query, extract_entities, kb_retrieve)
- [x] All prompts are available (query_analysis, kb_retrieval, response_synthesis)

### 4. Performance Monitoring ✓
- [x] Metrics system is configured
- [x] CloudWatch metrics integration ready
- [x] Performance targets defined:
  - Average response time < 30 seconds
  - Query analysis < 5 seconds
  - KB retrieval < 10 seconds
  - Response synthesis < 15 seconds

### 5. Error Handling ✓
- [x] Error handling methods implemented:
  - _handle_workflow_failure
  - _generate_user_friendly_error_message
  - _classify_error
- [x] Retry logic with exponential backoff
- [x] All tools have try-except blocks
- [x] User-friendly error messages

### 6. 11-Document Coverage ✓
- [x] Prompt mentions 11-document coverage
- [x] 11 examples in query analysis prompt
- [x] All 11 documents mentioned in examples:
  1. FSS 합본
  2. SOLAS Chapter II-2
  3. SOLAS 2017 Insulation penetration
  4. IGC Code
  5. DNV-RU-SHIP Pt4 Ch6
  6. DNV-RU-SHIP Pt6 Ch5 Sec4
  7. Design guidance_Support
  8. Design guidance_Spoolcutting
  9. Design guidance_hull penetration
  10. Piping practice_Support
  11. Piping practice_hull penetration
- [x] All 4 document categories handled (규정, 선급, 설계, 실무)

---

## 🚀 Deployment Steps

### Phase 1: Lambda Function Deployment

#### 1.1 Deploy classify_query Lambda
```bash
cd lambda_package/graphrag_tools/classify_query
zip -r classify_query.zip .
aws lambda create-function \
  --function-name graphrag-classify-query \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --zip-file fileb://classify_query.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0,AWS_REGION=us-west-2}"
```

#### 1.2 Deploy extract_entities Lambda
```bash
cd lambda_package/graphrag_tools/extract_entities
zip -r extract_entities.zip .
aws lambda create-function \
  --function-name graphrag-extract-entities \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --zip-file fileb://extract_entities.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0,AWS_REGION=us-west-2}"
```

#### 1.3 Deploy kb_retrieve Lambda
```bash
cd lambda_package/graphrag_tools/kb_retrieve
zip -r kb_retrieve.zip .
aws lambda create-function \
  --function-name graphrag-kb-retrieve \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --zip-file fileb://kb_retrieve.zip \
  --timeout 60 \
  --memory-size 1024 \
  --environment Variables="{BEDROCK_KB_ID=ZGBA1R5CS0,AWS_REGION=us-west-2}"
```

#### 1.4 Verify Lambda Deployments
```bash
# Test classify_query
aws lambda invoke \
  --function-name graphrag-classify-query \
  --payload '{"question":"고정식 CO2 소화 시스템의 최소 용량은?"}' \
  response.json

# Test extract_entities
aws lambda invoke \
  --function-name graphrag-extract-entities \
  --payload '{"question":"배관 관통부의 단열재 요구사항은?"}' \
  response.json

# Test kb_retrieve
aws lambda invoke \
  --function-name graphrag-kb-retrieve \
  --payload '{"query":"CO2 system capacity","num_results":10,"rerank":true,"kb_id":"ZGBA1R5CS0"}' \
  response.json
```

### Phase 2: Environment Configuration

#### 2.1 Update .env file
```bash
# Add Lambda function ARNs
LAMBDA_CLASSIFY_QUERY_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-classify-query
LAMBDA_EXTRACT_ENTITIES_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-extract-entities
LAMBDA_KB_RETRIEVE_ARN=arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-kb-retrieve

# Optional: Reranker model ARN
RERANKER_MODEL_ARN=arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0

# Feature flag (already enabled in config/agents.yaml)
GRAPHRAG_ENABLED=true
```

#### 2.2 Update config/agents.yaml
Update Lambda function names with actual ARNs if needed:
```yaml
graphrag:
  lambda_function_names:
    classify_query: "arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-classify-query"
    extract_entities: "arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-extract-entities"
    kb_retrieve: "arn:aws:lambda:us-west-2:ACCOUNT_ID:function:graphrag-kb-retrieve"
  reranker_model_arn: "arn:aws:bedrock:us-west-2::foundation-model/cohere.rerank-v3-5:0"
```

### Phase 3: IAM Permissions

#### 3.1 Lambda Execution Role
Ensure Lambda execution role has these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
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
        "bedrock:Retrieve"
      ],
      "Resource": "arn:aws:bedrock:us-west-2:*:knowledge-base/ZGBA1R5CS0"
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

#### 3.2 Streamlit Application Role
Ensure application has permission to invoke Lambda:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": [
        "arn:aws:lambda:us-west-2:*:function:graphrag-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-west-2::foundation-model/*"
    }
  ]
}
```

### Phase 4: Integration Testing

#### 4.1 Test GraphRAG Agent in Streamlit
```bash
# Start Streamlit application
streamlit run app.py

# In UI:
# 1. Select "GraphRAG 검색" agent
# 2. Test with sample questions:
#    - "고정식 CO2 소화 시스템의 최소 용량은?"
#    - "배관 관통부의 단열재 요구사항은?"
#    - "DNV 선급 규칙에서 단열재 요구사항은?"
```

#### 4.2 Verify Response Format
Check that responses include:
- [x] Korean language answer
- [x] References with source_file, page_number, ocr_text
- [x] Proper formatting for ReferenceDisplay component

#### 4.3 Test Error Scenarios
- [ ] Test with invalid question
- [ ] Test with Lambda timeout
- [ ] Test with KB unavailable
- [ ] Verify user-friendly error messages

### Phase 5: Performance Validation

#### 5.1 Response Time Testing
Test with various question types and verify:
- [ ] Average response time < 30 seconds
- [ ] Query analysis < 5 seconds
- [ ] KB retrieval < 10 seconds
- [ ] Response synthesis < 15 seconds

#### 5.2 Load Testing
- [ ] Test with multiple concurrent users
- [ ] Verify Lambda concurrency limits
- [ ] Monitor CloudWatch metrics

#### 5.3 Document Coverage Testing
Test questions covering all 11 documents:
- [ ] FSS 합본
- [ ] SOLAS Chapter II-2
- [ ] SOLAS 2017 Insulation penetration
- [ ] IGC Code
- [ ] DNV-RU-SHIP Pt4 Ch6
- [ ] DNV-RU-SHIP Pt6 Ch5 Sec4
- [ ] Design guidance_Support
- [ ] Design guidance_Spoolcutting
- [ ] Design guidance_hull penetration
- [ ] Piping practice_Support
- [ ] Piping practice_hull penetration

### Phase 6: Monitoring Setup

#### 6.1 CloudWatch Dashboards
Create dashboard with:
- [ ] Lambda invocation count
- [ ] Lambda duration
- [ ] Lambda errors
- [ ] KB retrieval metrics
- [ ] Response synthesis metrics

#### 6.2 Alarms
Set up alarms for:
- [ ] Lambda error rate > 5%
- [ ] Average response time > 30s
- [ ] Lambda throttling

#### 6.3 Logging
Verify structured logging:
- [ ] Query analysis logs
- [ ] Retrieval logs
- [ ] Synthesis logs
- [ ] Error logs with stack traces

---

## 📊 Post-Deployment Validation

### Acceptance Criteria
- [ ] All 6 verification tests pass
- [ ] GraphRAG agent is selectable in UI
- [ ] Responses are in Korean
- [ ] References display correctly
- [ ] Average response time < 30 seconds
- [ ] Error handling works correctly
- [ ] Independent from firefighting agent
- [ ] All 11 documents are covered in examples

### Success Metrics
- [ ] 95%+ successful query completion rate
- [ ] Average response time < 30 seconds
- [ ] User satisfaction with answer quality
- [ ] Proper document coverage across all categories

---

## 🔧 Troubleshooting

### Common Issues

#### Lambda Function Not Found
```bash
# Check Lambda function exists
aws lambda get-function --function-name graphrag-classify-query

# Update ARN in config/agents.yaml
```

#### Permission Denied
```bash
# Check IAM role permissions
aws iam get-role-policy --role-name lambda-execution-role --policy-name bedrock-access

# Add missing permissions
```

#### Timeout Errors
```bash
# Increase Lambda timeout
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --timeout 90

# Increase memory
aws lambda update-function-configuration \
  --function-name graphrag-kb-retrieve \
  --memory-size 2048
```

#### Import Errors
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📝 Rollback Plan

If deployment fails:

1. **Disable GraphRAG Agent**
   ```yaml
   # config/agents.yaml
   graphrag:
     enabled: false
   ```

2. **Revert to Previous Version**
   ```bash
   git checkout HEAD~1 agents/graphrag_agent/
   ```

3. **Delete Lambda Functions** (if needed)
   ```bash
   aws lambda delete-function --function-name graphrag-classify-query
   aws lambda delete-function --function-name graphrag-extract-entities
   aws lambda delete-function --function-name graphrag-kb-retrieve
   ```

---

## ✅ Deployment Sign-Off

- [ ] All pre-deployment verification tests passed (6/6)
- [ ] Lambda functions deployed successfully
- [ ] Environment variables configured
- [ ] IAM permissions verified
- [ ] Integration tests passed
- [ ] Performance requirements met
- [ ] Monitoring and logging configured
- [ ] Documentation updated

**Deployment Date:** _________________

**Deployed By:** _________________

**Verified By:** _________________

---

## 📚 Additional Resources

- [Requirements Document](.kiro/specs/graphrag-multi-agent/requirements.md)
- [Design Document](.kiro/specs/graphrag-multi-agent/design.md)
- [Implementation Tasks](.kiro/specs/graphrag-multi-agent/tasks.md)
- [Lambda Deployment Guide](../../lambda_package/graphrag_tools/DEPLOYMENT_GUIDE.md)
- [Testing Documentation](test_final_verification.py)
