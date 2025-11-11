# 지식 그래프 문서

## 개요

선박 소방 규정 챗봇은 규정 문서와 그 관계를 대화형으로 탐색할 수 있는 두 가지 강력한 지식 그래프 시각화 시스템을 제공합니다. 이러한 그래프는 사용자가 시각적 표현을 통해 해양 안전 규정의 복잡한 구조를 이해하는 데 도움을 줍니다.

## 그래프 유형

### 1. GraphRAG (Neptune Analytics)

**목적**: Neptune Analytics 그래프 데이터베이스를 사용한 문서-엔티티 관계 시각화입니다.

**데이터 소스**: OpenCypher 쿼리 언어를 사용하는 Neptune Analytics

**그래프 구조**:
- **총 노드 수**: 7,552개
  - Document (11개): 원본 PDF 문서
  - Chunk (2,531개): 문서 조각
  - Entity (5,010개): 추출된 개념 및 용어
- **총 관계 수**: 11,949개
  - CONTAINS (9,418개): Chunk → Entity 관계
  - FROM (2,531개): Chunk → Document 관계

**시각화 기능**:
- **대화형 디스플레이**: 완전한 상호작용이 가능한 900px 높이
- **노드 제한**: 성능을 위해 최대 2,000개 노드와 3,000개 엣지 표시
- **색상 코딩**: 
  - 청록색 (#4ecdc4): Document 노드
  - 파란색 (#45b7d1): Entity 노드
  - 주황색 (#ff9f43): 기타 노드
- **물리 엔진**: 자연스러운 노드 배치를 위한 Barnes-Hut 알고리즘
- **사용자 상호작용**: 클릭, 드래그, 줌, 호버로 세부정보 확인

**구현**: `knowledge_graph.py`

#### 주요 함수

**get_neptune_graph_data()**
```python
def get_neptune_graph_data():
    """Neptune Analytics에서 그래프 데이터 가져오기"""
    # 노드와 엣지를 위한 OpenCypher 쿼리
    nodes_query = "MATCH (n) RETURN id(n) as id, labels(n) as labels, properties(n) as properties LIMIT 2000"
    edges_query = "MATCH (a)-[r]->(b) RETURN id(r) as id, type(r) as label, id(a) as source, id(b) as target LIMIT 3000"
```

**create_neptune_graph()**
```python
def create_neptune_graph():
    """대화형 Neptune Analytics 그래프 시각화 생성"""
    net = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white")
    # 색상 코딩 및 물리 엔진으로 노드와 엣지 추가
```

#### Neptune Analytics 구성
- **Graph ID**: `g-gqisj8edd6`
- **리전**: `us-west-2`
- **쿼리 언어**: OpenCypher
- **엔드포인트**: Neptune Analytics API

### 2. FSS 온톨로지 그래프 (Neptune SPARQL)

**목적**: SPARQL 쿼리를 사용한 화재 안전 시스템(FSS) 규정의 의미론적 온톨로지 시각화입니다.

**데이터 소스**: SPARQL 엔드포인트를 사용하는 Neptune DB

**그래프 구조**:
- **총 트리플 수**: 653개 RDF 트리플
- **클래스**: 42개 온톨로지 클래스
- **인스턴스**: 186개 구체적 인스턴스
- **FSS 챕터**: 17개 구조화된 챕터

**시각화 기능**:
- **방향성 그래프**: 화살표로 관계 방향 표시
- **의미론적 관계**: RDF 기반 온톨로지 구조
- **챕터 구성**: FSS Code 챕터 계층구조
- **대화형 디스플레이**: 완전한 상호작용이 가능한 900px 높이
- **색상 코딩**: 노드 유형 및 클래스 계층구조 기반

**구현**: `fss_full_graph.py`

#### 주요 함수

**get_full_ontology()**
```python
def get_full_ontology():
    """Neptune SPARQL에서 완전한 FSS 온톨로지 가져오기"""
    query = """
    PREFIX fss: <http://www.semanticweb.org/fss#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?s ?p ?o ?sType ?oType ?sLabel ?oLabel
    WHERE {
        ?s ?p ?o .
        OPTIONAL { ?s rdf:type ?sType }
        OPTIONAL { ?o rdf:type ?oType }
        OPTIONAL { ?s rdfs:label ?sLabel }
        OPTIONAL { ?o rdfs:label ?oLabel }
    }
    """
```

**create_full_graph()**
```python
def create_full_graph(data):
    """대화형 FSS 온톨로지 그래프 시각화 생성"""
    net = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white")
    # RDF 트리플 처리 및 의미론적 그래프 생성
```

#### Neptune SPARQL 구성
- **엔드포인트**: `shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com`
- **포트**: 8182
- **프로토콜**: SigV4 인증을 사용하는 HTTPS
- **쿼리 언어**: SPARQL 1.1

## 사용자 인터페이스 통합

### 사이드바 네비게이션

사용자는 사이드바를 통해 지식 그래프에 접근할 수 있습니다:

```python
# ui/sidebar.py에서
st.markdown("### 🕸️ 지식 그래프")
graph_type = st.radio(
    "그래프 선택",
    ["🕸️ 모든 문서의 GraphRAG", "FSS 문서 GraphDB"],
    key="graph_selector"
)
```

### 그래프 표시

그래프가 선택되면:
1. 채팅 인터페이스가 숨겨짐
2. 그래프 시각화가 메인 영역에 표시됨
3. 그래프 위에 설명 정보가 표시됨
4. 닫기 버튼으로 채팅 모드로 돌아갈 수 있음

```python
# app.py에서
if st.session_state.get('show_knowledge_graph', False):
    selected_graph_type = st.session_state.get('selected_graph_type')
    
    if selected_graph_type == "🕸️ 모든 문서의 GraphRAG":
        net = create_neptune_graph()
        html_string = net.generate_html()
        components.html(html_string, height=900)
    
    elif selected_graph_type == "FSS 문서 GraphDB":
        data = get_full_ontology()
        net, node_count, edge_count = create_full_graph(data)
        html_string = net.generate_html()
        components.html(html_string, height=900)
```

## 기술 구현

### PyVis 네트워크 라이브러리

두 그래프 모두 시각화를 위해 PyVis를 사용합니다:

```python
from pyvis.network import Network

net = Network(
    height="900px",
    width="100%",
    bgcolor="#1e1e1e",
    font_color="white"
)
```

### 물리 엔진 구성

**GraphRAG 물리 엔진**:
```python
net.set_options("""
var options = {
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -8000,
      "springConstant": 0.001,
      "springLength": 200
    },
    "stabilization": {"iterations": 150}
  }
}
""")
```

**FSS 온톨로지 물리 엔진**:
```python
net.set_options("""
var options = {
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -8000,
      "springConstant": 0.001,
      "springLength": 200
    },
    "stabilization": {"iterations": 150}
  },
  "edges": {
    "arrows": {"to": {"enabled": true}}
  }
}
""")
```

### AWS 인증

**Neptune Analytics**:
```python
neptune_client = boto3.client(
    'neptune-graph',
    region_name='us-west-2',
    config=Config(retries={"total_max_attempts": 1, "mode": "standard"})
)
```

**Neptune SPARQL**:
```python
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

session = boto3.Session()
credentials = session.get_credentials()
request = AWSRequest(method='POST', url=SPARQL_ENDPOINT, data=query)
SigV4Auth(credentials, 'neptune-db', REGION).add_auth(request)
```

## 성능 최적화

### 노드 제한

원활한 성능을 보장하기 위해:
- **GraphRAG**: 2,000개 노드와 3,000개 엣지로 제한
- **FSS 온톨로지**: 모든 653개 트리플 표시 (관리 가능한 크기)

### 캐싱

```python
@st.cache_resource
def get_neptune_client():
    return boto3.client('neptune-graph', region_name='us-west-2')
```

### 지연 로딩

그래프는 선택될 때만 로드되며, 초기 페이지 로드 시에는 로드되지 않습니다.

## 사용 사례

### GraphRAG 사용 사례

1. **문서 발견**: 엔티티 연결을 통해 관련 문서 찾기
2. **개념 탐색**: 문서 전반에 걸쳐 개념이 어떻게 관련되는지 이해
3. **콘텐츠 네비게이션**: 문서 구조의 시각적 탐색
4. **관계 분석**: 문서 관계의 패턴 식별

### FSS 온톨로지 사용 사례

1. **규정 구조**: FSS Code 구성 이해
2. **의미론적 관계**: 온톨로지 연결 탐색
3. **챕터 네비게이션**: FSS 챕터를 시각적으로 탐색
4. **규정 준수 매핑**: 요구사항을 규정 구조에 매핑

## 문제 해결

### 일반적인 문제

**Neptune Analytics 연결**:
```python
# 그래프 ID 및 리전 확인
neptune_client.execute_query(
    graphIdentifier='g-gqisj8edd6',
    queryString=query,
    language='OPEN_CYPHER'
)
```

**Neptune SPARQL 연결**:
```python
# 엔드포인트 및 인증 확인
NEPTUNE_ENDPOINT = "shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com"
SPARQL_ENDPOINT = f"https://{NEPTUNE_ENDPOINT}:8182/sparql"
```

**그래프가 표시되지 않음**:
- 브라우저 콘솔에서 JavaScript 오류 확인
- HTML 컴포넌트 렌더링 확인
- 충분한 브라우저 메모리 확인

**느린 성능**:
- 쿼리의 노드 제한 감소
- 물리 엔진 설정 최적화
- Neptune으로의 네트워크 지연 확인

## 향후 개선사항

### 계획된 기능

1. **검색 및 필터**: 이름 또는 속성으로 노드 검색
2. **서브그래프 추출**: 특정 서브그래프 추출 및 표시
3. **내보내기 기능**: 그래프 데이터 및 이미지 내보내기
4. **사용자 정의 레이아웃**: 사용자가 선택 가능한 레이아웃 알고리즘
5. **노드 세부정보 패널**: 노드 선택 시 상세 정보
6. **경로 찾기**: 노드 간 최단 경로 찾기
7. **커뮤니티 감지**: 노드 클러스터 및 커뮤니티 식별
8. **시간 기반 필터링**: 문서 날짜 또는 버전별 필터링

### 기술 개선사항

1. **점진적 로딩**: 대형 그래프를 점진적으로 로드
2. **WebGL 렌더링**: 더 나은 성능을 위해 WebGL 사용
3. **그래프 분석**: 내장 그래프 메트릭 및 통계
4. **사용자 정의 스타일링**: 사용자가 정의 가능한 색상 및 스타일
5. **모바일 최적화**: 모바일 장치용 터치 친화적 제어

## 모범 사례

### 사용자용

1. **개요부터 시작**: 줌 아웃을 사용하여 전체 구조 확인
2. **관심 영역에 집중**: 관심 있는 특정 영역으로 줌인
3. **호버 사용**: 노드 위에 마우스를 올려 세부정보 확인
4. **드래그하여 탐색**: 노드를 드래그하여 레이아웃 재구성
5. **완료 시 닫기**: 그래프를 닫아 채팅으로 돌아가기

### 개발자용

1. **쿼리 결과 제한**: 항상 노드 및 엣지 수 제한
2. **클라이언트 캐싱**: AWS 클라이언트에 Streamlit 캐싱 사용
3. **오류 처리**: 연결 실패를 우아하게 처리
4. **물리 엔진 최적화**: 시각적 매력과 성능의 균형
5. **성능 테스트**: 예상되는 최대 데이터 크기로 테스트

## 참고 자료

- **PyVis 문서**: https://pyvis.readthedocs.io/
- **Neptune Analytics**: https://docs.aws.amazon.com/neptune-analytics/
- **Neptune SPARQL**: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-api.html
- **OpenCypher**: https://opencypher.org/
- **SPARQL 1.1**: https://www.w3.org/TR/sparql11-query/
