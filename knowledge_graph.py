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

def get_neptune_graph_data():
    """Neptune Analytics에서 전체 그래프 데이터 가져오기"""
    try:
        neptune_client = get_neptune_client()
        
        # 노드 쿼리 (최대 2000개) - openCypher
        nodes_query = "MATCH (n) RETURN id(n) as id, labels(n) as labels, properties(n) as properties LIMIT 2000"
        # 환경변수에서 BDA Neptune Graph ID 가져오기 (기본 그래프)
        import os
        graph_id = os.getenv('NEPTUNE_BDA_GRAPH_ID', 'g-goxs5d7fi3')
        
        nodes_response = neptune_client.execute_query(
            graphIdentifier=graph_id,
            queryString=nodes_query,
            language='OPEN_CYPHER'
        )
        
        # 엣지 쿼리 (최대 3000개) - openCypher
        edges_query = "MATCH (a)-[r]->(b) RETURN id(r) as id, type(r) as label, id(a) as source, id(b) as target LIMIT 3000"
        edges_response = neptune_client.execute_query(
            graphIdentifier=graph_id,
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
            
            # 더 의미있는 속성 우선 활용
            bedrock_text = properties.get('AMAZON_BEDROCK_TEXT', '')
            source_uri = properties.get('metadata_x-amz-bedrock-kb-source-uri', '')
            
            # 1순위: AMAZON_BEDROCK_TEXT에서 의미있는 키워드 추출
            if bedrock_text and len(bedrock_text) > 10:
                # HTML 태그와 특수문자 제거 후 의믴있는 텍스트 추출
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