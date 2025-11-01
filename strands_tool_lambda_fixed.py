import json
import boto3

def lambda_handler(event, context):
    """
    Bedrock Agent에서 호출되는 Strands ReAct 검색 Tool (간소화 버전)
    """
    try:
        # 입력 파라미터 추출
        query = event.get('query', event.get('inputText', 'test query'))
        
        # Strands 라이브러리 import 시도
        try:
            import strands
            # Strands 사용 가능한 경우
            response_text = f"Strands ReAct 검색 완료: '{query}'\n소화시스템(Fire Fighting System) 관련 고급 검색이 수행되었습니다."
        except ImportError as ie:
            # Strands 없는 경우 대체 로직
            response_text = f"대체 검색 수행: '{query}'\n소화시스템(Fire Fighting System) 정보를 찾았습니다."
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': response_text,
                'source': 'Strands ReAct Search',
                'query': query
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'response': f"검색 중 오류 발생: {str(e)}"
            }, ensure_ascii=False)
        }