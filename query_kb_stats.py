#!/usr/bin/env python3
"""
KB와 Neptune DB의 실제 통계를 조회하는 스크립트
"""
import boto3
import json
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

def process_neptune_response(response):
    """Neptune 응답 처리 헬퍼 함수"""
    try:
        # payload를 직접 읽어서 디코드
        payload_data = response['payload'].read().decode('utf-8')
        
        # 전체 JSON으로 파싱
        json_response = json.loads(payload_data)
        
        # results 배열 반환
        return json_response.get('results', [])
        
    except Exception as e:
        print(f"응답 처리 오류: {e}")
        return []

def get_kb_stats():
    """Knowledge Base 통계 조회"""
    print("=== Knowledge Base 통계 조회 ===")
    
    # Bedrock Agent 클라이언트
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    
    kb_id = 'ZGBA1R5CS0'
    
    try:
        # KB 기본 정보
        kb_info = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        print(f"KB 이름: {kb_info['knowledgeBase']['name']}")
        print(f"KB 설명: {kb_info['knowledgeBase'].get('description', 'N/A')}")
        
        embedding_arn = kb_info['knowledgeBase']['knowledgeBaseConfiguration']['vectorKnowledgeBaseConfiguration']['embeddingModelArn']
        model_name = embedding_arn.split('/')[-1] if '/' in embedding_arn else embedding_arn
        print(f"임베딩 모델: {model_name}")
        
        # Data Sources 조회
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        print(f"데이터 소스 수: {len(data_sources['dataSourceSummaries'])}")
        
        for ds in data_sources['dataSourceSummaries']:
            print(f"- {ds['name']}: {ds['status']}")
            
        # 샘플 검색으로 대략적인 문서 수 추정
        sample_queries = ["SOLAS", "FSS", "소화", "화재", "규정"]
        total_results = 0
        unique_sources = set()
        
        for query in sample_queries:
            try:
                response = bedrock_runtime.retrieve(
                    knowledgeBaseId=kb_id,
                    retrievalQuery={'text': query},
                    retrievalConfiguration={
                        'vectorSearchConfiguration': {
                            'numberOfResults': 50
                        }
                    }
                )
                results = response.get('retrievalResults', [])
                print(f"'{query}' 검색 결과: {len(results)}개")
                total_results += len(results)
                
                # 고유 소스 파일 수집
                for result in results:
                    metadata = result.get('metadata', {})
                    source_uri = metadata.get('x-amz-bedrock-kb-source-uri', '')
                    if source_uri:
                        unique_sources.add(source_uri.split('/')[-1])
                        
            except Exception as e:
                print(f"'{query}' 검색 오류: {e}")
        
        print(f"평균 검색 결과: {total_results / len(sample_queries):.1f}개")
        print(f"발견된 고유 문서: {len(unique_sources)}개")
        
        # 추정 총 청크 수 (더 정확한 추정)
        estimated_chunks = total_results * 2  # 중복 제거 후 추정
        print(f"추정 총 청크 수: 약 {estimated_chunks:,}개")
        
    except Exception as e:
        print(f"KB 조회 오류: {e}")

