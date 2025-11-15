🔍 Neptune Analytics Ontology Structure Complete Analysis

📊 Basic Graph Concepts

🔵 Node
Definition: Points (●) in the graph, representing actual entities

Role: Represents people, documents, concepts, objects, etc.

Properties: Can store key-value data

🔗 Edge
Definition: Connection lines (→) between nodes, representing relationships

Directionality: A → B (directional)

Type: Type of relationship (CONTAINS, FROM, etc.)

🏗️ Neptune Analytics 3-Layer Ontology

1️⃣ DocumentId Node (Document Layer)
DocumentId: "DrP50TjwCql2mJV8Fmmc0JANOFrf0g..."
├── Role: Original PDF document identification
├── Properties: S3 path, metadata
└── Count: Dozens (1 per document)

2️⃣ Chunk Node (Text Layer)
Chunk: "ca3ea8d3-69c5-4d32-9c35-926e1bb88842"
├── Properties:
│   ├── AMAZON_BEDROCK_TEXT: "Actual document text..."
│   ├── AMAZON_BEDROCK_METADATA: "{metadata}"
│   ├── metadata_x-amz-bedrock-kb-source-uri: "s3://..."
│   └── metadata_x-amz-bedrock-kb-document-page-number: 1
└── Count: Thousands (documents split into small units)

3️⃣ Entity Node (Concept Layer)
Entity: "centerline (c.l.)"
Entity: "upper deck casing"  
Entity: "steel pipe"
Entity: "s/g room (steam generator room)"
└── Count: Thousands (concepts extracted from text)

🔗 Relationship Structure (Edge Types)

CONTAINS Relationship
Chunk --CONTAINS--> Entity
"Document chunk contains specific entity"

FROM Relationship
Chunk --FROM--> DocumentId
"Chunk originates from specific document"

📈 Data Scale
Total Nodes: 7,552

Total Edges: 11,949

Node Ratio: Entity > Chunk > DocumentId

🎯 Ontology Purpose and Usage

Knowledge Graph RAG System:
Question: "What materials are used for pipe penetrations?"
    ↓
1. Entity Search: "pipe", "penetration", "material"
    ↓  
2. Find Connected Chunks: Trace CONTAINS relationships
    ↓
3. Verify Original Document: Trace DocumentId via FROM relationships
    ↓
4. Generate Accurate Answer: Context-based response

Semantic Navigation:
Entity("steel pipe") 
    ↓ CONTAINS (reverse)
Chunk("pipe material description")
    ↓ FROM  
DocumentId("Piping_practice_hull_penetration.PDF")

🔄 Ontology Connection Pattern
DocumentId ←--FROM-- Chunk --CONTAINS--> Entity
     ↑                 ↓                    ↓
Original Document   Text Fragment      Extracted Concept

This structure represents hierarchical knowledge of Document → Text → Concept, providing an intelligent search system that delivers accurate document-based answers to natural language queries.