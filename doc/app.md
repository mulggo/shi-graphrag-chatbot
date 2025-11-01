# Application Documentation (app.py)

## Overview

The main Streamlit application (`app.py`) provides an interactive web interface for the Ship Firefighting Rules Chatbot. It integrates with AWS Bedrock Agent to deliver intelligent responses about ship firefighting regulations.

## Key Features

### 1. Streamlit Web Interface
- **Page Configuration**: Configured with ship emoji (🚢) and wide layout
- **Korean Language Support**: Full Korean language interface
- **Responsive Design**: Optimized for various screen sizes

### 2. AWS Integration
- **Bedrock Agent Runtime**: Connects to AWS Bedrock Agent for intelligent responses
- **S3 Client**: Downloads and displays original document images
- **Session Management**: Maintains conversation context using UUID-based sessions

### 3. Reference System
- **Document References**: Extracts and displays source document information
- **OCR Text Display**: Shows extracted text from PDF documents
- **Image Viewer**: Displays original PDF page images from S3
- **Metadata Information**: Provides document metadata including page numbers

## Core Components

### AWS Client Initialization
```python
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-agent-runtime', region_name='us-west-2')

@st.cache_resource
def get_s3_client():
    return boto3.client('s3', region_name='us-west-2')
```

### Session State Management
- `messages`: Stores conversation history
- `session_id`: Unique identifier for each chat session

### Reference Processing
The application processes trace events from Bedrock Agent to extract:
- Source file names
- Page numbers
- OCR extracted text
- S3 image URIs

## User Interface Components

### Main Chat Interface
- **Chat Input**: Text input for user queries
- **Message Display**: Shows conversation history with role-based styling
- **Reference Links**: Clickable reference numbers in responses

### Reference Display
- **Expandable Sections**: Each reference shown in collapsible expander
- **OCR Text Area**: Scrollable text area showing extracted content
- **Image Display**: Full-width image display with zoom capability
- **Metadata JSON**: Structured display of document information

### Sidebar Information
- **Session Information**: Current session ID and message count
- **New Session Button**: Resets conversation and generates new session ID
- **Supported Topics**: List of available query topics
- **Usage Instructions**: Brief guide on how to use the system

## Configuration

### AWS Resources
- **Agent ID**: `H5YNZKKNSW`
- **Agent Alias ID**: `FD3LV7TEN4`
- **Region**: `us-west-2`

### Streamlit Configuration
- **Page Title**: "선박 Firefighting 규칙 챗봇"
- **Page Icon**: 🚢
- **Layout**: Wide mode for better content display

## Error Handling

### S3 Image Loading
- Graceful handling of missing or inaccessible images
- User-friendly error messages
- Fallback to text-only display when images fail

### Agent Communication
- Exception handling for Bedrock Agent API calls
- Error message display to users
- Continuation of service despite individual request failures

## Performance Optimizations

### Caching
- AWS clients cached using `@st.cache_resource`
- Prevents repeated client initialization
- Improves response times

### Streaming Response
- Real-time display of agent responses
- Progressive loading of reference information
- Enhanced user experience with immediate feedback

## Usage Examples

### Basic Query
```
User: "선박 설계시 firefighting 규칙에 대해 알려주세요"
System: [Processes query through Bedrock Agent]
Response: [Detailed answer with references]
```

### Reference Interaction
1. User receives response with reference numbers [1], [2], etc.
2. References displayed in expandable sections below response
3. Each reference shows OCR text and original image
4. Metadata provides additional document context

## Troubleshooting

### Common Issues
1. **AWS Credentials**: Ensure proper AWS configuration
2. **Region Settings**: Verify us-west-2 region access
3. **Agent Permissions**: Check Bedrock Agent access permissions
4. **S3 Access**: Verify S3 bucket read permissions

### Debug Information
- Session ID displayed in sidebar for tracking
- Error messages shown directly in interface
- Console logging for development debugging

## Future Enhancements

### Planned Features
- Multi-language response support
- Advanced search filters
- Document upload capability
- Export conversation history
- Enhanced reference linking system