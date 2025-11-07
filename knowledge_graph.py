import boto3
import streamlit as st
from pyvis.network import Network

@st.cache_resource
def get_neptune_client():
    from botocore.config import Config
    return boto3.client(
        'neptune-graph', 
        region_name='us-west-2',
        config=Config(retries={"total_max_attempts": 1, "mode": "standard"}, read_timeout=None)
    )

def get_neptune_graph_data():
    """Neptune Analytics에서 전체 그래프 데이터 가져오기"""
    try:
        neptune_client = get_neptune_client()
        
        # 노드 쿼리 (최대 2000개) - openCypher
        nodes_query = "MATCH (n) RETURN id(n) as id, labels(n) as labels, properties(n) as properties LIMIT 2000"
        nodes_response = neptune_client.execute_query(
            graphIdentifier='g-gqisj8edd6',
            queryString=nodes_query,
            language='OPEN_CYPHER'
        )
        
        # 엣지 쿼리 (최대 3000개) - openCypher
        edges_query = "MATCH (a)-[r]->(b) RETURN id(r) as id, type(r) as label, id(a) as source, id(b) as target LIMIT 3000"
        edges_response = neptune_client.execute_query(
            graphIdentifier='g-gqisj8edd6',
            queryString=edges_query,
            language='OPEN_CYPHER'
        )
        
        # Neptune Analytics API는 StreamingBody를 반환하므로 JSON으로 파싱 필요
        import json
        
        nodes_data = json.loads(nodes_response['payload'].read().decode('utf-8'))
        edges_data = json.loads(edges_response['payload'].read().decode('utf-8'))
        
        # 디버그 정보 출력
        st.info(f"노드 데이터: {len(nodes_data.get('results', []))}개, 엣지 데이터: {len(edges_data.get('results', []))}개")
        

        
        return nodes_data.get('results', []), edges_data.get('results', [])
    except Exception as e:
        st.error(f"Neptune 데이터 로드 실패: {e}")
        st.info("네튤단 엔드포인트를 확인하고 knowledge_graph.py에서 수정하세요.")
        return [], []

def create_neptune_graph():
    """Neptune Analytics 전체 그래프 시각화"""
    net = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white")
    
    nodes, edges = get_neptune_graph_data()
    
    if not nodes:
        net.add_node("empty", label="데이터 없음", color="#ff6b6b")
        return net
    
    # 노드 ID 수집
    node_ids = set()
    
    # 노드 추가
    for node in nodes:
        node_id = str(node.get('id', ''))
        if node_id:
            node_ids.add(node_id)
            labels = node.get('labels', ['Node'])
            properties = node.get('properties', {})
            
            # 엔티티 ID에서 실제 이름 추출
            if 'Entity' in labels and node_id.startswith('x-amz-bedrock-kb-'):
                # "x-amz-bedrock-kb-" 제거하고 실제 엔티티 이름 사용
                name = node_id.replace('x-amz-bedrock-kb-', '')
            else:
                # 기존 로직: 파일명, 텍스트 등에서 추출
                bedrock_text = properties.get('AMAZON_BEDROCK_TEXT', '')
                source_uri = properties.get('metadata_x-amz-bedrock-kb-source-uri', '')
                
                if source_uri:
                    filename = source_uri.split('/')[-1].replace('.PDF', '').replace('.pdf', '')
                    name = filename
                elif bedrock_text:
                    text_preview = bedrock_text[:50].strip()
                    if 'MATERIAL' in text_preview:
                        name = 'MATERIAL'
                    elif 'PIPE' in text_preview:
                        name = 'PIPE'
                    elif 'STEEL' in text_preview:
                        name = 'STEEL'
                    else:
                        name = text_preview.split()[0] if text_preview.split() else 'Chunk'
                else:
                    name = str(labels[0]) if labels else node_id[:8]
            
            color = "#4ecdc4" if 'Document' in str(node.get('labels', [])) else "#45b7d1" if 'Entity' in str(node.get('labels', [])) else "#ff9f43"
            
            net.add_node(node_id, 
                        label=str(name), 
                        color=color, 
                        size=15,
                        title=f"Labels: {node.get('labels', [])}\nProperties: {list(properties.keys())}\nID: {node_id}")
    
    # 엣지 추가 (존재하는 노드만)
    for edge in edges:
        source = str(edge.get('source', ''))
        target = str(edge.get('target', ''))
        edge_label = edge.get('label', 'relates')
        
        if source in node_ids and target in node_ids:
            net.add_edge(source, target, label=edge_label, color="#666")
    
    # 대용량 그래프 최적화 (2000 노드, 3000 엣지 대응)
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {"iterations": 100},
        "barnesHut": {
          "gravitationalConstant": -10000,
          "centralGravity": 0.2,
          "springLength": 120,
          "springConstant": 0.02,
          "damping": 0.12
        }
      },
      "nodes": {
        "font": {"size": 10},
        "widthConstraint": {"maximum": 150}
      },
      "edges": {
        "font": {"size": 8},
        "smooth": {"enabled": true, "type": "continuous"}
      },
      "interaction": {
        "hideEdgesOnDrag": true,
        "hideNodesOnDrag": true
      }
    }
    """)
    
    return net