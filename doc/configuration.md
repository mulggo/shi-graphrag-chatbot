# Multi-Agent System Configuration Documentation

## Overview

This document describes the configuration system for the multi-agent Ship Firefighting Rules Chatbot, including agent definitions, AWS resources, and application settings.

## Core Configuration Files

### 1. config/agents.yaml (Primary Configuration)

**Purpose**: Central configuration file defining all agents, their capabilities, and AWS resource mappings.

#### Agent Configuration Structure
```yaml
agents:
  firefighting:
    display_name: "선박 소방 규정"
    description: "선박 소방 시스템 및 SOLAS 규정 전문가"
    module_path: "agents.firefighting_agent.agent"
    bedrock_agent_id: "WT3ZJ25XCL"
    bedrock_alias_id: "3RWZZLJDY1"
    knowledge_base_id: "ZGBA1R5CS0"
    enabled: true
    ui_config:
      icon: "🚢"
      color: "#FF6B6B"
      topics:
        - "고정식 소화 시스템"
        - "휴대용 소화기"
        - "배수 시스템"
        - "안전 구역"
        - "SOLAS 규정"

global_config:
  aws_region: "us-west-2"
  default_language: "ko"
  session_timeout: 3600
  max_message_length: 4000
  enable_tracing: true
```

#### Configuration Parameters
- **display_name**: Human-readable agent name for UI
- **description**: Agent purpose and capabilities
- **module_path**: Python import path to agent implementation
- **bedrock_agent_id**: AWS Bedrock Agent identifier
- **bedrock_alias_id**: Bedrock Agent alias for versioning
- **knowledge_base_id**: Associated Knowledge Base identifier
- **enabled**: Agent activation status
- **ui_config**: User interface customization settings

#### Adding New Agents
1. Define agent in `config/agents.yaml`
2. Implement agent class in specified module path
3. Configure AWS Bedrock Agent and Knowledge Base
4. Test agent functionality through AgentManager

### 2. .streamlit/config.toml (Streamlit Configuration)

**Purpose**: Streamlit application configuration for optimal performance and compatibility.

#### Configuration Structure
```toml
[server]
headless = true
runOnSave = false
port = 8501
enableCORS = true
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"

[client]
caching = false
displayEnabled = true
showErrorDetails = true

[logger]
level = "info"
```

#### Key Settings
- **headless**: Runs without browser auto-opening
- **enableCORS**: Enables cross-origin requests for CloudFront
- **enableXsrfProtection**: Disabled for API compatibility
- **caching**: Disabled for real-time updates
- **serverAddress**: Binds to all interfaces for deployment

#### CloudFront Compatibility
These settings optimize Streamlit for CloudFront deployment and WebSocket functionality.

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
- **Agent ID**: `WT3ZJ25XCL`
- **Agent Alias ID**: `3RWZZLJDY1`
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