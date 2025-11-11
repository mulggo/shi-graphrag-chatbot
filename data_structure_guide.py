"""
데이터 구조 안내서
선박 소방 규정 챗봇이 사용하는 데이터의 구조와 관계를 쉽게 설명하는 페이지
"""
import streamlit as st
import pandas as pd

class DataSchemaExplorer:
    """데이터 구조 안내서 클래스"""
    
    def __init__(self):
        pass

    def render_schema_explorer(self):    
        # 탭 생성
        tab1, tab2 = st.tabs([
            "📚 GraphRAG", 
            "🕸️ GraphDB"
        ])
        
        with tab1:
            self._render_kb_explanation()
        
        with tab2:
            self._render_fss_ontology()
        
    
    def _render_kb_explanation(self):
        """Knowledge Base 쉬운 설명"""
        st.markdown("## 📚 GraphRAG (Knowledge Base)")
        st.markdown("""
        **Knowledge Base는 마치 도서관과 같습니다.**
        선박 소방 규정 문서들을 컴퓨터가 빠르게 찾을 수 있도록 정리해둔 곳입니다.
        """)
        
        st.info("""
        **데이터 출처:** Neptune Analytics (OpenCypher 엔드포인트)  
        **그래프 DB:** Knowledge Graph 기반 RAG (Retrieval-Augmented Generation)  
        **쿼리 언어:** OpenCypher
        """)
        
        # 그래프 구조 설명 (맨 위로 이동)
        st.markdown("## 🕸️ GraphRAG 구조")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 노드(Node) 구성")
            st.markdown("""
            **총 7,552개 노드**
            - **Document (11개)**: 원본 문서
            - **Chunk (2,531개)**: 문서 조각
            - **Entity (5,010개)**: 추출된 개념
            """)
            
            st.markdown("#### 🏷️ 라벨(Label) 종류")
            labels = [
                {"라벨": "Document", "개수": "11개", "설명": "원본 PDF 문서"},
                {"라벨": "Chunk", "개수": "2,531개", "설명": "문서의 작은 조각"},
                {"라벨": "Entity", "개수": "5,010개", "설명": "추출된 핵심 개념"}
            ]
            df_labels = pd.DataFrame(labels)
            st.dataframe(df_labels, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 🔗 엣지(Edge) 구성")
            st.markdown("""
            **총 11,949개 관계**
            - **CONTAINS (9,418개)**: Chunk → Entity
            - **FROM (2,531개)**: Chunk → Document
            """)
            
            st.markdown("#### 🔗 엣지 유형")
            edges = [
                {"관계": "CONTAINS", "개수": "9,418개", "설명": "Chunk가 Entity를 포함"},
                {"관계": "FROM", "개수": "2,531개", "설명": "Chunk가 Document로부터 생성됨"}
            ]
            df_edges = pd.DataFrame(edges)
            st.dataframe(df_edges, use_container_width=True, hide_index=True)

        st.markdown("### 🔍 검색 과정")
        st.markdown("""
        1. **질문 입력** → 사용자가 질문
        2. **의미 분석** → AI가 질문 이해
        3. **문서 검색** → 관련 문서 찾기
        4. **점수 계산** → 관련도 점수 부여
        5. **결과 제공** → 답변과 원본 이미지
        """)

        st.markdown("---")
        
        # 11개 문서 목록
        st.markdown("## 📄 Documents")
        st.markdown("**선박 소방 규정 관련 11개 문서**")
        
        documents = [
            {"번호": "1", "문서명": "FSS 합본", "설명": "국제 화재 안전 시스템 코드 (Fire Safety Systems Code)"},
            {"번호": "2", "문서명": "SOLAS Chapter II-2", "설명": "해상인명안전협약 - 구조, 화재 방호, 화재 탐지 및 소화"},
            {"번호": "3", "문서명": "SOLAS 2017 Insulation penetration", "설명": "SOLAS 단열재 관통 규정"},
            {"번호": "4", "문서명": "IGC Code", "설명": "국제 가스 운반선 코드 (International Gas Carrier Code)"},
            {"번호": "5", "문서명": "DNV-RU-SHIP Pt4 Ch6", "설명": "DNV 선급 규칙 - Part 4 Chapter 6"},
            {"번호": "6", "문서명": "DNV-RU-SHIP Pt6 Ch5 Sec4", "설명": "DNV 선급 규칙 - Part 6 Chapter 5 Section 4"},
            {"번호": "7", "문서명": "Design guidance_Support", "설명": "설계 가이드 - 지지 구조"},
            {"번호": "8", "문서명": "Design guidance_Spoolcutting", "설명": "설계 가이드 - 스풀 절단"},
            {"번호": "9", "문서명": "Design guidance_hull penetration", "설명": "설계 가이드 - 선체 관통부"},
            {"번호": "10", "문서명": "Piping practice_Support", "설명": "배관 실무 - 지지 구조"},
            {"번호": "11", "문서명": "Piping practice_hull penetration", "설명": "배관 실무 - 선체 관통부"}
        ]
        
        df_docs = pd.DataFrame(documents)
        st.dataframe(df_docs, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 샘플 데이터
        st.markdown("## 📝 Chunk, Entity and Relation")
        
        tab1, tab2, tab3 = st.tabs(["청크 예시", "엔티티 예시", "관계 예시"])
        
        with tab1:
            st.markdown("### ✂️ 청크(Chunk) 샘플")
            st.markdown("**문서를 검색 가능한 작은 조각으로 분할 (총 2,531개)**")
            
            st.markdown("#### 📋 청크 속성 구조")
            st.markdown("""
            - **metadata_x-amz-bedrock-kb-source-uri**: S3 원본 문서 경로
              - 예: `s3://shi-kb-bucket/documents/pipes/Piping_practice_hull_penetration.PDF`
            - **AMAZON_BEDROCK_TEXT**: 청크의 실제 텍스트 내용
              - 문서에서 추출된 텍스트 조각
            - **AMAZON_BEDROCK_METADATA**: JSON 메타데이터
              - sourceUrl: 원본 문서 URL
              - relatedContent: 관련 이미지 S3 경로
              - parentText: 상위 컨텍스트 텍스트
            - **metadata_x-amz-bedrock-kb-data-source-id**: 데이터 소스 ID
              - 예: `VDXB3NKJ0O`
            - **metadata_x-amz-bedrock-kb-document-page-number**: 문서 페이지 번호
              - 예: `1.0`, `5.0`
            """)
            
        with tab2:
            st.markdown("### 🏷️ 엔티티(Entity) 샘플")
            st.markdown("**문서에서 추출된 핵심 개념과 용어 (총 5,010개)**")
            
            st.markdown("#### 📋 Entity 노드 구조")
            st.markdown("""
            - **node_id**: `x-amz-bedrock-kb-` 접두사 + 엔티티 이름
              - 예: `x-amz-bedrock-kb-pipe`, `x-amz-bedrock-kb-upper deck casing`
            - **labels**: `["Entity"]` - 모든 엔티티는 Entity 라벨을 가짐
            - **속성**: 별도 속성 없음 (node_id 자체가 엔티티 식별자)
            """)
            
            st.markdown("---")
            
            st.markdown("#### 🏷️ 주요 엔티티 카테고리 (실제 데이터 기반)")
            
            st.info("""
            **분류 방법:** 엔티티 이름에 특정 키워드가 포함된 경우 해당 카테고리로 분류  
            **중복 허용:** 하나의 엔티티가 여러 카테고리에 포함될 수 있음 (예: "stainless steel pipe"는 파이프와 강철 둘 다 포함)  
            **전체 개수:** 5,010개 엔티티 중 키워드 매칭된 항목만 표시
            """)
            
            st.markdown("""
            **키워드 기반 분류 결과:**
            - **탱크 관련 (144개)**: tank top, tank boundaries, single hull tanker, tank deck, oil fuel tanks 등
            - **파이프 시스템 (127개)**: pipe, stainless steel pipe, sampling pipes, sample pipes, pipe tunnel 등
            - **화물 시스템 (126개)**: cargo oil lines, main cargo control spaces, deck cargo 등
            - **규정/챕터 (126개)**: chapter 2, chapter 4, solas chapter ii-2, fss code 등
            - **화재 안전 (121개)**: fire safety systems code, fire condition, fire detection and fire alarm system 등
            - **규정 (100개)**: regulation ii-2/10.9.1.2, solas regulation ii-2/10.6.4, gas regulation valves 등
            - **물/수계통 (83개)**: watertight bulkhead, seawater pump, water spray nozzle, sliding watertight doors 등
            - **선실/공간 (70개)**: s/g room (steam generator room), air condition room, engine-room, pump-rooms 등
            - **데크/갑판 (59개)**: upper deck casing, upper deck, 3rd deck, embarkation deck, helideck 등
            - **밸브 시스템 (59개)**: relief valves, gas regulation valves, excess flow valve, esd valves 등
            - **펌프 시스템 (56개)**: seawater pump, fire pumps, pump-rooms, pump, sprinkler pump 등
            - **강철/재료 (45개)**: stainless steel pipe, steel, steel enclosure, carbon manganese steels 등
            - **포말 시스템 (29개)**: foam, foam generator, helicopter facility foam firefighting appliances 등
            - **엔진/기계 (26개)**: engine-room, engine power, engines, engine casing, internal combustion engine 등
            """)
        
        with tab3:
            st.markdown("### 🔗 관계(Relationship) 샘플")
            st.markdown("**노드 간의 연결 관계 (총 11,949개)**")
            
            st.markdown("#### 📋 관계(Edge) 구조")
            st.markdown("""
            - **type**: 관계 타입 (CONTAINS, FROM)
            - **속성**: 별도 속성 없음 (관계 타입만으로 의미 표현)
            - **방향성**: 단방향 관계 (출발 노드 → 도착 노드)
            """)
            
            st.markdown("---")
            
            st.markdown("#### 🔗 관계 타입별 개수 (실제 데이터)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("CONTAINS", "9,418개", help="Chunk → Entity")
                st.markdown("**의미**: 청크가 엔티티를 포함")
                st.markdown("**예시**: 특정 청크 → pipe, tank, valve 등")
            
            with col2:
                st.metric("FROM", "2,531개", help="Chunk → Document")
                st.markdown("**의미**: 청크가 문서로부터 생성됨")
                st.markdown("**예시**: 청크 → FSS.pdf, Piping_practice.PDF 등")
            
            st.markdown("---")
            
            st.markdown("#### 📊 관계 예시")
            
            relationships = [
                {
                    "출발 노드": "Chunk (청크)",
                    "관계": "CONTAINS →",
                    "도착 노드": "Entity (pipe)",
                    "설명": "청크가 'pipe' 엔티티를 포함"
                },
                {
                    "출발 노드": "Chunk (청크)",
                    "관계": "CONTAINS →",
                    "도착 노드": "Entity (fire safety)",
                    "설명": "청크가 'fire safety' 엔티티를 포함"
                },
                {
                    "출발 노드": "Chunk (청크)",
                    "관계": "FROM →",
                    "도착 노드": "Document (FSS.pdf)",
                    "설명": "청크가 FSS.pdf 문서로부터 생성됨"
                },
                {
                    "출발 노드": "Chunk (청크)",
                    "관계": "FROM →",
                    "도착 노드": "Document (Piping_practice.PDF)",
                    "설명": "청크가 Piping_practice.PDF 문서로부터 생성됨"
                },
                {
                    "출발 노드": "Chunk (청크)",
                    "관계": "CONTAINS →",
                    "도착 노드": "Entity (tank top)",
                    "설명": "청크가 'tank top' 엔티티를 포함"
                }
            ]
            df_relationships = pd.DataFrame(relationships)
            st.dataframe(df_relationships, use_container_width=True, hide_index=True)

    def _render_fss_ontology(self):
        """FSS 온톨로지 상세 설명"""
        st.markdown("# 🔥 FSS 온톨로지 구조")
        
        st.info("""
        **데이터 출처:** Neptune DB (SPARQL 엔드포인트)  
        **온톨로지:** FSS (Fire Safety Systems) 규정 구조화  
        **쿼리 언어:** SPARQL
        """)
        
        # 데이터 규모
        st.markdown("## 📊 데이터 규모")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🔗 총 트리플", "653개", help="RDF의 기본 데이터 단위 (주어-술어-목적어)")
        with col2:
            st.metric("🏷️ 주요 클래스", "42개", help="온톨로지 클래스 분류")
        with col3:
            st.metric("📋 인스턴스", "186개", help="실제 시스템, 규정 인스턴스")
        with col4:
            st.metric("🔗 프로퍼티", "69개", help="RDF 속성 및 관계")
        with col5:
            st.metric("📖 FSS 챕터", "17개", help="FSS 코드의 각 장")
        
        st.markdown("---")
        
        # 클래스, 인스턴스, 프로퍼티 개념 설명
        st.markdown("## 📚 RDF 온톨로지 핵심 개념")
        
        st.info("""
        **그래프 DB의 핵심 개념:**  
        인스턴스는 독립적인 속성을 "소유"하지 않습니다. 대신 **프로퍼티(관계)를 통해 다른 인스턴스와 연결**됩니다.  
        모든 데이터는 **트리플(주어-술어-목적어)** 형태로 저장되며, 이들이 연결되어 그래프를 형성합니다.
        """)
        
        st.markdown("### 🔗 트리플 (Triple) - 모든 것의 기본")
        st.markdown("""
        **RDF는 트리플(Subject-Predicate-Object)로 모든 정보를 표현합니다.**
        
        트리플 = **주어** + **술어** + **목적어**
        """)
        
        st.code("""
예시: "CO2System은 ExtinguishingSystem이다"
→ 주어(Subject): CO2System
→ 술어(Predicate): rdf:type
→ 목적어(Object): ExtinguishingSystem
        """, language="text")
        
        st.markdown("---")
                
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🏷️ 클래스 (Class)")
            st.markdown("""
            **개념의 분류 또는 타입**
            
            예시:
            - `Chapter` (챕터)
            - `ExtinguishingSystem` (소화 시스템)
            - `ProtectedSpace` (보호 공간)
            - `Capacity` (용량)
            
            *마치 "동물", "식물" 같은 카테고리*
            """)
        
        with col2:
            st.markdown("### 📦 인스턴스 (Instance)")
            st.markdown("""
            **클래스의 구체적인 예**
            
            예시:
            - `Chapter5` (Chapter의 인스턴스)
            - `CO2System` (ExtinguishingSystem의 인스턴스)
            - `CargoSpace` (ProtectedSpace의 인스턴스)
            - `CO2_Pressure` (Capacity의 인스턴스)
            
            *마치 "진돗개", "장미" 같은 구체적 개체*
            """)
        
        with col3:
            st.markdown("### 🔗 프로퍼티 (Property)")
            st.markdown("""
            **인스턴스 간의 관계**
            
            예시:
            - `detailsSystem` (다루는 시스템)
            - `appliesTo` (적용되는 곳)
            - `hasSpecification` (가지는 사양)
            - `hasComponent` (가지는 구성요소)
            
            *마치 "소유하다", "포함하다" 같은 관계*
            """)
        
        st.markdown("---")

        st.markdown("### 💡 관계 구조의 특징")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔗 공유되는 인스턴스")
            st.markdown("""
            **여러 시스템이 같은 공간을 공유합니다:**
            - `CargoSpace`, `MachinerySpace`, `RoRoSpace`는
            - CO2System, FoamSystem, WaterSprayingSystem 등
            - 여러 소화 시스템에서 **공통으로 참조**됩니다
            
            **이것이 그래프 DB의 장점입니다:**
            - 데이터 중복 없이 관계로 연결
            - 한 번 정의된 공간을 여러 시스템이 재사용
            """)
        
        with col2:
            st.markdown("#### 📋 관계 타입 (Property)")
            st.markdown("""
            **주요 프로퍼티 설명:**
            
            - **detailsSystem**: Chapter → System
              - 챕터가 다루는 소화 시스템
            - **appliesTo**: System → Space
              - 시스템이 적용되는 보호 공간
            - **hasSpecification**: System → Spec
              - 시스템의 기술 사양 (압력, 온도, 성능 등)
            - **hasComponent**: System → Component
              - 시스템의 구성 요소
            """)


        st.markdown("---")


        # 실제 예시로 설명
        st.markdown("### 💡 전체 구조 흐름 (실제 데이터)")
        
        st.markdown("""
        **4단계 계층 구조로 정보가 연결됩니다:**
        """)
        
        st.code("""
1단계: 클래스 정의
   Chapter (클래스) ← "챕터"라는 개념
   
2단계: 인스턴스 생성
   Chapter5 (인스턴스) ← Chapter 클래스의 구체적 예
   rdf:type → Chapter
   rdfs:label → "Chapter 5 Fixed gas fire-extinguishing systems"
   
3단계: 프로퍼티로 연결
   Chapter5 --[detailsSystem]--> CO2System
   (Chapter5가 CO2System을 다룬다)
   
4단계: 하위 구조 확장
   CO2System --[appliesTo]--> CargoSpace
   CO2System --[hasSpecification]--> CO2_Pressure
   CO2System --[hasSpecification]--> CO2_Temperature
   
5단계: 구체적 값
   CO2_Pressure --[value]--> "15 bar"
   CO2_Temperature --[value]--> "-18°C"
        """, language="text")
        
        st.markdown("""
        **이렇게 트리플들이 연결되어 복잡한 규정 구조를 표현합니다.**
        - 총 653개의 트리플이 이런 방식으로 연결되어 있습니다
        - 42개 클래스, 186개 인스턴스가 서로 관계를 맺고 있습니다
        """)
        
        st.markdown("---")
                
        # 온톨로지 구조 시각화
        st.markdown("## 🔗 온톨로지 구조 예시")
        
        st.info("""
        **표시 범위:** 전체 17개 Chapter 중 3개 Chapter (5, 6, 7)의 상세 구조  
        **데이터 출처:** Neptune DB SPARQL 쿼리로 실제 조회한 데이터  
        **구조 깊이:** Chapter → ExtinguishingSystem → Specification/Component (3단계)
        """)
        
        st.markdown("### 온톨로지 계층 구조 (Chapter 5, 6, 7)")
        st.code("""Chapter5 (Fixed gas fire-extinguishing systems)
└── [detailsSystem]
    └── CO2System : ExtinguishingSystem
        ├── [appliesTo]
        │   ├── CargoSpace : ProtectedSpace
        │   ├── MachinerySpace : ProtectedSpace
        │   └── RoRoSpace : ProtectedSpace
        └── [hasSpecification]
            ├── CO2_CargoVolPercentage : Capacity
            ├── CO2_MachineryVolPercentage : Capacity
            ├── CO2_Pressure : Pressure
            ├── CO2_Temperature : Temperature
            ├── CO2_DischargeTime : Performance
            └── CO2_Controls : Control

Chapter6 (Fixed foam fire-extinguishing system)
└── [detailsSystem]
    └── HighExpansionFoamSystem : ExtinguishingSystem
        ├── [appliesTo]
        │   ├── CargoSpace : ProtectedSpace
        │   ├── MachinerySpace : ProtectedSpace
        │   └── RoRoSpace : ProtectedSpace
        ├── [hasSpecification]
        │   ├── DeckHeightSpec : Specification
        │   ├── FoamGeneratorClearance : Performance
        │   ├── FoamGeneratorSpacing : Performance
        │   └── HighFoam_FillingTime : Performance
        ├── [hasTemperature]
        │   ├── AmbientTemperature : Temperature
        │   └── FoamConcentrateTemperature : Temperature
        ├── [hasWeight]
        │   └── FoamConcentrateDensity : Weight
        ├── [hasDuration]
        │   └── NominalFillingTime : Duration
        └── [hasDesignRequirement]
            └── SectioningRequirement : Requirement

Chapter7 (Water-spraying systems)
└── [detailsSystem]
    └── WaterSprayingSystem : ExtinguishingSystem
        └── [appliesTo]
            └── MachinerySpace : ProtectedSpace
└── detailsSystem → CabinBalconySystem
        """, language="text")
        
        st.markdown("---")
        
        # 관계 패턴 설명
        st.markdown("## 📊 주요 관계 패턴")
        
        st.markdown("### 🔗 실제 관계 구조 예시: CO2System")
        
        st.markdown("""
        **CO2System 인스턴스가 다른 인스턴스들과 어떻게 연결되어 있는지 보여줍니다.**  
        각 화살표는 프로퍼티(관계)를 나타내며, 이를 통해 정보가 연결됩니다.
        """)

# 전역 인스턴스
schema_explorer = DataSchemaExplorer()
