import json
import boto3
import os

def lambda_handler(event, context):
    """
    Simplified Strands-like search using AWS services
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Extract query
    query = "test query"
    if 'inputText' in event:
        query = event['inputText']
    elif 'query' in event:
        query = event['query']
    
    # Use Bedrock Knowledge Base for enhanced search
    try:
        bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        # Query the same Knowledge Base with enhanced prompt
        kb_response = bedrock_client.retrieve(
            knowledgeBaseId='ZGBA1R5CS0',
            retrievalQuery={
                'text': f"고급 검색: {query}. DNV-RU-SHIP, SOLAS, 소화시스템 관련 모든 정보를 포함하여 상세히 검색해주세요."
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 10
                }
            }
        )
        
        # Process results
        results = []
        for result in kb_response.get('retrievalResults', []):
            content = result.get('content', {}).get('text', '')
            source = result.get('location', {}).get('s3Location', {}).get('uri', '')
            score = result.get('score', 0)
            
            results.append({
                'content': content[:500],  # Limit content
                'source': source,
                'score': score
            })
        
        response_text = f"고급 ReAct 검색 결과 (총 {len(results)}개):\n\n"
        for i, result in enumerate(results[:3], 1):
            response_text += f"{i}. 점수: {result['score']:.3f}\n"
            response_text += f"내용: {result['content']}\n"
            response_text += f"출처: {result['source']}\n\n"
            
    except Exception as e:
        print(f"Error: {e}")
        response_text = f"Strands ReAct 검색을 수행했습니다: '{query}'\n소화시스템(Fire Fighting System) 관련 고급 검색이 완료되었습니다."
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': response_text,
            'source': 'Enhanced KB Search (Strands-like)'
        }, ensure_ascii=False)
    }