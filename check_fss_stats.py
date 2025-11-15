#!/usr/bin/env python3
import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

NEPTUNE_ENDPOINT = "shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com"
SPARQL_ENDPOINT = f"https://{NEPTUNE_ENDPOINT}:8182/sparql"
REGION = "us-west-2"

def run_sparql_query(query):
    session = boto3.Session()
    credentials = session.get_credentials()
    headers = {'Content-Type': 'application/sparql-query', 'Accept': 'application/json'}
    request = AWSRequest(method='POST', url=SPARQL_ENDPOINT, data=query, headers=headers)
    SigV4Auth(credentials, 'neptune-db', REGION).add_auth(request)
    
    try:
        response = requests.post(SPARQL_ENDPOINT, data=query, headers=dict(request.headers))
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def explore_fss_ontology():
    print("🔍 FSS 온톨로지 전체 탐색 중...")
    
    # 1. 전체 데이터 구조 탐색
    explore_query = """
    SELECT ?s ?p ?o (COUNT(*) as ?count)
    WHERE {
        ?s ?p ?o .
    }
    GROUP BY ?s ?p ?o
    ORDER BY DESC(?count)
    LIMIT 50
    """
    
    print("\n📊 전체 데이터 구조 탐색...")
    result = run_sparql_query(explore_query)
    
    if result and result['results']['bindings']:
        print(f"   ✅ 상위 50개 트리플 패턴:")
        for i, binding in enumerate(result['results']['bindings'][:10]):
            s = binding['s']['value'].split('#')[-1] if '#' in binding['s']['value'] else binding['s']['value'].split('/')[-1]
            p = binding['p']['value'].split('#')[-1] if '#' in binding['p']['value'] else binding['p']['value'].split('/')[-1]
            o = binding['o']['value'].split('#')[-1] if '#' in binding['o']['value'] else binding['o']['value'][:50]
            count = binding['count']['value']
            print(f"   [{i+1:2d}] {s} --{p}--> {o} ({count}회)")
    
    # 2. 네임스페이스별 분석
    namespace_query = """
    SELECT ?namespace (COUNT(*) as ?count)
    WHERE {
        ?s ?p ?o .
        BIND(REPLACE(STR(?s), "#.*$", "#") as ?namespace)
    }
    GROUP BY ?namespace
    ORDER BY DESC(?count)
    """
    
    print("\n📊 네임스페이스별 분석...")
    result = run_sparql_query(namespace_query)
    
    if result and result['results']['bindings']:
        print(f"   ✅ 네임스페이스별 트리플 수:")
        for binding in result['results']['bindings']:
            ns = binding['namespace']['value']
            count = binding['count']['value']
            print(f"   - {ns}: {count}개")
    
    # 3. 술어(Property) 분석
    predicate_query = """
    SELECT ?predicate (COUNT(*) as ?count)
    WHERE {
        ?s ?predicate ?o .
    }
    GROUP BY ?predicate
    ORDER BY DESC(?count)
    """
    
    print("\n📊 술어(Property) 분석...")
    result = run_sparql_query(predicate_query)
    
    if result and result['results']['bindings']:
        print(f"   ✅ 상위 술어들:")
        for i, binding in enumerate(result['results']['bindings'][:15]):
            pred = binding['predicate']['value'].split('#')[-1] if '#' in binding['predicate']['value'] else binding['predicate']['value'].split('/')[-1]
            count = binding['count']['value']
            print(f"   [{i+1:2d}] {pred}: {count}회")
    
    # 4. rdf:type 분석
    type_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?type (COUNT(*) as ?count)
    WHERE {
        ?s rdf:type ?type .
    }
    GROUP BY ?type
    ORDER BY DESC(?count)
    """
    
    print("\n📊 rdf:type 분석...")
    result = run_sparql_query(type_query)
    
    if result and result['results']['bindings']:
        print(f"   ✅ 타입별 인스턴스 수:")
        for binding in result['results']['bindings']:
            type_name = binding['type']['value'].split('#')[-1] if '#' in binding['type']['value'] else binding['type']['value'].split('/')[-1]
            count = binding['count']['value']
            print(f"   - {type_name}: {count}개")
    
    # 5. 전체 통계
    stats_queries = {
        "총 트리플": "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o . }",
        "고유 주어": "SELECT (COUNT(DISTINCT ?s) as ?count) WHERE { ?s ?p ?o . }",
        "고유 술어": "SELECT (COUNT(DISTINCT ?p) as ?count) WHERE { ?s ?p ?o . }",
        "고유 목적어": "SELECT (COUNT(DISTINCT ?o) as ?count) WHERE { ?s ?p ?o . }"
    }
    
    print("\n📊 전체 통계...")
    for name, query in stats_queries.items():
        result = run_sparql_query(query)
        if result and result['results']['bindings']:
            count = result['results']['bindings'][0]['count']['value']
            print(f"   {name}: {count}개")

def check_fss_stats():
    print("🔍 FSS 온톨로지 통계 확인 중...")
    
    # 먼저 전체 탐색
    explore_fss_ontology()
    
    # 수정된 쿼리들
    # 1. 총 트리플 수
    triple_query = """
    SELECT (COUNT(*) as ?count)
    WHERE {
        ?s ?p ?o .
    }
    """
    
    # 2. 클래스 수 (더 포괄적)
    class_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT (COUNT(DISTINCT ?class) as ?count)
    WHERE {
        { ?class rdf:type rdfs:Class . }
        UNION
        { ?class rdf:type owl:Class . }
        UNION
        { ?instance rdf:type ?class . }
    }
    """
    
    # 3. 인스턴스 수 (더 포괄적)
    instance_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT (COUNT(DISTINCT ?instance) as ?count)
    WHERE {
        ?instance rdf:type ?class .
    }
    """
    
    # 4. 프로퍼티 수
    property_query = """
    SELECT (COUNT(DISTINCT ?property) as ?count)
    WHERE {
        ?s ?property ?o .
    }
    """
    
    # 5. FSS 챕터 수 (더 포괄적)
    chapter_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT (COUNT(DISTINCT ?chapter) as ?count)
    WHERE {
        ?chapter ?p ?o .
        FILTER(CONTAINS(LCASE(STR(?chapter)), "chapter"))
    }
    """
    
    queries = [
        ("총 트리플", triple_query),
        ("총 클래스", class_query),
        ("총 인스턴스", instance_query),
        ("총 프로퍼티", property_query),
        ("FSS 챕터", chapter_query)
    ]
    
    results = {}
    
    print("\n" + "="*50)
    print("📊 FSS 온톨로지 정확한 통계")
    print("="*50)
    
    for name, query in queries:
        print(f"\n📊 {name} 확인 중...")
        result = run_sparql_query(query)
        
        if result and result['results']['bindings']:
            count = result['results']['bindings'][0]['count']['value']
            results[name] = int(count)
            print(f"   ✅ {name}: {count}개")
        else:
            print(f"   ❌ {name}: 쿼리 실패")
            results[name] = "실패"
    
    print("\n" + "="*50)
    print("📊 FSS 온톨로지 최종 통계")
    print("="*50)
    for name, count in results.items():
        print(f"{name:15}: {count}")
    
    return results

if __name__ == "__main__":
    check_fss_stats()