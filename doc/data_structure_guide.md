# Data Structure Guide Documentation

## Overview

The Data Structure Guide is an interactive documentation feature that helps users understand the underlying data architecture of the Ship Firefighting Rules Chatbot. It provides comprehensive information about both Neptune Analytics (GraphRAG) and Neptune DB (SPARQL) data structures in an accessible format.

## Purpose

The guide serves multiple audiences:
- **End Users**: Understand how the system organizes and retrieves information
- **Developers**: Learn the technical structure for system maintenance and extension
- **Data Analysts**: Explore data models and relationships
- **System Administrators**: Monitor data statistics and system health

## Implementation

**File**: `data_structure_guide.py`

**Class**: `DataSchemaExplorer`

### Main Components

```python
class DataSchemaExplorer:
    """데이터 구조 안내서 클래스"""
    
    def render_schema_explorer(self):
        """Main rendering function with tabbed interface"""
        tab1, tab2 = st.tabs([
            "📚 GraphRAG", 
            "🕸️ GraphDB"
        ])
```

## User Interface

### Tab Structure

The guide uses a two-tab interface:

1. **📚 GraphRAG Tab**: Neptune Analytics structure and statistics
2. **🕸️ GraphDB Tab**: Neptune SPARQL ontology details

### Access Method

Users access the guide through the sidebar:

```python
# In ui/sidebar.py
if st.button("📊 데이터 구조 안내서", use_container_width=True):
    st.session_state.show_data_schema = True
    st.rerun()
```

## GraphRAG Tab (Neptune Analytics)

### Overview Section

**Purpose**: Explain the Knowledge Base concept in simple terms

**Content**:
- Library analogy for easy understanding
- Data source information (Neptune Analytics)
- Query language (OpenCypher)
- Purpose and functionality

```python
def _render_kb_explanation(self):
    """Knowledge Base 쉬운 설명"""
    st.markdown("## 📚 GraphRAG (Knowledge Base)")
    st.markdown("""
    **Knowledge Base는 마치 도서관과 같습니다.**
    선박 소방 규정 문서들을 컴퓨터가 빠르게 찾을 수 있도록 정리해둔 곳입니다.
    """)
```

### Graph Structure Section

**Node Composition**:
- **Total Nodes**: 7,552
  - Document (11): Original PDF documents
  - Chunk (2,531): Document fragments
  - Entity (5,010): Extracted concepts

**Edge Composition**:
- **Total Relationships**: 11,949
  - CONTAINS (9,418): Chunk → Entity
  - FROM (2,531): Chunk → Document

**Visual Display**:
```python
# Two-column layout for nodes and edges
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 노드(Node) 구성")
    # Node statistics and labels table
    
with col2:
    st.markdown("### 🔗 엣지(Edge) 구성")
    # Edge statistics and types table
```

### Search Process Section

**Purpose**: Explain how the system retrieves information

**Steps**:
1. **질문 입력** → User asks a question
2. **의미 분석** → AI understands the question
3. **문서 검색** → Find relevant documents
4. **점수 계산** → Assign relevance scores
5. **결과 제공** → Provide answer with original images

### Document List Section

**Purpose**: Display all 11 documents in the knowledge base

**Format**:
```python
documents = [
    {"번호": "1", "문서명": "FSS 합본", "설명": "국제 화재 안전 시스템 코드"},
    {"번호": "2", "문서명": "SOLAS Chapter II-2", "설명": "해상인명안전협약"},
    # ... more documents
]
df_documents = pd.DataFrame(documents)
st.dataframe(df_documents, use_container_width=True, hide_index=True)
```

**Document List**:
1. FSS 합본 (Fire Safety Systems Code)
2. SOLAS Chapter II-2
3. SOLAS 2017 Insulation penetration
4. IGC Code (International Gas Carrier Code)
5. DNV-RU-SHIP Pt.6 Ch.7 (Fire safety)
6. DNV-RU-SHIP Pt.6 Ch.8 (Fire detection and alarm)
7. DNV-RU-SHIP Pt.6 Ch.9 (Fire extinction)
8. DNV-RU-SHIP Pt.6 Ch.10 (Fire protection)
9. DNV-RU-SHIP Pt.6 Ch.11 (Escape routes)
10. DNV-RU-SHIP Pt.6 Ch.12 (Helicopter facilities)
11. DNV-RU-SHIP Pt.6 Ch.13 (Operational requirements)

## GraphDB Tab (Neptune SPARQL)

### FSS Ontology Section

**Purpose**: Explain the SPARQL-based ontology structure

**Content**:
- RDF triple structure explanation
- Ontology class hierarchy
- Instance relationships
- SPARQL query examples

```python
def _render_fss_ontology(self):
    """FSS 온톨로지 설명"""
    st.markdown("## 🕸️ GraphDB (FSS Ontology)")
    st.markdown("""
    **SPARQL 기반 의미론적 온톨로지**
    FSS(Fire Safety Systems) 규정의 구조화된 지식 표현입니다.
    """)
```

### Ontology Statistics

**Structure**:
- **Total Triples**: 653 RDF triples
- **Classes**: 42 ontology classes
- **Instances**: 186 concrete instances
- **FSS Chapters**: 17 structured chapters

### RDF Triple Explanation

**Purpose**: Help users understand RDF structure

**Format**: Subject - Predicate - Object

**Example**:
```
fss:Chapter1 rdf:type fss:FireSafetyChapter
fss:Chapter1 fss:hasTitle "General"
fss:Chapter1 fss:contains fss:Section1_1
```

