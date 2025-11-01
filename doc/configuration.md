# Configuration Documentation

## Overview

This document describes the configuration files and settings used in the Ship Firefighting Rules Chatbot project.

## Configuration Files

### 1. strands_tool_schema.json

**Purpose**: OpenAPI schema definition for the Strands ReAct search tool integration with Bedrock Agent.

#### Schema Structure
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Strands ReAct Search",
    "version": "1.0.0",
    "description": "Advanced ReAct search tool"
  }
}
```

#### API Endpoint Definition
- **Path**: `/search`
- **Method**: POST
- **Operation ID**: `strandsReactSearch`
- **Description**: "Use this when default search fails to find relevant information"

#### Request Schema
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query"
    }
  },
  "required": ["query"]
}
```

#### Response Schema
```json
{
  "type": "object",
  "properties": {
    "result": {
      "type": "string",
      "description": "Search result"
    }
  }
}
```

#### Usage in Bedrock Agent
1. Upload schema to Bedrock Agent Action Group
2. Associate with Lambda function
3. Configure as tool for enhanced search capabilities

### 2. lambda_trust_policy.json

**Purpose**: IAM trust policy for Lambda function execution role.

#### Policy Structure
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

#### Key Components
- **Version**: Policy language version (2012-10-17)
- **Effect**: Allow access
- **Principal**: AWS Lambda service
- **Action**: Assume role permission

#### Usage
1. Create IAM role for Lambda function
2. Attach this trust policy to the role
3. Add necessary execution policies (Bedrock, S3, CloudWatch)

### 3. requirements.txt (Lambda Package)

**Purpose**: Python dependencies for Lambda function deployment.

#### Dependencies
```
strands-agents
boto3
```

#### Package Details
- **strands-agents**: Strands framework for ReAct pattern implementation
- **boto3**: AWS SDK for Python

#### Installation
```bash
pip install -r requirements.txt
```

## AWS Resource Configuration

### Bedrock Agent Configuration

#### Agent Settings
- **Agent ID**: `H5YNZKKNSW`
- **Agent Alias ID**: `FD3LV7TEN4`
- **Region**: `us-west-2`
- **Model**: Claude 3.5 Sonnet

#### Action Group Configuration
- **Name**: Strands ReAct Search
- **Schema**: `strands_tool_schema.json`
- **Lambda Function**: Strands tool implementation
- **Description**: Advanced search capabilities

### Knowledge Base Configuration

#### Knowledge Base Settings
- **Knowledge Base ID**: `ZGBA1R5CS0`
- **Region**: `us-west-2`
- **Vector Database**: Amazon OpenSearch Serverless
- **Embedding Model**: Amazon Titan Embeddings

#### Data Source Configuration
- **Source Type**: S3 bucket
- **Document Format**: PDF files
- **Processing**: OCR enabled for image extraction
- **Chunking Strategy**: Semantic chunking

### Lambda Function Configuration

#### Runtime Settings
- **Runtime**: Python 3.11
- **Architecture**: x86_64
- **Memory**: 512MB - 1GB (recommended)
- **Timeout**: 30-60 seconds

#### Environment Variables
No specific environment variables required. AWS credentials handled via IAM roles.

#### Layer Configuration
- **Layer 1**: Strands agents and dependencies
- **Layer 2**: Additional Python packages
- **Total Size**: Optimized for cold start performance

## Application Configuration

### Streamlit Configuration

#### Page Settings
```python
st.set_page_config(
    page_title="선박 Firefighting 규칙 챗봇",
    page_icon="🚢",
    layout="wide"
)
```

#### AWS Client Configuration
```python
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-agent-runtime', region_name='us-west-2')

@st.cache_resource
def get_s3_client():
    return boto3.client('s3', region_name='us-west-2')
```

### Session Management
- **Session ID**: UUID-based unique identifiers
- **Message Storage**: In-memory session state
- **Conversation History**: Maintained per session

## Security Configuration

### IAM Permissions

#### Lambda Execution Role
Required permissions:
- `bedrock:InvokeAgent`
- `bedrock:Retrieve`
- `s3:GetObject`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

#### Bedrock Agent Role
Required permissions:
- `lambda:InvokeFunction`
- `bedrock:InvokeModel`
- Knowledge Base access permissions

### Network Configuration
- **VPC**: Not required for basic setup
- **Security Groups**: Default settings sufficient
- **Subnets**: Public subnets for internet access

## Performance Configuration

### Caching Strategy
- **AWS Clients**: Cached using Streamlit's `@st.cache_resource`
- **Session Data**: In-memory caching
- **Response Caching**: Not implemented (real-time responses)

### Optimization Settings
- **Lambda Memory**: 512MB minimum for Strands framework
- **Knowledge Base Results**: Limited to 10 results per query
- **Content Display**: Truncated for performance

## Monitoring Configuration

### CloudWatch Logs
- **Lambda Logs**: Automatic logging enabled
- **Application Logs**: Streamlit logging to console
- **Error Tracking**: Exception logging in all components

### Metrics Collection
- **Lambda Metrics**: Duration, memory usage, error rate
- **Agent Metrics**: Invocation count, success rate
- **Knowledge Base Metrics**: Query performance, result quality

## Environment-Specific Configuration

### Development Environment
- **Local Testing**: Use AWS CLI credentials
- **Debug Mode**: Enhanced logging enabled
- **Test Data**: Sample queries and responses

### Production Environment
- **IAM Roles**: Service-specific roles
- **Monitoring**: CloudWatch alarms configured
- **Scaling**: Auto-scaling for Lambda functions

## Configuration Best Practices

### Security
1. **Least Privilege**: Minimal required permissions
2. **Role Separation**: Separate roles for different services
3. **Credential Management**: No hardcoded credentials

### Performance
1. **Resource Sizing**: Appropriate memory and timeout settings
2. **Caching**: Effective use of caching mechanisms
3. **Connection Reuse**: Persistent connections where possible

### Maintainability
1. **Configuration Files**: Centralized configuration
2. **Environment Variables**: Environment-specific settings
3. **Documentation**: Clear configuration documentation

## Troubleshooting Configuration Issues

### Common Problems
1. **Permission Errors**: Check IAM roles and policies
2. **Resource Not Found**: Verify resource IDs and regions
3. **Timeout Issues**: Adjust Lambda timeout settings
4. **Memory Issues**: Increase Lambda memory allocation

### Diagnostic Steps
1. **Check AWS Credentials**: `aws sts get-caller-identity`
2. **Verify Resource Access**: Test individual service calls
3. **Review CloudWatch Logs**: Check for error messages
4. **Test Configuration**: Use utility scripts for validation

### Configuration Validation
1. **Schema Validation**: Verify OpenAPI schema format
2. **Policy Validation**: Check IAM policy syntax
3. **Resource Validation**: Confirm resource existence
4. **Integration Testing**: End-to-end configuration testing