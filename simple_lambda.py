import json

def lambda_handler(event, context):
    """
    Simple test Lambda function for Bedrock Agent Action Group
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Extract query from event
    query = "test query"
    if 'inputText' in event:
        query = event['inputText']
    elif 'query' in event:
        query = event['query']
    
    # Simple response
    response = {
        "response": f"한국어로 답변합니다: '{query}'에 대한 검색을 수행했습니다. 소화시스템(Fire Fighting System) 관련 정보를 찾았습니다.",
        "source": "Strands ReAct Search (Test)"
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response, ensure_ascii=False)
    }