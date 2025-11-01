import json
import boto3
from strands import Agent, KnowledgeBaseTool

def lambda_handler(event, context):
    """
    Bedrock Agent에서 호출되는 Strands ReAct 검색 Tool
    """
    try:
        # 입력 파라미터 추출
        input_text = event.get('inputText', '')
        session_id = event.get('sessionId', 'default')
        
        # Strands Agent 초기화 (ReAct 패턴)
        kb_tool = KnowledgeBaseTool(
            knowledge_base_id='ZGBA1R5CS0',
            region='us-west-2'
        )
        
        strands_agent = Agent(
            name="ReAct Search Agent",
            instructions="""
            You are a ReAct-based search agent for shipbuilding engineering documents.
            
            When searching for information:
            1. THINK about what information is needed
            2. ACT by searching the knowledge base with relevant keywords
            3. OBSERVE the results and evaluate if they answer the question
            4. If not satisfied, try different keywords or search strategies
            5. Continue until you find relevant information or exhaust options
            
            Always respond in Korean (한국어).
            """,
            tools=[kb_tool],
            model="anthropic.claude-3-5-sonnet-20240620-v1:0"
        )
        
        # ReAct 검색 수행
        result = strands_agent.run(input_text)
        
        return {
            'statusCode': 200,
            'body': {
                'result': result.content,
                'session_id': session_id,
                'search_method': 'strands_react'
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'result': f"검색 중 오류가 발생했습니다: {str(e)}"
            }
        }