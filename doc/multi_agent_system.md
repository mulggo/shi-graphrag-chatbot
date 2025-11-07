# Multi-Agent System Documentation

## Overview

The Ship Firefighting Rules Chatbot uses a modular multi-agent architecture that allows for easy extension and maintenance of specialized AI agents for different regulation domains.

## Architecture Components

### Agent Manager (`core/agent_manager.py`)

The central orchestrator that manages all agents in the system.

**Key Features:**
- **Dynamic Agent Loading**: Loads agents based on YAML configuration
- **Message Routing**: Routes user queries to appropriate agents
- **Configuration Management**: Handles agent registration and lifecycle
- **Error Handling**: Graceful handling of agent failures

**Usage:**
```python
from core.agent_manager import AgentManager

manager = AgentManager()
result = manager.route_message('firefighting', 'Your question', 'session-id')
```

### Base Agent (`agents/base_agent.py`)

Abstract base class that all agents inherit from, providing common functionality.

**Common Features:**
- **AWS Bedrock Integration**: Built-in Bedrock Agent communication
- **Reference Extraction**: Automatic extraction of document references
- **S3 Image Handling**: Download and display of reference images
- **Error Handling**: Standardized error responses
- **Logging**: Interaction logging capabilities

**Implementation Pattern:**
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def process_message(self, message: str, session_id: str) -> Dict:
        # Custom processing logic
        result = self.invoke_bedrock_agent(message, session_id)
        return result
```

## Agent Configuration

### Configuration File (`config/agents.yaml`)

Agents are defined in YAML format for easy management:

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
```

### Configuration Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `display_name` | Human-readable agent name | Yes |
| `description` | Agent description | Yes |
| `module_path` | Python module path to agent | Yes |
| `bedrock_agent_id` | AWS Bedrock Agent ID | Yes |
| `bedrock_alias_id` | AWS Bedrock Agent Alias ID | Yes |
| `knowledge_base_id` | AWS Knowledge Base ID | Yes |
| `enabled` | Whether agent is active | No (default: true) |
| `ui_config` | UI customization settings | No |

## Current Agents

### Firefighting Agent (`agents/firefighting_agent/agent.py`)

Specialized agent for ship firefighting regulations and SOLAS standards.

**Capabilities:**
- SOLAS regulation interpretation
- Fire suppression system guidance
- Fire risk assessment
- Equipment selection support
- Compliance verification

**Knowledge Base:**
- SOLAS Chapter II-2 documents
- FSS Code regulations
- DNV-RU-SHIP rules
- Technical specifications

## Adding New Agents

### Step 1: Create Agent Structure

```bash
mkdir -p agents/new_agent
touch agents/new_agent/__init__.py
```

### Step 2: Implement Agent Class

Create `agents/new_agent/agent.py`:

```python
from agents.base_agent import BaseAgent
from typing import Dict

class Agent(BaseAgent):
    """New specialized agent"""
    
    def __init__(self, config):
        super().__init__(config)
        # Agent-specific initialization
    
    def process_message(self, message: str, session_id: str) -> Dict:
        """Process user message"""
        # Custom preprocessing
        enhanced_message = self._enhance_query(message)
        
        # Call Bedrock Agent
        result = self.invoke_bedrock_agent(enhanced_message, session_id)
        
        # Custom postprocessing
        return self._enhance_response(result)
    
    def _enhance_query(self, message: str) -> str:
        """Agent-specific query enhancement"""
        # Add domain-specific context
        return f"Domain context: {message}"
    
    def _enhance_response(self, result: Dict) -> Dict:
        """Agent-specific response enhancement"""
        # Add domain-specific formatting
        return result
    
    def get_capabilities(self) -> List[str]:
        """Return agent-specific capabilities"""
        return [
            "Domain-specific capability 1",
            "Domain-specific capability 2"
        ]
```

### Step 3: Update Configuration

Add to `config/agents.yaml`:

```yaml
agents:
  new_agent:
    display_name: "New Agent Name"
    description: "Agent description"
    module_path: "agents.new_agent.agent"
    bedrock_agent_id: "YOUR_BEDROCK_AGENT_ID"
    bedrock_alias_id: "YOUR_BEDROCK_ALIAS_ID"
    knowledge_base_id: "YOUR_KNOWLEDGE_BASE_ID"
    enabled: true
    ui_config:
      icon: "🔧"
      color: "#4ECDC4"
      topics:
        - "Topic 1"
        - "Topic 2"
```

### Step 4: Test Agent

```python
from core.agent_manager import AgentManager

manager = AgentManager()
result = manager.route_message('new_agent', 'Test question', 'test-session')
print(result)
```

## Best Practices

### Agent Development

1. **Inherit from BaseAgent**: Always extend the base class
2. **Implement process_message()**: Core method for message handling
3. **Use Configuration**: Leverage agent configuration for flexibility
4. **Handle Errors Gracefully**: Return structured error responses
5. **Add Logging**: Use built-in logging capabilities

### Configuration Management

1. **Use Descriptive Names**: Clear display names and descriptions
2. **Organize by Domain**: Group related agents logically
3. **Version Control**: Track configuration changes
4. **Environment Separation**: Different configs for dev/prod

### Testing

1. **Unit Tests**: Test individual agent methods
2. **Integration Tests**: Test with AgentManager
3. **End-to-End Tests**: Test through UI
4. **Performance Tests**: Monitor response times

## Troubleshooting

### Common Issues

1. **Agent Not Loading**:
   - Check module path in configuration
   - Verify agent class name is "Agent"
   - Check for syntax errors in agent code

2. **Bedrock Connection Errors**:
   - Verify AWS credentials
   - Check agent ID and alias ID
   - Ensure proper IAM permissions

3. **Configuration Errors**:
   - Validate YAML syntax
   - Check required parameters
   - Verify file paths

### Debug Mode

Enable debug logging in agent manager:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = AgentManager()
```

## Future Enhancements

### Planned Features

1. **Agent Collaboration**: Multi-agent workflows
2. **Dynamic Loading**: Runtime agent registration
3. **Performance Monitoring**: Agent performance metrics
4. **A/B Testing**: Agent version comparison
5. **Auto-scaling**: Dynamic agent instance management

### Extension Points

1. **Custom Tools**: Agent-specific tool integration
2. **Middleware**: Request/response processing pipeline
3. **Caching**: Agent response caching
4. **Analytics**: Usage and performance analytics