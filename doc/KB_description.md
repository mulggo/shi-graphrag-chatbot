🔍 Neptune Analytics 온톨로지 구조 완전 분석
📊 기본 그래프 개념
🔵 노드 (Node)
정의: 그래프의 점(●), 실제 개체를 표현

역할: 사람, 문서, 개념, 사물 등을 나타냄

속성: key-value 데이터를 저장 가능

🔗 엣지 (Edge)
정의: 노드 간 연결선(→), 관계를 표현

방향성: A → B (방향 있음)

타입: 관계의 종류 (CONTAINS, FROM 등)

🏗️ Neptune Analytics 3계층 온톨로지
1️⃣ DocumentId 노드 (문서 계층)
DocumentId: "DrP50TjwCql2mJV8Fmmc0JANOFrf0g..."
├── 역할: 원본 PDF 문서 식별
├── 속성: S3 경로, 메타데이터
└── 개수: 수십 개 (문서별 1개)

Copy
2️⃣ Chunk 노드 (텍스트 계층)
Chunk: "ca3ea8d3-69c5-4d32-9c35-926e1bb88842"
├── 속성:
│   ├── AMAZON_BEDROCK_TEXT: "실제 문서 텍스트..."
│   ├── AMAZON_BEDROCK_METADATA: "{메타데이터}"
│   ├── metadata_x-amz-bedrock-kb-source-uri: "s3://..."
│   └── metadata_x-amz-bedrock-kb-document-page-number: 1
└── 개수: 수천 개 (문서를 작은 단위로 분할)

Copy
3️⃣ Entity 노드 (개념 계층)
Entity: "centerline (c.l.)"
Entity: "upper deck casing"  
Entity: "steel pipe"
Entity: "s/g room (steam generator room)"
└── 개수: 수천 개 (텍스트에서 추출된 개념들)

Copy
🔗 관계 구조 (엣지 타입)
CONTAINS 관계
Chunk --CONTAINS--> Entity
"문서 청크가 특정 엔티티를 포함한다"

Copy
FROM 관계
Chunk --FROM--> DocumentId
"청크가 특정 문서에서 나왔다"

Copy
📈 데이터 규모
총 노드: 7,552개

총 엣지: 11,949개

노드 비율: Entity > Chunk > DocumentId

🎯 온톨로지 목적과 활용
지식 그래프 RAG 시스템:
질문: "배관 관통부 재료는 무엇인가?"
    ↓
1. Entity 검색: "pipe", "penetration", "material"
    ↓  
2. 연결된 Chunk 찾기: CONTAINS 관계 추적
    ↓
3. 원본 문서 확인: FROM 관계로 DocumentId 추적
    ↓
4. 정확한 답변 생성: 컨텍스트 기반 응답

Copy
의미적 탐색:
Entity("steel pipe") 
    ↓ CONTAINS (역방향)
Chunk("배관 재료 설명")
    ↓ FROM  
DocumentId("Piping_practice_hull_penetration.PDF")

Copy
🔄 온톨로지 연결 패턴
DocumentId ←--FROM-- Chunk --CONTAINS--> Entity
     ↑                 ↓                    ↓
   원본문서        텍스트조각            추출개념

Copy
이 구조는 문서 → 텍스트 → 개념의 계층적 지식 표현으로, 자연어 질의에 대해 정확한 문서 기반 답변을 제공하는 지능형 검색 시스템입니다.