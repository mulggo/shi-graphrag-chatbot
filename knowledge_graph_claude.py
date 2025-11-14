import boto3
import streamlit as st
from pyvis.network import Network

def get_neptune_client():
    from botocore.config import Config
    return boto3.client(
        'neptune-graph', 
        region_name='us-west-2',
        config=Config(retries={"total_max_attempts": 1, "mode": "standard"}, read_timeout=None)
    )

def get_neptune_graph_data_claude():
    """Neptune Analytics Claude 그래프에서 데이터 가져오기 (g-ryb6suoa69)"""
    try:
        neptune_client = get_neptune_client()
        
        # 노드 쿼리 (최대 2000개) - openCypher
        nodes_query = "MATCH (n) RETURN id(n) as id, labels(n) as labels, properties(n) as properties LIMIT 2000"
        nodes_response = neptune_client.execute_query(
            graphIdentifier='g-ryb6suoa69',
            queryString=nodes_query,
            language='OPEN_CYPHER'
        )
        
        # 엣지 쿼리 (최대 3000개) - openCypher
        edges_query = "MATCH (a)-[r]->(b) RETURN id(r) as id, type(r) as label, id(a) as source, id(b) as target LIMIT 3000"
        edges_response = neptune_client.execute_query(
            graphIdentifier='g-ryb6suoa69',
            queryString=edges_query,
            language='OPEN_CYPHER'
        )
        
        import json
        
        nodes_data = json.loads(nodes_response['payload'].read().decode('utf-8'))
        edges_data = json.loads(edges_response['payload'].read().decode('utf-8'))
        
        # 전체 노드/엣지 개수 확인
        total_nodes_query = "MATCH (n) RETURN count(n) as count"
        total_edges_query = "MATCH ()-[r]->() RETURN count(r) as count"
        
        total_nodes_response = neptune_client.execute_query(
            graphIdentifier='g-ryb6suoa69',
            queryString=total_nodes_query,
            language='OPEN_CYPHER'
        )
        
        total_edges_response = neptune_client.execute_query(
            graphIdentifier='g-ryb6suoa69',
            queryString=total_edges_query,
            language='OPEN_CYPHER'
        )
        
        total_nodes_data = json.loads(total_nodes_response['payload'].read().decode('utf-8'))
        total_edges_data = json.loads(total_edges_response['payload'].read().decode('utf-8'))
        
        total_nodes_count = total_nodes_data.get('results', [{}])[0].get('count', 0)
        total_edges_count = total_edges_data.get('results', [{}])[0].get('count', 0)
        display_nodes_count = len(nodes_data.get('results', []))
        display_edges_count = len(edges_data.get('results', []))
        
        st.info(f"**Claude 그래프 전체:** 노드 {total_nodes_count:,}개, 엣지 {total_edges_count:,}개\n\n**현재 표시:** 노드 {display_nodes_count:,}개, 엣지 {display_edges_count:,}개")
        
        return nodes_data.get('results', []), edges_data.get('results', [])
    except Exception as e:
        st.error(f"Claude Neptune 데이터 로드 실패: {e}")
        return [], []

def create_neptune_graph_claude():
    """Neptune Analytics Claude 그래프 시각화"""
    net = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white")
    
    nodes, edges = get_neptune_graph_data_claude()
    
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
            
            # 더 의미있는 속성 우선 활용
            bedrock_text = properties.get('AMAZON_BEDROCK_TEXT', '')
            source_uri = properties.get('metadata_x-amz-bedrock-kb-source-uri', '')
            
            # 1순위: AMAZON_BEDROCK_TEXT에서 의미있는 키워드 추출
            if bedrock_text and len(bedrock_text) > 10:
                # HTML 태그와 특수문자 제거 후 의미있는 텍스트 추출
                import re
                clean_text = re.sub(r'<[^>]+>', '', bedrock_text)  # HTML 태그 제거
                clean_text = re.sub(r'[#\-\*\|\\]+', ' ', clean_text)  # 특수문자 제거
                clean_text = clean_text.strip()
                
                if clean_text:
                    text_words = [word for word in clean_text.split() if len(word) > 1]  # 1글자 단어 제외
                    if len(text_words) >= 3:
                        name = f"[Chunk] {' '.join(text_words[:3])}"
                    elif len(text_words) >= 1:
                        chunk_name = ' '.join(text_words[:2]) if len(text_words) >= 2 else text_words[0]
                        name = f"[Chunk] {chunk_name}"
                    else:
                        name = f"[Chunk] {bedrock_text[:20].strip()}"
                else:
                    name = f"[Chunk] {bedrock_text[:20].strip()}"
            # 2순위: 파일명에서 추출
            elif source_uri:
                filename = source_uri.split('/')[-1].replace('.PDF', '').replace('.pdf', '')
                name = filename
            # 3순위: Entity 노드의 ID 정리
            elif 'Entity' in labels and node_id.startswith('x-amz-bedrock-kb-'):
                clean_id = node_id.replace('x-amz-bedrock-kb-', '')
                # 긴 ID는 줄여서 표시
                if len(clean_id) > 20:
                    name = clean_id[:20] + '...'
                else:
                    name = clean_id
            # 4순위: 라벨 기반
            else:
                if 'Chunk' in labels:
                    name = f"[Chunk] {node_id[:15]}..."
                else:
                    name = str(labels[0]) if labels and labels[0] != 'DocumentID' else f"Node-{node_id[:8]}"
            
            # Claude 그래프 색상 (주황색 계열)
            color = "#e67e22" if 'Document' in str(node.get('labels', [])) else "#d35400" if 'Entity' in str(node.get('labels', [])) else "#f39c12"
            
            net.add_node(node_id, 
                        label=str(name), 
                        color=color, 
                        size=15,
                        title=f"Claude Graph\\nLabels: {node.get('labels', [])}\\nProperties: {list(properties.keys())}\\nID: {node_id}")
    
    # 엣지 추가
    for edge in edges:
        source = str(edge.get('source', ''))
        target = str(edge.get('target', ''))
        edge_label = edge.get('label', 'relates')
        
        if source in node_ids and target in node_ids:
            net.add_edge(source, target, label=edge_label, color="#666")
    
    # 그래프 옵션 설정
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