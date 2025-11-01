# Lambda Functions Documentation

## Overview

This project includes several AWS Lambda functions that provide enhanced search capabilities using the Strands framework and direct AWS service integration.

## Lambda Functions

### 1. lambda_function.py (Main Strands Tool)

**Location**: `lambda_package/lambda_function.py`

**Purpose**: Primary Lambda function implementing Strands ReAct pattern for advanced search capabilities.

#### Features
- **Strands Agent Integration**: Uses Strands framework for ReAct (Reasoning and Acting) pattern
- **Knowledge Base Tool**: Integrates with AWS Bedrock Knowledge Base
- **Korean Language Support**: Responds in Korean language
- **Session Management**: Handles session-based conversations

#### Implementation Details
```python
# Key components:
- KnowledgeBaseTool: Connects to Knowledge Base (ZGBA1R5CS0)
- Agent: Implements ReAct pattern with specific instructions
- Model: Uses Claude 3.5 Sonnet for reasoning
```

#### Input Parameters
- `inputText`: User query text
- `sessionId`: Session identifier (optional, defaults to 'default')

#### Response Format
```json
{
    "statusCode": 200,
    "body": {
        "result": "Search results in Korean",
        "session_id": "session_identifier",
        "search_method": "strands_react"
    }
}
```

### 2. strands_tool_lambda.py (Alternative Implementation)

**Location**: `strands_tool_lambda.py`

**Purpose**: Alternative implementation of the Strands ReAct search tool with identical functionality to the main lambda function.

#### Key Differences
- Standalone file (not in package directory)
- Same core functionality as main lambda function
- Used for testing and backup deployment

### 3. simple_lambda.py (Test Function)

**Location**: `simple_lambda.py`

**Purpose**: Simple test Lambda function for basic Bedrock Agent Action Group testing.

#### Features
- **Basic Response**: Returns simple Korean response
- **Event Logging**: Logs incoming events for debugging
- **Parameter Extraction**: Handles multiple input parameter formats

#### Use Cases
- Testing Bedrock Agent integration
- Debugging event structure
- Basic functionality verification

### 4. strands_simple_lambda.py (Enhanced Test Function)

**Location**: `strands_simple_lambda.py`

**Purpose**: Enhanced test function that simulates Strands-like behavior using direct AWS services.

#### Features
- **Direct Knowledge Base Access**: Uses Bedrock Agent Runtime for KB queries
- **Enhanced Search**: Performs advanced search with multiple results
- **Result Processing**: Formats and scores search results
- **Error Handling**: Graceful fallback to basic responses

#### Search Configuration
- **Knowledge Base ID**: ZGBA1R5CS0
- **Result Count**: Up to 10 results
- **Content Limit**: 500 characters per result
- **Score Display**: Shows relevance scores

## Deployment Configuration

### Requirements
**File**: `lambda_package/requirements.txt`
```
strands-agents
boto3
```

### Trust Policy
**File**: `lambda_trust_policy.json`
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

### OpenAPI Schema
**File**: `strands_tool_schema.json`

Defines the API schema for Bedrock Agent integration:
- **Endpoint**: `/search` (POST)
- **Operation ID**: `strandsReactSearch`
- **Input**: JSON with `query` parameter
- **Output**: JSON with `result` field

## Lambda Layers

### Layer Structure
The project includes pre-built Lambda layers with dependencies:

#### layer/python/
- **Core Dependencies**: boto3, strands-agents, and related packages
- **Size Optimization**: Includes only necessary packages
- **Python Version**: Compatible with Python 3.11

#### lambda_layer/python/
- **Alternative Layer**: Additional layer configuration
- **Strands Framework**: Includes Strands agents framework
- **NumPy Support**: Includes NumPy for data processing

## Error Handling

### Exception Management
All Lambda functions implement comprehensive error handling:

```python
try:
    # Main logic
    result = strands_agent.run(input_text)
    return success_response
except Exception as e:
    return {
        'statusCode': 500,
        'body': {
            'error': str(e),
            'result': f"검색 중 오류가 발생했습니다: {str(e)}"
        }
    }
```

### Common Error Scenarios
1. **Strands Framework Errors**: Model access or tool initialization issues
2. **AWS Service Errors**: Knowledge Base or Bedrock access problems
3. **Input Validation**: Missing or malformed input parameters
4. **Timeout Issues**: Long-running search operations

## Performance Considerations

### Cold Start Optimization
- **Layer Usage**: Dependencies in layers reduce cold start time
- **Import Optimization**: Minimal imports in handler function
- **Connection Reuse**: AWS clients initialized outside handler

### Memory and Timeout Settings
- **Recommended Memory**: 512MB - 1GB
- **Timeout**: 30-60 seconds for complex searches
- **Concurrent Executions**: Configure based on expected load

## Integration with Bedrock Agent

### Action Group Configuration
1. **Schema Upload**: Use `strands_tool_schema.json`
2. **Lambda ARN**: Point to deployed function
3. **Permissions**: Ensure Bedrock can invoke Lambda

### Testing Integration
Use the test functions to verify:
- Event structure from Bedrock Agent
- Parameter passing
- Response format compatibility

## Monitoring and Logging

### CloudWatch Logs
- **Function Logs**: Automatic logging of function execution
- **Error Tracking**: Exception details and stack traces
- **Performance Metrics**: Duration and memory usage

### Custom Logging
```python
print(f"Received event: {json.dumps(event)}")
print(f"Processing query: {input_text}")
```

## Deployment Best Practices

### Packaging
1. **Dependencies**: Use layers for large dependencies
2. **Code Size**: Keep function code minimal
3. **Environment Variables**: Use for configuration

### Security
1. **IAM Roles**: Minimal required permissions
2. **VPC Configuration**: If accessing private resources
3. **Environment Variables**: Encrypt sensitive data

### Version Management
1. **Aliases**: Use aliases for different environments
2. **Versioning**: Tag versions for rollback capability
3. **Testing**: Test in staging before production deployment