# 🚢 Ship Firefighting Rules Chatbot

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Neptune-orange.svg)](https://aws.amazon.com)

A sophisticated multi-agent GraphRAG-powered chatbot system for ship firefighting regulations with interactive knowledge graph visualization and real-time data exploration capabilities.

## 🌟 Key Features

- **🤖 Multi-Agent Architecture**: Plan-Execute agent with AWS Bedrock integration
- **🕸️ Interactive Knowledge Graphs**: Neptune Analytics GraphRAG + FSS SPARQL ontology
- **📊 Data Structure Guide**: Comprehensive system architecture visualization
- **💬 Intelligent Chat**: Korean/English support with document references
- **🔍 Advanced Search**: Bedrock-powered GraphRAG with Cohere reranking

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS Account with Bedrock access
- AWS CLI configured

### Installation

```bash
# 1. Clone and setup
git clone <repository-url>
cd shi-graphrag-chatbot
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your AWS resource IDs

# 4. Run application
streamlit run app.py
```

## 📁 Project Structure

```
shi-graphrag-chatbot/
├── 📱 Core Application
│   ├── app.py                      # Main Streamlit app
│   ├── data_structure_guide.py     # System architecture guide
│   ├── knowledge_graph.py          # Neptune Analytics viewer
│   └── fss_full_graph.py          # FSS SPARQL ontology
│
├── 🤖 Multi-Agent System
│   ├── core/agent_manager.py       # Agent management
│   ├── agents/
│   │   ├── base_agent.py           # Base agent class
│   │   └── plan_execute_agent/     # Main agent implementation
│   └── config/agents.yaml          # Agent configuration
│
├── 🎨 User Interface
│   └── ui/
│       ├── sidebar.py              # Navigation
│       ├── chat_interface.py       # Chat UI
│       ├── reference_display.py    # Document viewer
│       └── agent_selector.py       # Agent selection
│

├── 📚 Documentation
│   └── doc/                        # All documentation files
│
└── 🚀 Deployment
    └── deployment/                 # AWS deployment configs
```

## 🎯 Usage

### 💬 Chat Interface
1. Select "💬 채팅" from sidebar
2. Choose agent from dropdown
3. Ask questions in Korean or English
4. Click reference numbers to view source documents

### 🕸️ Knowledge Graphs
1. Select "🕸️ 지식 그래프" from sidebar
2. Choose between:
   - **GraphRAG**: Neptune Analytics (7,552 nodes)
   - **FSS Ontology**: SPARQL semantic graph (653 triples)

### 📊 Data Structure Guide
1. Select "📊 데이터 구조 안내서" from sidebar
2. Explore system architecture and statistics

## ⚙️ Configuration

### Environment Variables
```bash
# .env
AWS_REGION=us-west-2
BEDROCK_AGENT_ID=WT3ZJ25XCL
BEDROCK_ALIAS_ID=3RWZZLJDY1
KNOWLEDGE_BASE_ID=ZGBA1R5CS0
NEPTUNE_GRAPH_ID=g-goxs5d7fi3
NEPTUNE_ENDPOINT=your-neptune-endpoint
```

### Agent Configuration
```yaml
# config/agents.yaml
agents:
  plan_execute:
    display_name: "Plan Execute Agent"
    description: "Advanced reasoning agent with GraphRAG"
    bedrock_agent_id: "WT3ZJ25XCL"
    bedrock_alias_id: "3RWZZLJDY1"
    enabled: true
```

## 🔧 Development

### Adding New Agents
1. Create agent directory: `agents/new_agent/`
2. Implement `Agent` class extending `BaseAgent`
3. Update `config/agents.yaml`

### Core Components
The system uses direct AWS service integration:
- **Plan-Execute Agent**: AWS Bedrock Agent Runtime
- **GraphRAG Search**: Neptune Analytics Knowledge Base
- **Reranking**: Cohere Rerank via Bedrock Runtime
- **OCR Storage**: DynamoDB for text and image URLs

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### AWS Production
```bash
# Deploy with Application Load Balancer
aws cloudformation deploy \
    --template-file deployment/alb-streamlit.yaml \
    --stack-name streamlit-alb
```

## 📊 System Metrics

- **Knowledge Base**: 10,000+ document chunks
- **Neptune Analytics**: 7,552 nodes, 11,949 relationships  
- **SPARQL Ontology**: 653 triples, 42 classes
- **Response Time**: < 3 seconds average

## 📚 Documentation

Comprehensive documentation in `/doc` folder:

- **[System Overview](doc/SYSTEM_OVERVIEW.md)** - Architecture overview
- **[Configuration Guide](doc/CONFIGURATION_GUIDE.md)** - Setup instructions
- **[Agent Development](doc/AGENT_DEVELOPMENT.md)** - Agent development guide
- **[Troubleshooting](doc/troubleshooting.md)** - Problem resolution
- **[Multi-Agent System](doc/multi_agent_system.md)** - Architecture details

Korean versions available with `-ko` suffix.

## 🛠️ Testing & Debugging

Available test utilities:
- `test_simple.py` - Basic functionality tests
- `test_full_workflow.py` - End-to-end testing
- `debug_aws_resources.py` - AWS resource status check

## 🔒 Security

- **Read-only Operations**: Prevents data modification
- **IAM Roles**: Least privilege access
- **Input Validation**: Query safety checking
- **Audit Logging**: CloudTrail integration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Follow code standards and add tests
4. Update documentation
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: Create GitHub issues for bugs
- **Documentation**: Check `/doc` directory
- **Troubleshooting**: See [troubleshooting guide](doc/troubleshooting.md)

---

**Built with ❤️ for maritime safety professionals**