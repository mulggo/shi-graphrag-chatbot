#!/usr/bin/env python3
import streamlit as st
import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os

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
        st.error(f"Error: {e}")
        return None

def get_full_ontology():
    """전체 FSS 온톨로지 데이터 가져오기"""
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
        FILTER(STRSTARTS(STR(?s), "http://www.semanticweb.org/fss#") || 
               STRSTARTS(STR(?p), "http://www.semanticweb.org/fss#"))
    }
    """
    return run_sparql_query(query)

def create_full_graph(data):
    """전체 온톨로지 그래프 생성"""
    net = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white")
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "barnesHut": {"gravitationalConstant": -8000, "springConstant": 0.001, "springLength": 200},
        "stabilization": {"iterations": 150}
      },
      "nodes": {"font": {"size": 12}},
      "edges": {"font": {"size": 10}, "arrows": {"to": {"enabled": true}}}
    }
    """)
    
    nodes = {}
    edges = set()
    
    for binding in data['results']['bindings']:
        s = binding['s']['value']
        p = binding['p']['value']
        o = binding['o']['value']
        
        # Subject 노드
        s_id = s.split('#')[-1] if '#' in s else s.split('/')[-1]
        s_label = binding.get('sLabel', {}).get('value', s_id)
        s_type = binding.get('sType', {}).get('value', '').split('#')[-1]
        
        if s_id not in nodes:
            nodes[s_id] = {
                'label': s_label,
                'type': s_type,
                'color': get_node_color(s_type),
                'size': get_node_size(s_type)
            }
        
        # Object가 URI인 경우
        if o.startswith('http'):
            o_id = o.split('#')[-1] if '#' in o else o.split('/')[-1]
            o_label = binding.get('oLabel', {}).get('value', o_id)
            o_type = binding.get('oType', {}).get('value', '').split('#')[-1]
            
            if o_id not in nodes:
                nodes[o_id] = {
                    'label': o_label,
                    'type': o_type,
                    'color': get_node_color(o_type),
                    'size': get_node_size(o_type)
                }
            
            # Edge 추가
            p_label = p.split('#')[-1] if '#' in p else p.split('/')[-1]
            edge_key = (s_id, o_id, p_label)
            if edge_key not in edges:
                edges.add(edge_key)
    
    # 노드 추가
    for node_id, node_data in nodes.items():
        net.add_node(
            node_id,
            label=node_data['label'],
            title=f"Type: {node_data['type']}",
            color=node_data['color'],
            size=node_data['size']
        )
    
    # 엣지 추가
    for s_id, o_id, p_label in edges:
        net.add_edge(s_id, o_id, label=p_label, title=p_label)
    
    return net, len(nodes), len(edges)

def get_node_color(node_type):
    """노드 타입별 색상"""
    colors = {
        'Chapter': '#ff4757',
        'ExtinguishingSystem': '#2ed573',
        'DetectionSystem': '#3742fa',
        'Component': '#70a1ff',
        'Specification': '#5352ed',
        'Performance': '#ff6348',
        'Requirement': '#ff9ff3',
        'Capacity': '#7bed9f',
        'Temperature': '#ff6b81',
        'Dimension': '#2f3542',
        'Pressure': '#ff3838',
        'Duration': '#ff9f43',
        'Weight': '#70a1ff',
        'Material': '#5f27cd',
        'Equipment': '#00d2d3',
        'SafetyDevice': '#ff6b6b',
        'Reference': '#a4b0be',
        'Document': '#57606f',
        'Organization': '#2f3640'
    }
    return colors.get(node_type, '#ddd')

def get_node_size(node_type):
    """노드 타입별 크기"""
    sizes = {
        'Chapter': 30,
        'ExtinguishingSystem': 25,
        'DetectionSystem': 25,
        'Component': 20,
        'Specification': 15,
        'Performance': 15,
        'Requirement': 15
    }
    return sizes.get(node_type, 10)

def main():
    st.set_page_config(page_title="FSS Full Knowledge Graph", layout="wide")
    
    st.title("🔥 FSS Complete Knowledge Graph")
    st.markdown("**Neptune Database의 전체 FSS 온톨로지 시각화**")
    
    # 통계
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 트리플", "653")
    with col2:
        st.metric("총 클래스", "42")
    with col3:
        st.metric("총 인스턴스", "186")
    with col4:
        st.metric("FSS 챕터", "17")
    
    if st.button("🚀 전체 그래프 로드", type="primary"):
        with st.spinner("Neptune에서 전체 온톨로지를 가져오는 중..."):
            data = get_full_ontology()
        
        if data and data['results']['bindings']:
            st.success(f"✅ {len(data['results']['bindings'])}개 트리플 로드 완료")
            
            with st.spinner("지식그래프 생성 중..."):
                net, node_count, edge_count = create_full_graph(data)
                
                st.info(f"📊 노드: {node_count}개, 엣지: {edge_count}개")
                
                # 그래프 표시
                with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                    net.save_graph(tmp.name)
                    with open(tmp.name, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    components.html(html_content, height=850)
                    os.unlink(tmp.name)
        else:
            st.error("❌ 데이터를 가져올 수 없습니다.")
    
    # 범례
    st.markdown("### 🎨 노드 타입별 색상")
    legend_data = [
        ("Chapter", "#ff4757"), ("ExtinguishingSystem", "#2ed573"),
        ("DetectionSystem", "#3742fa"), ("Component", "#70a1ff"),
        ("Specification", "#5352ed"), ("Performance", "#ff6348"),
        ("Requirement", "#ff9ff3"), ("Equipment", "#00d2d3")
    ]
    
    cols = st.columns(4)
    for i, (label, color) in enumerate(legend_data):
        with cols[i % 4]:
            st.markdown(f'<span style="color: {color}; font-size: 20px;">●</span> {label}', 
                       unsafe_allow_html=True)

if __name__ == "__main__":
    main()