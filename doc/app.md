# Multi-Agent Application Documentation (app.py)

## Overview

The main Streamlit application (`app.py`) provides a unified interface for the multi-agent Ship Firefighting Rules Chatbot system. It features conditional UI modes, knowledge graph visualization, and intelligent agent routing.

## Architecture Overview

The application operates in two primary modes:
1. **Chat Mode**: Interactive Q&A with specialized agents
2. **Graph Mode**: Knowledge graph visualization and exploration

## Key Features

### 1. Multi-Agent Interface
- **Agent Manager Integration**: Centralized agent routing and management
- **Configuration-Driven**: Agents loaded from YAML configuration
- **Conditional UI**: Chat interface hidden during graph visualization
- **Agent Selection**: Multiple knowledge base options (bda-neptune, bda-neptune-2)

### 2. Knowledge Graph Visualization
- **Dual Graph Types**: GraphRAG (Neptune Analytics) and FSS Ontology (SPARQL)
- **Interactive Visualization**: 900px height with full interactivity
- **Real-time Switching**: Seamless transition between graph types
- **Performance Optimized**: Handles 2,000+ nodes efficiently

### 3. Enhanced Chat System
- **Multi-Agent Support**: Routes queries to appropriate specialized agents
- **Reference Integration**: Advanced document reference extraction and display
- **Session Management**: Persistent conversation context
- **Korean/English Support**: Bilingual interface and responses

### 4. Data Structure Guide
- **System Architecture**: Comprehensive documentation of data models
- **Neptune Analytics**: GraphRAG structure with 7,552 nodes and 11,949 edges
- **Neptune DB**: SPARQL ontology with 653 triples and 42 classes
- **Visual Statistics**: Real-time metrics and data distribution across systems

## Core Components

### Multi-Agent System Integration
```python
# Agent Manager initialization
@st.cache_resource
def get_agent_manager():
    return AgentManager()

# UI Components initialization  
@st.cache_resource
def get_ui_components(_agent_manager):
    return {
        'agent_selector': AgentSelector(_agent_manager),
        'chat_interface': ChatInterface(_agent_manager),
        'reference_display': ReferenceDisplay(),
        'sidebar': Sidebar(_agent_manager)
    }
```

### Session State Management
- `messages`: Conversation history with agent attribution
- `session_id`: UUID-based session identifier
- `selected_agent`: Currently active agent
- `show_knowledge_graph`: Graph visualization state
- `selected_graph_type`: Active graph type

### Conditional UI Logic
```python
# Chat mode (when graph is not active)
if not st.session_state.get('show_knowledge_graph', False):
    # Show chat interface
    ui_components['chat_interface'].render_chat_history()

# Graph mode (when graph is selected)
if st.session_state.get('show_knowledge_graph', False):
    # Show knowledge graph visualization
    selected_graph_type = st.session_state.get('selected_graph_type')
```

## User Interface Components

### Unified Sidebar (`ui/sidebar.py`)
- **System Information**: Agent status and availability
- **GraphRAG Section**: Knowledge base selection (bda-neptune, bda-neptune-2)
- **Knowledge Graph Selector**: Graph type selection with radio buttons
- **Agent Information**: Current agent capabilities and supported topics
- **Session Management**: Session controls and information

### Chat Interface (`ui/chat_interface.py`)
- **Conditional Display**: Only shown when graph mode is inactive
- **Agent Attribution**: Messages tagged with responsible agent
- **Reference Integration**: Seamless reference display
- **Multi-Agent History**: Conversation context across agent switches

### Knowledge Graph Viewer
- **GraphRAG Visualization**: Neptune Analytics with 2,000 nodes, 3,000 edges
- **FSS Ontology Graph**: SPARQL-based semantic relationships
- **Interactive Controls**: Zoom, pan, node selection
- **Performance Optimized**: 900px height with smooth rendering

### Data Structure Guide (`data_structure_guide.py`)
- **Three-Tab Interface**: Overview, GraphRAG, and GraphDB sections
- **System Documentation**: Detailed explanation of data models
- **Real-time Statistics**: Current node, edge, and triple counts
- **Architecture Diagrams**: Visual representation of data relationships

### Reference Display (`ui/reference_display.py`)
- **Enhanced Metadata**: Source attribution and confidence scores
- **Image Integration**: S3-hosted original document images
- **OCR Text Extraction**: Searchable document content
- **Multi-Format Support**: PDF, image, and text references

## Configuration

### Current AWS Resources
- **Bedrock Agent ID**: `WT3ZJ25XCL`
- **Agent Alias ID**: `3RWZZLJDY1`
- **Knowledge Base ID**: `ZGBA1R5CS0`
- **Region**: `us-west-2`

### Neptune Resources
- **Analytics Graph**: `g-gqisj8edd6`
- **SPARQL Endpoint**: `shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com`

### Agent Configuration (`config/agents.yaml`)
```yaml
agents:
  firefighting:
    display_name: "선박 소방 규정"
    bedrock_agent_id: "WT3ZJ25XCL"
    bedrock_alias_id: "3RWZZLJDY1"
    knowledge_base_id: "ZGBA1R5CS0"
    enabled: true
```

### Streamlit Configuration (`.streamlit/config.toml`)
```toml
[server]
headless = true
port = 8501
enableCORS = true

[browser]
gatherUsageStats = false
```

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