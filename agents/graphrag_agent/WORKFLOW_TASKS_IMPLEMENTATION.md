# WORKFLOW_TASKS Implementation Summary

## Task 7: 워크플로우 작업 정의

**Status**: ✅ Completed

## Implementation Details

### Location
- **File**: `agents/graphrag_agent/workflow_agents.py`
- **Lines**: 33-56

### WORKFLOW_TASKS Definition

Implemented a list of 3 workflow tasks that define the GraphRAG multi-agent workflow:

```python
WORKFLOW_TASKS = [
    {
        "task_id": "query_analysis",
        "description": "사용자 질문을 분석하고 검색 전략을 생성합니다",
        "system_prompt": get_prompt_by_agent_type("query_analysis"),
        "dependencies": [],
        "priority": 5,
        "tools": ["classify_query", "extract_entities"]
    },
    {
        "task_id": "kb_retrieval",
        "description": "Knowledge Base에서 관련 문서를 검색하고 reranking을 수행합니다",
        "system_prompt": get_prompt_by_agent_type("kb_retrieval"),
        "dependencies": ["query_analysis"],
        "priority": 3,
        "tools": ["kb_retrieve"]
    },
    {
        "task_id": "response_synthesis",
        "description": "검색 결과를 한국어 답변으로 합성합니다",
        "system_prompt": get_prompt_by_agent_type("response_synthesis"),
        "dependencies": ["kb_retrieval"],
        "priority": 2,
        "tools": []
    }
]
```

## Task Structure

Each task in WORKFLOW_TASKS contains:

1. **task_id**: Unique identifier for the task
2. **description**: Korean description of what the task does
3. **system_prompt**: Loaded from YAML files via `get_prompt_by_agent_type()`
4. **dependencies**: List of task_ids that must complete before this task
5. **priority**: Integer priority (higher = more important)
6. **tools**: List of tool names available to this task

## Workflow Architecture

### Task 1: Query Analysis
- **ID**: `query_analysis`
- **Dependencies**: None (entry point)
- **Priority**: 5 (highest)
- **Tools**: `classify_query`, `extract_entities`
- **Purpose**: Analyzes user questions and generates search strategies

### Task 2: KB Retrieval
- **ID**: `kb_retrieval`
- **Dependencies**: `query_analysis`
- **Priority**: 3 (medium)
- **Tools**: `kb_retrieve`
- **Purpose**: Executes Knowledge Base searches with reranking

### Task 3: Response Synthesis
- **ID**: `response_synthesis`
- **Dependencies**: `kb_retrieval`
- **Priority**: 2 (lower)
- **Tools**: None (uses Bedrock directly)
- **Purpose**: Synthesizes search results into Korean responses

## Dependency Chain

```
query_analysis (priority 5)
    ↓
kb_retrieval (priority 3)
    ↓
response_synthesis (priority 2)
```

This sequential dependency ensures:
1. Questions are analyzed before searching
2. Searches complete before synthesis
3. Proper data flow through the workflow

## Requirements Satisfied

✅ **Requirement 1.2**: Multi-agent workflow architecture
- Three specialized agents defined
- Clear task dependencies
- Priority-based execution order
- Tool mapping for each task

## Integration Points

### With Prompts System
- Uses `get_prompt_by_agent_type()` from `prompts.py`
- Loads prompts from YAML files in `prompts/` directory
- Ensures Anthropic 9 principles compliance

### With Tools System
- References tool names: `classify_query`, `extract_entities`, `kb_retrieve`
- Tools are imported from `tools.py`
- Tools are Lambda function wrappers

### With Main Agent
- WORKFLOW_TASKS will be used by `agent.py` to create Strands workflows
- Provides structure for workflow orchestration
- Enables parallel execution where dependencies allow

## Verification

Created `test_workflow_tasks.py` to verify:
- ✅ 3 tasks defined
- ✅ All required fields present
- ✅ Correct data types
- ✅ Dependencies properly configured
- ✅ Priorities correctly set
- ✅ Tools correctly mapped
- ✅ System prompts loaded successfully

## Next Steps

The WORKFLOW_TASKS definition is now ready for use in:
- **Task 6**: Main GraphRAG Agent implementation (already completed)
- **Task 8**: Logging and monitoring
- **Task 10**: Integration and testing

The main agent (`agent.py`) will use WORKFLOW_TASKS to:
1. Create Strands workflow instances
2. Define task execution order
3. Manage dependencies
4. Monitor workflow progress

## Notes

- System prompts are loaded dynamically from YAML files
- This allows updating prompts without code changes
- Tool names match the function names in `tools.py`
- Priority values follow convention: higher number = higher priority
- Dependencies are validated at runtime by Strands framework
