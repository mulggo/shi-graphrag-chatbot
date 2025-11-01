# Ship Firefighting Rules Chatbot

A GraphRAG-powered chatbot system for ship firefighting regulations using AWS Bedrock Agent and Strands framework.

## Overview

This project implements an intelligent chatbot that provides information about ship firefighting regulations, particularly focusing on SOLAS (Safety of Life at Sea) standards and DNV-RU-SHIP rules. The system uses AWS Bedrock Agent with Knowledge Base integration and Strands ReAct pattern for enhanced search capabilities.

## Features

- **Interactive Streamlit Web Interface**: User-friendly chat interface with Korean language support
- **AWS Bedrock Agent Integration**: Leverages AWS Bedrock Agent for intelligent responses
- **Knowledge Base Search**: Retrieves information from ship firefighting regulation documents
- **Reference Display**: Shows source documents with OCR text and original images
- **Strands ReAct Pattern**: Advanced search using ReAct (Reasoning and Acting) methodology
- **Multi-language Support**: Korean and English documentation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Bedrock Agent  │    │  Knowledge Base │
│   Frontend      │───▶│   (H5YNZKKNSW)   │───▶│   (ZGBA1R5CS0)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Lambda Function │
                       │  (Strands Tool)  │
                       └──────────────────┘
```

## Project Structure

```
shi-graphrag-chatbot/
├── app.py                          # Main Streamlit application
├── lambda_package/                 # Lambda function package
│   ├── lambda_function.py         # Strands ReAct search tool
│   └── requirements.txt           # Lambda dependencies
├── layer/                         # Lambda layer with dependencies
├── lambda_layer/                  # Additional lambda layer
├── extract_references.py         # Reference extraction utility
├── get_kb_text.py                # Knowledge base testing utility
├── test_agent_trace.py           # Agent tracing test script
├── simple_lambda.py              # Simple test lambda
├── strands_tool_lambda.py        # Strands tool implementation
├── strands_tool_schema.json      # OpenAPI schema for Strands tool
├── lambda_trust_policy.json      # IAM trust policy for Lambda
└── doc/                          # Documentation directory
```

## Quick Start

### Prerequisites

- AWS Account with Bedrock access
- Python 3.11+
- Streamlit
- AWS CLI configured

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd shi-graphrag-chatbot
```

2. Install dependencies:
```bash
pip install streamlit boto3 strands-agents
```

3. Configure AWS credentials:
```bash
aws configure
```

4. Run the Streamlit application:
```bash
streamlit run app.py
```

## Configuration

### AWS Resources

- **Bedrock Agent ID**: `H5YNZKKNSW`
- **Agent Alias ID**: `FD3LV7TEN4`
- **Knowledge Base ID**: `ZGBA1R5CS0`
- **Region**: `us-west-2`

### Environment Variables

No additional environment variables required. AWS credentials should be configured via AWS CLI or IAM roles.

## Usage

1. Open the Streamlit web interface
2. Ask questions about ship firefighting regulations in Korean or English
3. View responses with source document references
4. Click on reference numbers to see original documents and OCR text
5. Access original PDF images stored in S3

### Example Queries

- "선박 설계시 firefighting 규칙에 대해 알려주세요"
- "고정식 소화 시스템의 요구사항은 무엇인가요?"
- "SOLAS 규정에 따른 휴대용 소화기 배치 기준"

## Development

### Lambda Function Deployment

1. Package the Lambda function:
```bash
cd lambda_package
zip -r ../lambda_function.zip .
```

2. Deploy using AWS CLI or Console

### Testing

Run test scripts to verify functionality:

```bash
python test_agent_trace.py
python extract_references.py
python get_kb_text.py
```

## Documentation

Detailed documentation is available in the `doc/` directory:

- [Application Documentation](doc/app.md)
- [Lambda Functions](doc/lambda_functions.md)
- [Testing Utilities](doc/testing_utilities.md)
- [Configuration Files](doc/configuration.md)

Korean versions are also available with `-ko` suffix.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please contact the development team or create an issue in the repository.