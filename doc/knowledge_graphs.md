# Knowledge Graphs Documentation

## Overview

The Ship Firefighting Rules Chatbot features two powerful knowledge graph visualization systems that provide interactive exploration of regulation documents and their relationships. These graphs help users understand the complex structure of maritime safety regulations through visual representation.

## Graph Types

### 1. GraphRAG (Neptune Analytics)

**Purpose**: Document-entity relationship visualization using Neptune Analytics graph database.

**Data Source**: Neptune Analytics with OpenCypher query language

**Graph Structure**:
- **Total Nodes**: 7,552
  - Document (11): Original PDF documents
  - Chunk (2,531): Document fragments
  - Entity (5,010): Extracted concepts and terms
- **Total Relationships**: 11,949
  - CONTAINS (9,418): Chunk → Entity relationships
  - FROM (2,531): Chunk → Document relationships

**Visualization Features**:
- **Interactive Display**: 900px height with full interactivity
- **Node Limit**: Displays up to 2,000 nodes and 3,000 edges for performance
- **Color Coding**: 
  - Cyan (#4ecdc4): Document nodes
  - Blue (#45b7d1): Entity nodes
  - Orange (#ff9f43): Other nodes
- **Physics Engine**: Barnes-Hut algorithm for natural node positioning
- **User Interaction**: Click, drag, zoom, and hover for details

**Implementation**: `knowledge_graph.py`

#### Key Functions

**get_neptune_graph_data()**
```python
def get_neptune_graph_data():
    """Fetch graph data from Neptune Analytics"""
    # OpenCypher queries for nodes and edges
    nodes_query = "MATCH (n) RETURN id(n) as id, labels(n) as labels, properties(n) as properties LIMIT 2000"
    edges_query = "MATCH (a)-[r]->(b) RETURN id(r) as id, type(r) as label, id(a) as source, id(b) as target LIMIT 3000"
```

**create_neptune_graph()**
```python
def create_neptune_graph():
    """Create interactive Neptune Analytics graph visualization"""
    net = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white")
    # Add nodes and edges with color coding and physics
```

#### Neptune Analytics Configuration
- **Graph ID**: `g-gqisj8edd6`
- **Region**: `us-west-2`
- **Query Language**: OpenCypher
- **Endpoint**: Neptune Analytics API

### 2. FSS Ontology Graph (Neptune SPARQL)

**Purpose**: Semantic ontology visualization of Fire Safety Systems (FSS) regulations using SPARQL queries.

**Data Source**: Neptune DB with SPARQL endpoint

**Graph Structure**:
- **Total Triples**: 653 RDF triples
- **Classes**: 42 ontology classes
- **Instances**: 186 concrete instances
- **FSS Chapters**: 17 structured chapters

**Visualization Features**:
- **Directed Graph**: Arrows show relationship direction
- **Semantic Relationships**: RDF-based ontology structure
- **Chapter Organization**: FSS Code chapter hierarchy
- **Interactive Display**: 900px height with full interactivity
- **Color Coding**: Based on node type and class hierarchy

**Implementation**: `fss_full_graph.py`

#### Key Functions

**get_full_ontology()**
```python
def get_full_ontology():
    """Fetch complete FSS ontology from Neptune SPARQL"""
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
    """Create interactive FSS ontology graph visualization"""
    net = Network(height="900px", width="100%", bgcolor="#1e1e1e", font_color="white")
    # Process RDF triples and create semantic graph
```

#### Neptune SPARQL Configuration
- **Endpoint**: `shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com`
- **Port**: 8182
- **Protocol**: HTTPS with SigV4 authentication
- **Query Language**: SPARQL 1.1

## User Interface Integration

### Sidebar Navigation

Users can access knowledge graphs through the sidebar:

```python
# In ui/sidebar.py
st.markdown("### 🕸️ 지식 그래프")
graph_type = st.radio(
    "그래프 선택",
    ["🕸️ 모든 문서의 GraphRAG", "FSS 문서 GraphDB"],
    key="graph_selector"
)
```

### Graph Display

When a graph is selected:
1. Chat interface is hidden
2. Graph visualization is displayed in main area
3. Descriptive information is shown above the graph
4. Close button allows return to chat mode

```python
# In app.py
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

## Technical Implementation

### PyVis Network Library

Both graphs use PyVis for visualization:

```python
from pyvis.network import Network

net = Network(
    height="900px",
    width="100%",
    bgcolor="#1e1e1e",
    font_color="white"
)
```

### Physics Configuration

**GraphRAG Physics**:
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

**FSS Ontology Physics**:
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

### AWS Authentication

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

## Performance Optimization

### Node Limiting

To ensure smooth performance:
- **GraphRAG**: Limited to 2,000 nodes and 3,000 edges
- **FSS Ontology**: Displays all 653 triples (manageable size)

### Caching

```python
@st.cache_resource
def get_neptune_client():
    return boto3.client('neptune-graph', region_name='us-west-2')
```

### Lazy Loading

Graphs are only loaded when selected, not on initial page load.

## Use Cases

### GraphRAG Use Cases

1. **Document Discovery**: Find related documents through entity connections
2. **Concept Exploration**: Understand how concepts relate across documents
3. **Content Navigation**: Visual navigation of document structure
4. **Relationship Analysis**: Identify patterns in document relationships

### FSS Ontology Use Cases

1. **Regulation Structure**: Understand FSS Code organization
2. **Semantic Relationships**: Explore ontological connections
3. **Chapter Navigation**: Navigate through FSS chapters visually
4. **Compliance Mapping**: Map requirements to regulation structure

## Troubleshooting

### Common Issues

**Neptune Analytics Connection**:
```python
# Check graph ID and region
neptune_client.execute_query(
    graphIdentifier='g-gqisj8edd6',
    queryString=query,
    language='OPEN_CYPHER'
)
```

**Neptune SPARQL Connection**:
```python
# Verify endpoint and authentication
NEPTUNE_ENDPOINT = "shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com"
SPARQL_ENDPOINT = f"https://{NEPTUNE_ENDPOINT}:8182/sparql"
```

**Graph Not Displaying**:
- Check browser console for JavaScript errors
- Verify HTML component rendering
- Ensure sufficient browser memory

**Slow Performance**:
- Reduce node limit in queries
- Optimize physics settings
- Check network latency to Neptune

## Future Enhancements

### Planned Features

1. **Search and Filter**: Search nodes by name or property
2. **Subgraph Extraction**: Extract and display specific subgraphs
3. **Export Functionality**: Export graph data and images
4. **Custom Layouts**: User-selectable layout algorithms
5. **Node Details Panel**: Detailed information on node selection
6. **Path Finding**: Find shortest paths between nodes
7. **Community Detection**: Identify node clusters and communities
8. **Time-based Filtering**: Filter by document date or version

### Technical Improvements

1. **Progressive Loading**: Load large graphs incrementally
2. **WebGL Rendering**: Use WebGL for better performance
3. **Graph Analytics**: Built-in graph metrics and statistics
4. **Custom Styling**: User-customizable colors and styles
5. **Mobile Optimization**: Touch-friendly controls for mobile devices

## Best Practices

### For Users

1. **Start with Overview**: Use zoom out to see overall structure
2. **Focus on Areas**: Zoom into specific areas of interest
3. **Use Hover**: Hover over nodes to see details
4. **Drag to Explore**: Drag nodes to reorganize layout
5. **Close When Done**: Close graph to return to chat

### For Developers

1. **Limit Query Results**: Always limit node and edge counts
2. **Cache Clients**: Use Streamlit caching for AWS clients
3. **Handle Errors**: Gracefully handle connection failures
4. **Optimize Physics**: Balance visual appeal and performance
5. **Test Performance**: Test with maximum expected data size

## References

- **PyVis Documentation**: https://pyvis.readthedocs.io/
- **Neptune Analytics**: https://docs.aws.amazon.com/neptune-analytics/
- **Neptune SPARQL**: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-api.html
- **OpenCypher**: https://opencypher.org/
- **SPARQL 1.1**: https://www.w3.org/TR/sparql11-query/
