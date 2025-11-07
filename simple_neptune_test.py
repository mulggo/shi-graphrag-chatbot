#!/usr/bin/env python3
import boto3
import json

def test_neptune():
    print("Neptune Analytics 간단 테스트 시작...")
    
    neptune_client = boto3.client('neptune-graph', region_name='us-west-2')
    graph_id = 'g-gqisj8edd6'
    
    try:
        # 그래프 정보 조회
        graph_info = neptune_client.get_graph(graphIdentifier=graph_id)
        print(f"그래프 이름: {graph_info['name']}")
        print(f"그래프 상태: {graph_info['status']}")
        
        # 간단한 테스트 쿼리
        test_query = "RETURN 1 as test"
        print(f"\n테스트 쿼리 실행: {test_query}")
        
        response = neptune_client.execute_query(
            graphIdentifier=graph_id,
            queryString=test_query,
            language='OPEN_CYPHER'
        )
        
        print("응답 타입:", type(response))
        print("응답 키들:", response.keys())
        
        # payload 처리
        payload = response['payload']
        print("Payload 타입:", type(payload))
        
        # 데이터 읽기
        data = payload.read()
        print("읽은 데이터 타입:", type(data))
        print("읽은 데이터 길이:", len(data))
        
        if isinstance(data, bytes):
            decoded_data = data.decode('utf-8')
        else:
            decoded_data = str(data)
            
        print("디코딩된 데이터:", repr(decoded_data))
        
        # JSON 파싱 시도
        if decoded_data.strip():
            try:
                json_data = json.loads(decoded_data)
                print("JSON 파싱 성공:", json_data)
            except json.JSONDecodeError as e:
                print("JSON 파싱 실패:", e)
                # 줄별로 파싱 시도
                for i, line in enumerate(decoded_data.strip().split('\n')):
                    if line.strip():
                        try:
                            line_json = json.loads(line)
                            print(f"라인 {i} JSON:", line_json)
                        except json.JSONDecodeError:
                            print(f"라인 {i} 파싱 실패:", repr(line))
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_neptune()