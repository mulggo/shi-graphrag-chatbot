# Testing Utilities Documentation

## Overview

This project includes several utility scripts for testing and debugging the chatbot system. These tools help verify functionality, extract references, and analyze system behavior.

## Testing Scripts

### 1. test_agent_trace.py

**Purpose**: Comprehensive testing of Bedrock Agent with detailed trace analysis.

#### Features
- **Full Trace Analysis**: Captures and analyzes all trace events from Bedrock Agent
- **Reference Extraction**: Identifies and displays knowledge base references
- **Event Structure Analysis**: Examines the structure of trace events
- **Debug Output**: Detailed logging of agent interaction flow

#### Key Functionality
```python
# Main test function
def test_agent_with_trace():
    # Invokes agent with trace enabled
    response = client.invoke_agent(
        agentId='WT3ZJ25XCL',
        agentAliasId='3RWZZLJDY1',
        sessionId=session_id,
        inputText='선박 설계시 firefighting 규칙에 대해 알려주세요',
        enableTrace=True
    )
```

#### Output Analysis
- **Completion Text**: Final agent response
- **Trace Events**: Detailed breakdown of each trace event
- **Knowledge Base Lookups**: References found during search
- **Orchestration Flow**: Step-by-step agent reasoning process

#### Usage
```bash
python test_agent_trace.py
```

### 2. extract_references.py

**Purpose**: Extracts and analyzes reference information from agent responses.

#### Features
- **Reference Parsing**: Extracts references from agent trace data
- **Content Analysis**: Analyzes reference content and metadata
- **Base64 Decoding**: Handles byte content in references
- **Structured Output**: Organized display of reference information

#### Reference Data Structure
```python
ref_data = {
    'content': content_text,
    'source_file': ref.get('metadata', {}).get('x-amz-bedrock-kb-source-uri', ''),
    'page_number': ref.get('metadata', {}).get('x-amz-bedrock-kb-document-page-number', 0),
    'description': ref.get('metadata', {}).get('x-amz-bedrock-kb-description', '')
}
```

#### Content Processing
- **Text Content**: Direct text extraction from references
- **Byte Content**: Base64 decoding for binary content
- **Error Handling**: Graceful handling of decode errors
- **Content Preview**: Shows first 500 characters of each reference

#### Usage
```bash
python extract_references.py
```

### 3. get_kb_text.py

**Purpose**: Direct testing of Knowledge Base retrieval functionality.

#### Features
- **Direct KB Access**: Bypasses agent to test Knowledge Base directly
- **Vector Search**: Uses vector search configuration
- **Result Analysis**: Detailed analysis of retrieval results
- **Metadata Extraction**: Extracts all available metadata

#### Search Configuration
```python
response = client.retrieve(
    knowledgeBaseId='ZGBA1R5CS0',
    retrievalQuery={
        'text': 'firefighting 고정식 소화 시스템'
    },
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 3
        }
    }
)
```

#### Result Processing
- **Score Analysis**: Shows relevance scores for each result
- **Content Extraction**: Displays text content from results
- **Location Information**: S3 location details
- **OCR Text**: Extracted OCR text from document metadata
- **Image URIs**: Original document image locations

#### Usage
```bash
python get_kb_text.py
```

## Test Data Files

### payload.txt
Contains sample input payload for testing Lambda functions.

### test_payload.json
JSON formatted test payload for structured testing.

### response.json
Sample response data for reference and comparison.

## Debugging Features

### Trace Event Analysis
All testing utilities provide detailed trace event analysis:

#### Event Types
- **Orchestration Trace**: Main agent reasoning flow
- **Knowledge Base Lookup**: Search operations
- **Observation Events**: Agent observations and decisions
- **Action Events**: Tool invocations and responses

#### Data Extraction
- **Reference Metadata**: Complete metadata extraction
- **Content Processing**: Text and binary content handling
- **Location Tracking**: S3 URIs and document locations
- **Score Analysis**: Relevance scoring information

### Error Handling
Comprehensive error handling in all utilities:

```python
try:
    # Main testing logic
    response = client.invoke_agent(...)
    # Process response
except Exception as e:
    print(f"Error: {e}")
    return "", []
```

## Output Formats

### Console Output
All utilities provide structured console output:

```
=== AGENT RESPONSE ===
[Agent response text]

=== EXTRACTED REFERENCES (N) ===
[1] 참조 문서:
파일: document.pdf
페이지: 1
참조 텍스트 (처음 500자):
[Content preview...]
총 길이: 1234 문자
```

### JSON Output
Structured data output for programmatic use:

```json
{
    "completion": "Agent response",
    "references": [
        {
            "source_file": "document.pdf",
            "page_number": 1,
            "content": "Reference text",
            "description": "OCR extracted text"
        }
    ]
}
```

## Performance Testing

### Response Time Analysis
- **Agent Invocation Time**: Time to get agent response
- **Reference Processing Time**: Time to extract references
- **Total Processing Time**: End-to-end processing time

### Memory Usage
- **Content Size Analysis**: Size of extracted content
- **Reference Count**: Number of references per query
- **Metadata Size**: Size of metadata information

## Integration Testing

### End-to-End Testing
1. **Agent Invocation**: Test complete agent workflow
2. **Reference Extraction**: Verify reference processing
3. **Content Display**: Test content rendering
4. **Error Scenarios**: Test error handling

### Component Testing
1. **Knowledge Base**: Direct KB testing
2. **Lambda Functions**: Individual function testing
3. **Trace Processing**: Trace event handling
4. **Content Processing**: Reference content handling

## Usage Recommendations

### Development Workflow
1. **Start with get_kb_text.py**: Test Knowledge Base connectivity
2. **Use test_agent_trace.py**: Verify agent integration
3. **Run extract_references.py**: Test reference processing
4. **Check output formats**: Verify data structure

### Debugging Process
1. **Check AWS Credentials**: Ensure proper authentication
2. **Verify Resource IDs**: Confirm agent and KB IDs
3. **Test Network Connectivity**: Check region and endpoints
4. **Analyze Error Messages**: Use detailed error output

### Performance Optimization
1. **Monitor Response Times**: Track performance metrics
2. **Analyze Reference Counts**: Optimize search parameters
3. **Check Content Sizes**: Monitor memory usage
4. **Test Concurrent Usage**: Verify scalability

## Common Issues and Solutions

### Authentication Issues
- **Solution**: Check AWS credentials and permissions
- **Verification**: Use `aws sts get-caller-identity`

### Resource Access Issues
- **Solution**: Verify resource IDs and region settings
- **Verification**: Check AWS console for resource status

### Content Processing Issues
- **Solution**: Check encoding and content types
- **Verification**: Use debug output to analyze content structure

### Performance Issues
- **Solution**: Optimize search parameters and result counts
- **Verification**: Monitor CloudWatch metrics