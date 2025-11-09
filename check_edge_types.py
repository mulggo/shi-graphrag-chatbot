#!/usr/bin/env python3
"""Neptune Analytics에서 실제 엣지 타입 확인"""
import boto3
import json

def process_neptune_response(response):
    """Neptune 응답 처리"""
    try:
        payload_data = response['payload'].read().decode('utf-8')
        json_response = json.loads(payload_data)
        return json_response.get('results', [])
    except Exception as e:
        print(f"응답 처리 오류: {e}")
        return []

def check_edge_types():
    """실제 엣지 타입 조회"""
    neptune_client = boto3.client('neptune-graph', region_name='us-west-2')
    graph_id = 'g-gqisj8edd6'
    
    # 엣지 타입별 개수 조회
    query = """
    MATCH ()-[r]->() 
    RETURN type(r) as edge_type, count(r) as count 
    ORDER BY count DESC
    """
    
    try:
        response = neptune_client.execute_query(
            graphIdentifier=graph_id,
            queryString=query,
            language='OPEN_CYPHER'
        )
        
        results = process_neptune_response(response)
        
        print("=== 실제 엣지 타입 ===")
        print(f"총 {len(results)}개 타입\n")
        
        for item in results:
            edge_type = item.get('edge_type', '')
            count = item.get('count', 0)
            print(f"{edge_type}: {count:,}개")
            
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_edge_types()