### SPARQL Query Examples

**Purpose**: Show how to query the ontology

**Basic Query**:
```sparql
PREFIX fss: <http://www.semanticweb.org/fss#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-schema#>

SELECT ?chapter ?title
WHERE {
    ?chapter rdf:type fss:FireSafetyChapter .
    ?chapter fss:hasTitle ?title .
}
```

## Data Visualization

### Tables and DataFrames

The guide uses Pandas DataFrames for structured data display:

```python
import pandas as pd

# Node labels table
labels = [
    {"라벨": "Document", "개수": "11개", "설명": "원본 PDF 문서"},
    {"라벨": "Chunk", "개수": "2,531개", "설명": "문서의 작은 조각"},
    {"라벨": "Entity", "개수": "5,010개", "설명": "추출된 핵심 개념"}
]
df_labels = pd.DataFrame(labels)
st.dataframe(df_labels, use_container_width=True, hide_index=True)
```

### Statistics Display

**Metrics**:
- Node counts by type
- Edge counts by relationship
- Document counts
- Triple counts
- Class and instance counts

### Visual Formatting

**Color Coding**:
- Info boxes for important information
- Success boxes for statistics
- Warning boxes for limitations
- Error boxes for issues

```python
st.info("""
**데이터 출처:** Neptune Analytics (OpenCypher 엔드포인트)  
**그래프 DB:** Knowledge Graph 기반 RAG
**쿼리 언어:** OpenCypher
""")
```

## Integration with Main Application

### Session State Management

```python
# In app.py
if st.session_state.get('show_data_schema', False):
    from data_structure_guide import schema_explorer
    schema_explorer.render_schema_explorer()
```

### Navigation Flow

1. User clicks "📊 데이터 구조 안내서" in sidebar
2. `show_data_schema` flag is set to True
3. Chat interface is hidden
4. Data structure guide is displayed
5. User can close to return to chat

### Close Button

```python
if st.button("❌ 닫기", use_container_width=True):
    st.session_state.show_data_schema = False
    st.rerun()
```

## Technical Details

### Data Sources

**Neptune Analytics**:
- Graph ID: `g-gqisj8edd6`
- Region: `us-west-2`
- Query Language: OpenCypher
- Purpose: Document-entity relationships

**Neptune SPARQL**:
- Endpoint: `shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com`
- Port: 8182
- Query Language: SPARQL 1.1
- Purpose: Semantic ontology

### Performance Considerations

**Caching**:
- Static content is cached
- Statistics are computed once per session
- No real-time queries (uses pre-computed values)

**Lazy Loading**:
- Guide content only loads when accessed
- Reduces initial page load time
- Improves overall application performance

## Use Cases

### For End Users

1. **Understanding Search Results**: Learn how the system finds information
2. **Document Discovery**: See what documents are available
3. **System Transparency**: Understand the data behind answers
4. **Learning Resource**: Educational content about the system

### For Developers

1. **System Documentation**: Technical reference for data structures
2. **Query Development**: Examples for writing queries
3. **Data Model Understanding**: Learn the graph schema
4. **Debugging**: Verify data structure and statistics

### For Data Analysts

1. **Data Exploration**: Understand available data
2. **Relationship Analysis**: Learn how data is connected
3. **Statistics Review**: Monitor data growth and distribution
4. **Query Planning**: Plan analytical queries

## Best Practices

### Content Updates

When updating the guide:
1. Keep explanations simple and accessible
2. Use analogies for complex concepts
3. Provide visual examples
4. Include actual statistics
5. Update document lists when adding new documents

### User Experience

1. **Progressive Disclosure**: Start simple, add details gradually
2. **Visual Hierarchy**: Use headers and formatting effectively
3. **Interactive Elements**: Tables and expandable sections
4. **Clear Navigation**: Easy to find and return from guide

### Maintenance

1. **Regular Updates**: Keep statistics current
2. **Accuracy**: Verify all numbers and examples
3. **Consistency**: Match actual system behavior
4. **Documentation**: Comment code for future maintainers

## Future Enhancements

### Planned Features

1. **Real-time Statistics**: Query actual counts from Neptune
2. **Interactive Diagrams**: Visual schema representations
3. **Sample Queries**: Executable query examples
4. **Data Quality Metrics**: Show data completeness and quality
5. **Export Functionality**: Download schema documentation
6. **Search Functionality**: Search within the guide
7. **Version History**: Track schema changes over time

### Technical Improvements

1. **Dynamic Content**: Generate content from actual data
2. **Performance Monitoring**: Show query performance stats
3. **Data Lineage**: Show data flow and transformations
4. **Schema Validation**: Verify schema consistency
5. **Automated Updates**: Auto-update when data changes

## Troubleshooting

### Common Issues

**Guide Not Displaying**:
- Check session state flags
- Verify import statements
- Check for Python errors in console

**Incorrect Statistics**:
- Update hardcoded values
- Verify Neptune connectivity
- Check query results

**Formatting Issues**:
- Verify Markdown syntax
- Check DataFrame rendering
- Test in different browsers

## References

- **Neptune Analytics Documentation**: https://docs.aws.amazon.com/neptune-analytics/
- **Neptune SPARQL Documentation**: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-api.html
- **Streamlit DataFrames**: https://docs.streamlit.io/library/api-reference/data/st.dataframe
- **Pandas Documentation**: https://pandas.pydata.org/docs/
