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

def get_neptune_graph_data_bda():
    """Neptune Analytics BDA 그래프에서 데이터 가져오기 (g-goxs5d7fi3)"""
    try:
        neptune_client = get_neptune_client()
        
        # 전체 노드/엣지 개수 확인
        total_nodes_query = "MATCH (n) RETURN count(n) as count"
        total_edges_query = "MATCH ()-[r]->() RETURN count(r) as count"
        
        total_nodes_response = neptune_client.execute_query(
            graphIdentifier='g-goxs5d7fi3',
            queryString=total_nodes_query,
            language='OPEN_CYPHER'
        )
        
        total_edges_response = neptune_client.execute_query(
            graphIdentifier='g-goxs5d7fi3',
            queryString=total_edges_query,
            language='OPEN_CYPHER'
        )
        
        # 노드 쿼리 (최대 2000개) - openCypher
        nodes_query = "MATCH (n) RETURN id(n) as id, labels(n) as labels, properties(n) as properties LIMIT 2000"
        nodes_response = neptune_client.execute_query(
            graphIdentifier='g-goxs5d7fi3',
            queryString=nodes_query,
            language='OPEN_CYPHER'
        )
        
        # 엣지 쿼리 (최대 3000개) - openCypher
        edges_query = "MATCH (a)-[r]->(b) RETURN id(r) as id, type(r) as label, id(a) as source, id(b) as target LIMIT 3000"
        edges_response = neptune_client.execute_query(
            graphIdentifier='g-goxs5d7fi3',
            queryString=edges_query,
            language='OPEN_CYPHER'
        )
        
        import json
        
        total_nodes_data = json.loads(total_nodes_response['payload'].read().decode('utf-8'))
        total_edges_data = json.loads(total_edges_response['payload'].read().decode('utf-8'))
        nodes_data = json.loads(nodes_response['payload'].read().decode('utf-8'))
        edges_data = json.loads(edges_response['payload'].read().decode('utf-8'))
        
        total_nodes_count = total_nodes_data.get('results', [{}])[0].get('count', 0)
        total_edges_count = total_edges_data.get('results', [{}])[0].get('count', 0)
        display_nodes_count = len(nodes_data.get('results', []))
        display_edges_count = len(edges_data.get('results', []))
        
        st.info(f"**BDA 그래프 전체:** 노드 {total_nodes_count:,}개, 엣지 {total_edges_count:,}개\n\n**현재 표시:** 노드 {display_nodes_count:,}개, 엣지 {display_edges_count:,}개")
        
        return nodes_data.get('results', []), edges_data.get('results', [])
    except Exception as e:
        st.error(f"BDA Neptune 데이터 로드 실패: {e}")
        return [], []

def create_neptune_graph_bda():
    """Neptune Analytics BDA 그래프 시각화"""
    net = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white")
    
    nodes, edges = get_neptune_graph_data_bda()
    
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
            
            # DocumentId 노드를 실제 문서명으로 표시
            if 'DocumentId' in labels:
                # DocumentId → 문서명 매핑
                doc_mapping = {
                    'Vsnmv78EMf5JVSfxFID06NAd09nqlaO5O+qTzBVNPpvmelJNdpIpbbYK2nK2J1rM': 'FSS',
                    '26ct1KXQW7CuiihAn7IthgquLEUJLRlzblrREVUINJBqTa9x5Y1HbLjNpmCF7Ptb': 'Piping_practice_hull_penetration',
                    'y5Zn9jwn/9C+FaRr9N+77ODGSynOs0VhVMaU8F8AvzQQC2bbDWSvtSQZc6uxA3bF': 'Design_guidance_hull_penetration',
                    'TqvdAfkUWMgutxmS3kR63z+zCDjXYx3IbD+kDXmCxNe6DREYDdEgQAtCvxcR4vBz': 'DNV-RU-SHIP-Pt6 Ch5 Sec4',
                    '+QCKEoQv941jK98XaDgb5sHOWmJs3nkrD9zIzDOEjpWJdAO/2m8TJ2nwU1tXg7y7': 'IGC_Code_latest',
                    'j2pDvEzQovyNfrWpBXSLybLWdyVR2r17x81gRY3qV1OjY4kfBTVn4pvhUHTcUpaq': 'DNV-RU-SHIP-Pt4 Ch6',
                    't0wgE6bm9deCUgo8qPPwuEfJjaJ/5lXWdp/l/GIuw2PSqo5e1zhQ/okiFd4uK/S+': 'Design guidance_Support',
                    'qR1wt0/DYqNT7f4rEuR5XcVfB9lOixqa6y1tUrL3cSURIlm8lgoS6sAk47Z7SeQm': 'Design guidance_Spoolcutting',
                    'RPrIfZKLci/8WBLJwpLJoc0j2+KRZvDZ2dMbca4nH+wTN+BqN/qfUGIBPbH1umk8': '02-2 SOLAS Chapter II-2_Construction Fire Protection, Fire Detection and Fire Extinction',
                    'lB7MaJexISM5nYRaJjr6u1JUmwvKK6QZXU1CmzjwbHzG3cpGBbaJ4mG/ig3hmyOg': 'SOLAS_2017_Insulation_penetration',
                    '0k0YQOD0F8JkC0EcdK+VmlQyPkwXao3iow4eWJi2A6zffTk9ghq78huHPcV/9i0Q': 'Piping practice_Support'
                }
                name = doc_mapping.get(node_id, f'Document-{node_id[:8]}')
            # x-amz-bedrock-kb- 접두사 제거 (모든 노드에 적용)
            elif node_id.startswith('x-amz-bedrock-kb-'):
                clean_name = node_id.replace('x-amz-bedrock-kb-', '')
                name = clean_name if clean_name.strip() else 'Entity'
            # Chunk 노드 처리
            else:
                bedrock_text = properties.get('AMAZON_BEDROCK_TEXT', '')
                source_uri = properties.get('metadata_x-amz-bedrock-kb-source-uri', '')
                
                if source_uri:
                    filename = source_uri.split('/')[-1].replace('.PDF', '').replace('.pdf', '')
                    name = filename
                elif bedrock_text:
                    text_preview = bedrock_text[:50].strip()
                    name = text_preview.split()[0] if text_preview.split() else 'Chunk'
                else:
                    name = str(labels[0]) if labels else node_id[:8]
            
            # BDA 그래프 색상 (파란색 계열)
            color = "#3498db" if 'DocumentId' in str(node.get('labels', [])) else "#2980b9" if 'Entity' in str(node.get('labels', [])) else "#1abc9c"
            
            net.add_node(node_id, 
                        label=str(name), 
                        color=color, 
                        size=15,
                        title=f"BDA Graph\\nLabels: {node.get('labels', [])}\\nProperties: {list(properties.keys())}\\nID: {node_id}")
    
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