def get_neptune_stats():
    """Neptune Analytics 통계 조회"""
    print("\n=== Neptune Analytics 통계 조회 ===")
    
    neptune_client = boto3.client('neptune-graph', region_name='us-west-2')
    graph_id = 'g-gqisj8edd6'
    
    try:
        # 그래프 정보 조회
        graph_info = neptune_client.get_graph(graphIdentifier=graph_id)
        print(f"그래프 이름: {graph_info['name']}")
        print(f"그래프 상태: {graph_info['status']}")
        
        # 노드 수 조회 쿼리
        node_count_query = "MATCH (n) RETURN count(n) as node_count"
        
        response = neptune_client.execute_query(
            graphIdentifier=graph_id,
            queryString=node_count_query,
            language='OPEN_CYPHER'
        )
        
        result_data = process_neptune_response(response)
        
        if result_data:
            node_count = result_data[0].get('node_count', 0)
            print(f"총 노드 수: {node_count:,}개")
        
        # 관계 수 조회
        edge_count_query = "MATCH ()-[r]->() RETURN count(r) as edge_count"
        
        response = neptune_client.execute_query(
            graphIdentifier=graph_id,
            queryString=edge_count_query,
            language='OPEN_CYPHER'
        )
        
        result_data = process_neptune_response(response)
        
        if result_data:
            edge_count = result_data[0].get('edge_count', 0)
            print(f"총 관계 수: {edge_count:,}개")
        
        # 노드 타입별 분포
        label_query = "MATCH (n) RETURN labels(n) as labels, count(n) as count ORDER BY count DESC LIMIT 10"
        
        response = neptune_client.execute_query(
            graphIdentifier=graph_id,
            queryString=label_query,
            language='OPEN_CYPHER'
        )
        
        result_data = process_neptune_response(response)
        
        print("노드 타입별 분포:")
        for item in result_data:
            labels = item.get('labels', [])
            count = item.get('count', 0)
            print(f"- {labels}: {count:,}개")
            
        # 관계 타입별 분포
        rel_query = "MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count ORDER BY count DESC LIMIT 10"
        
        response = neptune_client.execute_query(
            graphIdentifier=graph_id,
            queryString=rel_query,
            language='OPEN_CYPHER'
        )
        
        result_data = process_neptune_response(response)
        
        print("관계 타입별 분포:")
        for item in result_data:
            rel_type = item.get('rel_type', '')
            count = item.get('count', 0)
            print(f"- {rel_type}: {count:,}개")
            
    except Exception as e:
        print(f"Neptune 조회 오류: {e}")

def get_sparql_stats():
    """SPARQL 온톨로지 통계 조회"""
    print("\n=== SPARQL 온톨로지 통계 조회 ===")
    
    try:
        # Neptune SPARQL 엔드포인트
        neptune_endpoint = "shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com"
        sparql_endpoint = f"https://{neptune_endpoint}:8182/sparql"
        
        # AWS 인증 설정
        session = boto3.Session()
        credentials = session.get_credentials()
        region = 'us-west-2'
        
        # 총 트리플 수 조회
        count_query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/sparql-results+json'
        }
        
        data = f"query={requests.utils.quote(count_query)}"
        
        request = AWSRequest(
            method='POST',
            url=sparql_endpoint,
            data=data,
            headers=headers
        )
        
        SigV4Auth(credentials, 'neptune-db', region).add_auth(request)
        prepared_request = request.prepare()
        
        response = requests.post(
            prepared_request.url,
            data=prepared_request.body,
            headers=prepared_request.headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            bindings = result.get('results', {}).get('bindings', [])
            if bindings:
                total_triples = bindings[0]['count']['value']
                print(f"총 트리플 수: {total_triples}개")
        else:
            print(f"SPARQL 쿼리 실패: {response.status_code}")
        
        # 클래스 수 조회
        class_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT (COUNT(DISTINCT ?class) as ?count) 
        WHERE { 
            ?instance rdf:type ?class .
            FILTER(STRSTARTS(STR(?class), "http://www.semanticweb.org/fss#"))
        }
        """
        
        data = f"query={requests.utils.quote(class_query)}"
        request = AWSRequest(method='POST', url=sparql_endpoint, data=data, headers=headers)
        SigV4Auth(credentials, 'neptune-db', region).add_auth(request)
        prepared_request = request.prepare()
        
        response = requests.post(
            prepared_request.url,
            data=prepared_request.body,
            headers=prepared_request.headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            bindings = result.get('results', {}).get('bindings', [])
            if bindings:
                class_count = bindings[0]['count']['value']
                print(f"FSS 클래스 수: {class_count}개")
        
        # 인스턴스 수 조회
        instance_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(?instance) as ?count)
        WHERE { 
            ?instance rdf:type ?class .
            FILTER(STRSTARTS(STR(?class), "http://www.semanticweb.org/fss#"))
        }
        """
        
        data = f"query={requests.utils.quote(instance_query)}"
        request = AWSRequest(method='POST', url=sparql_endpoint, data=data, headers=headers)
        SigV4Auth(credentials, 'neptune-db', region).add_auth(request)
        prepared_request = request.prepare()
        
        response = requests.post(
            prepared_request.url,
            data=prepared_request.body,
            headers=prepared_request.headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            bindings = result.get('results', {}).get('bindings', [])
            if bindings:
                instance_count = bindings[0]['count']['value']
                print(f"FSS 인스턴스 수: {instance_count}개")
                
    except Exception as e:
        print(f"SPARQL 조회 오류: {e}")

if __name__ == "__main__":
    get_kb_stats()
    get_neptune_stats()
    get_sparql_stats()