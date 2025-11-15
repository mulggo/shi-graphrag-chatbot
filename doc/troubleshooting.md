# 🚨 Troubleshooting Guide

## 📋 Table of Contents
- [Common Issues](#common-issues)
- [AWS Related Issues](#aws-related-issues)
- [Agent Related Issues](#agent-related-issues)
- [Knowledge Graph Issues](#knowledge-graph-issues)
- [Performance Issues](#performance-issues)
- [Debugging Tools](#debugging-tools)

## 🔧 Common Issues

### 1. **Application Won't Start**

#### Symptoms
```bash
streamlit run app.py
# ModuleNotFoundError: No module named 'xxx'
```

#### Solutions
```bash
# 1. Check virtual environment activation
source venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Check Python path
python -c "import sys; print(sys.path)"
```

### 2. **Environment Variables Loading Failed**

#### Symptoms
- Configuration values showing as None
- AWS resource access failures

#### Solutions
```bash
# 1. Check .env file exists
ls -la .env

# 2. Check .env file contents
cat .env

# 3. Test environment variable loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AWS_REGION'))"
```

### 3. **Port Conflicts**

#### Symptoms
```bash
OSError: [Errno 48] Address already in use
```

#### Solutions
```bash
# 1. Check process using port
lsof -i :8501

# 2. Kill process
kill -9 <PID>

# 3. Use different port
streamlit run app.py --server.port 8502
```

## ☁️ AWS Related Issues

### 1. **AWS Credentials Issues**

#### Symptoms
```
NoCredentialsError: Unable to locate credentials
```

#### Solutions
```bash
# 1. Check AWS CLI configuration
aws configure list

# 2. Check credential status
aws sts get-caller-identity

# 3. Reconfigure credentials
aws configure
```

#### Permission Verification
```bash
# Check Bedrock permissions
aws bedrock list-foundation-models --region us-west-2

# Check Neptune permissions
aws neptune-graph list-graphs --region us-west-2

# Check S3 permissions
aws s3 ls s3://claude-neptune/
```

### 2. **Bedrock Agent Access Failed**

#### Symptoms
```
AccessDeniedException: User is not authorized to perform: bedrock-agent:InvokeAgent
```

#### Solutions
```bash
# 1. Check Agent status
aws bedrock-agent get-agent --agent-id WT3ZJ25XCL --region us-west-2

# 2. Check Agent Alias
aws bedrock-agent get-agent-alias --agent-id WT3ZJ25XCL --agent-alias-id 3RWZZLJDY1 --region us-west-2

# 3. Add required IAM policies
```

#### Required IAM Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agent:InvokeAgent",
                "bedrock-agent-runtime:InvokeAgent",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. **Knowledge Base Access Failed**

#### Symptoms
```
ValidationException: Knowledge base ZGBA1R5CS0 not found
```

#### Solutions
```bash
# 1. Check KB exists
aws bedrock-agent get-knowledge-base --knowledge-base-id ZGBA1R5CS0 --region us-west-2

# 2. Check KB status
aws bedrock-agent list-knowledge-bases --region us-west-2

# 3. Check KB sync status
aws bedrock-agent get-knowledge-base --knowledge-base-id ZGBA1R5CS0 --region us-west-2 | grep status
```

### 4. **Neptune Connection Failed**

#### Symptoms
```
EndpointConnectionError: Could not connect to the endpoint URL
```

#### Solutions
```bash
# 1. Check Neptune graph status
aws neptune-graph get-graph --graph-identifier g-goxs5d7fi3 --region us-west-2

# 2. Check network connectivity
curl -I https://neptune-graph.us-west-2.amazonaws.com

# 3. Check VPC configuration (if needed)
aws ec2 describe-vpcs --region us-west-2
```

## 🤖 Agent Related Issues

### 1. **Agent Loading Failed**

#### Symptoms
- Agents not showing in sidebar
- "No available agents" message

#### Solutions
```python
# 1. Check agent configuration
import yaml
with open('config/agents.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print(config)

# 2. Test agent class import
from agents.plan_execute_agent.agent import Agent
agent = Agent()
print("✅ Agent loaded successfully")

# 3. Test Agent Manager
from core.agent_manager import AgentManager
manager = AgentManager()
agents = manager.get_available_agents()
print(f"Loaded agents: {[a.name for a in agents]}")
```

### 2. **Message Processing Failed**

#### Symptoms
```
AttributeError: 'Agent' object has no attribute 'process_message'
```

#### Solutions
```python
# 1. Check base class inheritance
from agents.base_agent import BaseAgent

class Agent(BaseAgent):  # BaseAgent inheritance required
    def process_message(self, message: str, session_id: str, **kwargs):
        # Implementation required
        pass

# 2. Check method signature
# Correct signature: process_message(self, message: str, session_id: str, **kwargs) -> Dict[str, Any]
```

### 3. **Response Format Error**

#### Symptoms
- Response not displaying properly in UI
- Reference documents not appearing

#### Solutions
```python
# Correct response format
def process_message(self, message: str, session_id: str, **kwargs) -> Dict[str, Any]:
    return {
        "success": True,                    # Required: bool
        "content": "Response content",      # Required: str
        "references": [                     # Optional: List[Dict]
            {
                "source": "Document name",
                "content": "Reference content",
                "score": 0.95,
                "metadata": {}
            }
        ],
        "metadata": {                       # Optional: Dict
            "agent": "agent_name",
            "response_time": 1.23,
            "model_used": "claude-3-haiku"
        }
    }
```

## 🕸️ Knowledge Graph Issues

### 1. **Graph Not Loading**

#### Symptoms
- Only "No Data" node displayed
- Graph loading failure message

#### Solutions
```python
# 1. Test Neptune connection
import boto3
client = boto3.client('neptune-graph', region_name='us-west-2')

try:
    response = client.execute_query(
        graphIdentifier='g-goxs5d7fi3',
        queryString='MATCH (n) RETURN count(n) as count LIMIT 1',
        language='OPEN_CYPHER'
    )
    print("✅ Neptune connection successful")
except Exception as e:
    print(f"❌ Neptune connection failed: {e}")

# 2. Check query results
import json
data = json.loads(response['payload'].read().decode('utf-8'))
print(f"Node count: {data}")
```

### 2. **Slow Graph Rendering**

#### Symptoms
- Graph loading takes 10+ seconds
- Browser becomes unresponsive

#### Solutions
```python
# 1. Adjust node limit
nodes_query = "MATCH (n) RETURN ... LIMIT 1000"  # Reduce from 2000 to 1000

# 2. Adjust physics engine settings
net.set_options("""
var options = {
  "physics": {
    "enabled": true,
    "stabilization": {"iterations": 50}  # Reduce from 100 to 50
  }
}
""")
```

### 3. **FSS GraphDB Connection Failed**

#### Symptoms
```
❌ Unable to fetch FSS data.
```

#### Solutions
```bash
# 1. Check Neptune SPARQL endpoint
aws neptune describe-db-clusters --region us-west-2

# 2. Set environment variables
export NEPTUNE_ENDPOINT=your-cluster.cluster-xxx.us-west-2.neptune.amazonaws.com

# 3. Test SPARQL query
curl -X POST "https://${NEPTUNE_ENDPOINT}:8182/sparql" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
```

## ⚡ Performance Issues

### 1. **Slow Response Time (>5 seconds)**

#### Root Cause Analysis
```python
# Performance profiling
import time
import cProfile

def profile_agent():
    agent = PlanExecuteAgent()
    
    def test_message():
        return agent.process_message("Test message", "test_session")
    
    # Run profiling
    cProfile.run('test_message()', 'profile_output.prof')
    
    # Analyze results
    import pstats
    stats = pstats.Stats('profile_output.prof')
    stats.sort_stats('cumulative').print_stats(10)
```

#### Solutions
```python
# 1. Set timeouts
from botocore.config import Config

config = Config(
    read_timeout=10,
    connect_timeout=5,
    retries={'max_attempts': 2}
)

client = boto3.client('bedrock-agent-runtime', config=config)

# 2. Parallel processing
import asyncio
import concurrent.futures

async def parallel_search():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [
            executor.submit(search_kb1, query),
            executor.submit(search_kb2, query)
        ]
        results = [task.result() for task in tasks]
    return results
```

### 2. **Memory Usage Increase**

#### Symptoms
- Memory usage increases over time
- System becomes sluggish

#### Solutions
```python
# 1. Session state cleanup
def cleanup_session():
    # Remove old messages
    if len(st.session_state.messages) > 50:
        st.session_state.messages = st.session_state.messages[-20:]
    
    # Clear caches
    st.cache_data.clear()
    st.cache_resource.clear()

# 2. Memory monitoring
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")
```

## 🛠️ Debugging Tools

### 1. **Log Level Configuration**

```python
# Logging configuration
import logging

# Development environment
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Production environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### 2. **Streamlit Debug Mode**

```bash
# Run in debug mode
streamlit run app.py --logger.level debug

# Check Network tab in developer tools
# Check error messages in browser console
```

### 3. **AWS Resource Status Check Script**

```python
# debug_aws_resources.py
import boto3
import json

def check_all_resources():
    """Check all AWS resource status"""
    
    # Bedrock Agent
    try:
        client = boto3.client('bedrock-agent', region_name='us-west-2')
        agent = client.get_agent(agentId='WT3ZJ25XCL')
        print(f"✅ Bedrock Agent: {agent['agent']['agentStatus']}")
    except Exception as e:
        print(f"❌ Bedrock Agent: {e}")
    
    # Knowledge Base
    try:
        kb = client.get_knowledge_base(knowledgeBaseId='ZGBA1R5CS0')
        print(f"✅ Knowledge Base: {kb['knowledgeBase']['status']}")
    except Exception as e:
        print(f"❌ Knowledge Base: {e}")
    
    # Neptune Analytics
    try:
        neptune_client = boto3.client('neptune-graph', region_name='us-west-2')
        graph = neptune_client.get_graph(graphIdentifier='g-goxs5d7fi3')
        print(f"✅ Neptune Graph: {graph['status']}")
    except Exception as e:
        print(f"❌ Neptune Graph: {e}")

if __name__ == "__main__":
    check_all_resources()
```

### 4. **Agent Response Debugging**

```python
# debug_agent_response.py
from agents.plan_execute_agent.agent import PlanExecuteAgent
import json

def debug_agent_step_by_step():
    """Step-by-step agent debugging"""
    agent = PlanExecuteAgent()
    query = "What are the fire extinguisher requirements for ships?"
    
    print("=== Step 1: Document Plan Creation ===")
    plan = agent._create_document_plan(query)
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    
    print("\n=== Step 2: Neptune Search ===")
    if plan.get('success'):
        english_query = plan.get('english_query', query)
        search_results = agent._execute_neptune_search(english_query)
        print(f"Search results: {len(search_results)} items")
        
        print("\n=== Step 3: Cohere Reranking ===")
        if search_results:
            reranked = agent._cohere_rerank(english_query, search_results)
            print(f"Reranked results: {len(reranked)} items")
            
            if reranked:
                print(f"Top score: {reranked[0].get('rerank_score', 'N/A')}")

if __name__ == "__main__":
    debug_agent_step_by_step()
```

## 📊 Performance Monitoring

### System Metrics Check

```python
# monitor_system.py
import psutil
import time
from datetime import datetime

def monitor_performance():
    """System performance monitoring"""
    
    while True:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        print(f"[{datetime.now()}] CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent}%")
        
        # Check thresholds
        if cpu_percent > 80:
            print("⚠️ High CPU usage")
        if memory_percent > 80:
            print("⚠️ High memory usage")
        
        time.sleep(10)

if __name__ == "__main__":
    monitor_performance()
```

## 🆘 Emergency Recovery Procedures

### 1. **Complete System Restart**

```bash
# 1. Kill Streamlit processes
pkill -f streamlit

# 2. Reactivate virtual environment
source venv/bin/activate

# 3. Check dependencies
pip check

# 4. Restart application
streamlit run app.py
```

### 2. **Configuration Reset**

```bash
# 1. Backup environment variables
cp .env .env.backup

# 2. Restore to default configuration
cp .env.example .env

# 3. Set essential values only
echo "AWS_REGION=us-west-2" >> .env
echo "BEDROCK_AGENT_ID=WT3ZJ25XCL" >> .env
echo "BEDROCK_ALIAS_ID=3RWZZLJDY1" >> .env
```

### 3. **Git State Recovery**

```bash
# 1. Backup current state
git stash

# 2. Restore to last stable version
git log --oneline -5
git reset --hard <stable_version_hash>

# 3. Reapply changes (if needed)
git stash pop
```

## 📞 Support Requests

### Information to Include When Reporting Issues

1. **Environment Information**
   - OS and Python version
   - Installed package versions (`pip freeze`)
   - AWS region and resource IDs

2. **Error Logs**
   - Complete error stack trace
   - Streamlit logs (`streamlit.log`)
   - Browser console errors

3. **Reproduction Steps**
   - Actions performed before issue occurred
   - Input messages or configurations
   - Expected vs actual results

### Log Collection Script

```bash
# collect_logs.sh
#!/bin/bash

echo "=== System Information ===" > debug_info.txt
python --version >> debug_info.txt
pip freeze >> debug_info.txt

echo -e "\n=== Environment Variables ===" >> debug_info.txt
env | grep -E "(AWS|BEDROCK|NEPTUNE)" >> debug_info.txt

echo -e "\n=== Streamlit Logs ===" >> debug_info.txt
tail -100 streamlit.log >> debug_info.txt 2>/dev/null || echo "streamlit.log not found" >> debug_info.txt

echo -e "\n=== Agent Configuration ===" >> debug_info.txt
cat config/agents.yaml >> debug_info.txt

echo "Debug information saved to debug_info.txt"
```

## 📚 Related Documentation

- **[System Overview](../SYSTEM_OVERVIEW.md)**: Complete system architecture
- **[Configuration Guide](configuration.md)**: Configuration guide
- **[Agent Development](../AGENT_DEVELOPMENT.md)**: Agent development guide
- **[Multi-Agent System](multi_agent_system.md)**: Multi-agent system
- **[Testing Utilities](testing_utilities.md)**: Testing utilities

---

**Last Updated**: November 2024