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
        tab1, tab2, tab3 = st.tabs([
            "📊 전체 현황",
            "📚 GraphRAG", 
            "🕸️ GraphDB"
        ])
        
        with tab1:
            self._render_data_overview()

        with tab2:
            self._render_kb_explanation()
        
        with tab3:
            self._render_fss_ontology()
        
    
    def _render_kb_explanation(self):
        """Knowledge Base 쉬운 설명"""
        st.markdown("## 📚 GraphRAG (Knowledge Base)")
        st.markdown("""
        **Knowledge Base는 마치 도서관과 같습니다.**
        선박 소방 규정 문서들을 컴퓨터가 빠르게 찾을 수 있도록 정리해둔 곳입니다.
        """)
        
        # 실제 데이터
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 현재 저장된 데이터")
            st.metric("📄 문서 수", "11개")
            st.metric("✂️ 문서 조각 수", "2,531개")
            st.metric("🌐 지원 언어", "한국어, 영어")
        
        with col2:
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
        st.markdown("## 📄 저장된 문서 목록")
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
        
        # 그래프 구조 설명
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
        
        st.markdown("---")
        
        # 샘플 데이터
        st.markdown("## 📝 샘플 데이터")
        
        tab1, tab2, tab3 = st.tabs(["청크 예시", "엔티티 예시", "관계 예시"])
        
        with tab1:
            st.markdown("### ✂️ 청크(Chunk) 샘플")
            st.markdown("**문서를 검색 가능한 작은 조각으로 분할**")
            
            chunks = [
                {
                    "청크 ID": "chunk_001",
                    "원본 문서": "SOLAS Chapter II-2",
                    "내용 미리보기": "고정식 CO2 소화 시스템은 보호 구역의 총 용적에 대해...",
                    "페이지": "15"
                },
                {
                    "청크 ID": "chunk_002",
                    "원본 문서": "IMO FSS Code",
                    "내용 미리보기": "화재 감지 시스템은 연기, 열, 불꽃을 자동으로 감지하여...",
                    "페이지": "23"
                },
                {
                    "청크 ID": "chunk_003",
                    "원본 문서": "DNV-RU-SHIP",
                    "내용 미리보기": "스프링클러 헤드는 기관실 천장에 3m 간격으로 설치...",
                    "페이지": "42"
                }
            ]
            df_chunks = pd.DataFrame(chunks)
            st.dataframe(df_chunks, use_container_width=True, hide_index=True)
        
        with tab2:
            st.markdown("### 🏷️ 엔티티(Entity) 샘플")
            st.markdown("**문서에서 추출된 핵심 개념과 용어**")
            
            entities = [
                {
                    "엔티티": "CO2 System",
                    "타입": "소화 시스템",
                    "출현 빈도": "127회",
                    "관련 문서": "SOLAS, FSS Code, DNV"
                },
                {
                    "엔티티": "Fire Detection",
                    "타입": "감지 시스템",
                    "출현 빈도": "89회",
                    "관련 문서": "SOLAS, Fire Detection Systems"
                },
                {
                    "엔티티": "Sprinkler Head",
                    "타입": "장비 구성요소",
                    "출현 빈도": "64회",
                    "관련 문서": "DNV, Sprinkler Systems"
                },
                {
                    "엔티티": "Engine Room",
                    "타입": "선박 구역",
                    "출현 빈도": "156회",
                    "관련 문서": "SOLAS, DNV, FSS Code"
                },
                {
                    "엔티티": "Foam Concentrate",
                    "타입": "소화 약제",
                    "출현 빈도": "43회",
                    "관련 문서": "Foam Systems, FSS Code"
                }
            ]
            df_entities = pd.DataFrame(entities)
            st.dataframe(df_entities, use_container_width=True, hide_index=True)
        
        with tab3:
            st.markdown("### 🔗 관계(Relationship) 샘플")
            st.markdown("**노드 간의 연결 관계**")
            
            relationships = [
                {
                    "출발": "SOLAS Chapter II-2",
                    "관계": "CONTAINS",
                    "도착": "chunk_001",
                    "설명": "문서가 청크를 포함"
                },
                {
                    "출발": "chunk_001",
                    "관계": "HAS_ENTITY",
                    "도착": "CO2 System",
                    "설명": "청크에 엔티티 포함"
                },
                {
                    "출발": "CO2 System",
                    "관계": "RELATES_TO",
                    "도착": "Engine Room",
                    "설명": "CO2 시스템이 기관실에 설치"
                },
                {
                    "출발": "Fire Detection",
                    "관계": "TRIGGERS",
                    "도착": "CO2 System",
                    "설명": "화재 감지가 소화 시스템 작동"
                },
                {
                    "출발": "Sprinkler Head",
                    "관계": "PART_OF",
                    "도착": "Sprinkler System",
                    "설명": "스프링클러 헤드는 시스템의 일부"
                }
            ]
            df_relationships = pd.DataFrame(relationships)
            st.dataframe(df_relationships, use_container_width=True, hide_index=True)

    def _render_fss_ontology(self):
        """FSS 온톨로지 상세 설명"""
        st.markdown("# 🔥 FSS 온톨로지 구조")
        
        # 데이터 규모
        st.markdown("## 📊 데이터 규모")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📑 총 트리플", "653개", help="RDF의 기본 데이터 단위")
        with col2:
            st.metric("🏷️ 주요 클래스", "42개", help="엔티티 분류")
        with col3:
            st.metric("📋 구체적 항목", "186개", help="실제 시스템, 규정")
        with col4:
            st.metric("📖 FSS 챕터", "17개", help="FSS 코드의 각 장")
        
        # 트리플 설명
        st.markdown("### 🔗 트리플(Triple)이란?")
        st.markdown("**트리플은 하나의 사실을 표현하는 기본 단위입니다.**")
        
        triple_examples = [
            {"주어": "CO2System", "술어": "rdf:type", "목적어": "ExtinguishingSystem", "의미": "CO2 시스템은 소화 시스템이다"},
            {"주어": "CO2System", "술어": "rdfs:label", "목적어": "CO2 System", "의미": "CO2 시스템의 이름은 'CO2 System'이다"},
            {"주어": "CO2System", "술어": "hasSpecification", "목적어": "CO2_Capacity", "의미": "CO2 시스템은 용량 사양을 가진다"}
        ]
        
        df_triples = pd.DataFrame(triple_examples)
        st.dataframe(df_triples, use_container_width=True, hide_index=True)
        
        # 주요 클래스
        st.markdown("## 🏗️ 주요 클래스 계층")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 클래스별 개수")
            class_data = [
                {"클래스": "Performance", "개수": "38개", "설명": "성능 요구사항"},
                {"클래스": "Requirement", "개수": "19개", "설명": "일반 요구사항"},
                {"클래스": "Chapter", "개수": "17개", "설명": "FSS 코드 챕터"},
                {"클래스": "ExtinguishingSystem", "개수": "11개", "설명": "소화 시스템"},
                {"클래스": "Component", "개수": "9개", "설명": "시스템 구성요소"}
            ]
            df_classes = pd.DataFrame(class_data)
            st.dataframe(df_classes, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 🔥 소화 시스템 종류")
            systems = [
                "CO2System (CO2 시스템)",
                "NitrogenSystem (질소 시스템)",
                "HighExpansionFoamSystem (고팽창 포말)",
                "LowExpansionFoamSystem (저팽창 포말)",
                "WaterSprayingSystem (물분무 시스템)",
                "WaterMistSystem (워터미스트)",
                "DeckFoamSystem (갑판 포말)",
                "HelideckFoamSystem (헬리데크 포말)"
            ]
            for system in systems:
                st.markdown(f"- {system}")
        
        # 관계 패턴
        st.markdown("## 🔗 주요 관계 패턴")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 시스템 구조")
            st.code("""
Chapter 
  ↓ detailsSystem
ExtinguishingSystem
  ↓ hasSpecification  
Performance
  ↓ value
"구체적 값"
            """)
        
        with col2:
            st.markdown("### ⚙️ 구성요소")
            st.code("""
ExtinguishingSystem
  ↓ hasComponent
Component
  ↓ hasSpecification
Specification
  ↓ value
"사양 값"
            """)
        
    
    def _render_data_overview(self):
        """전체 데이터 현황"""        
        # 1. Neptune Analytics (GraphRAG)
        st.markdown("### 🕸️ Neptune Analytics (GraphRAG)")
        
        st.markdown("**용도**: 문서 관계 그래프")
        
        st.markdown("**데이터 구조**:")
        st.markdown("""
        - **노드(Node)**: 7,552개 - 그래프의 각 정보 단위
          - 문서 11개 + 청크 2,531개 + 엔티티 5,010개
        - **라벨(Label)**: 3가지 - 노드의 타입 분류
          - Document, Chunk, Entity
        - **엣지(Edge)**: 11,949개 - 노드 간 연결 관계
        - **프로퍼티(Property)**: 각 항목의 메타데이터
          - 파일명, 페이지 번호, 내용 등
        """)
        
        st.markdown("**쿼리 언어**: OpenCypher")
        
        st.markdown("**상세 분포**:")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 Document", "11개")
        with col2:
            st.metric("📝 Chunk", "2,531개")
        with col3:
            st.metric("🏷️ Entity", "5,010개")
        with col4:
            st.metric("🔗 Edge", "11,949개")
        
        st.markdown("---")
        
        # 2. Neptune DB (SPARQL 온톨로지)
        st.markdown("### 🔥 Neptune DB (SPARQL 온톨로지)")
        
        st.markdown("**용도**: FSS 규정 온톨로지")
        
        st.markdown("**데이터 구조**:")
        st.markdown("""
        - **트리플(Triple)**: 653개
        - **클래스(Class)**: 42개
        - **인스턴스(Instance)**: 186개
        - **프로퍼티(Property)**: RDF 속성 및 관계
        """)
        
        st.markdown("**쿼리 언어**: SPARQL")
        
        st.markdown("**상세 분포**:")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📑 트리플", "653개")
        with col2:
            st.metric("🏷️ 클래스", "42개")
        with col3:
            st.metric("📋 인스턴스", "186개")
        with col4:
            st.metric("📖 챕터", "17개")

# 전역 인스턴스
schema_explorer = DataSchemaExplorer()