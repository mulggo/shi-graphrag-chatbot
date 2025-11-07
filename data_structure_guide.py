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
        st.markdown("## 📚 문서 저장소 (Knowledge Base)")
        st.markdown("""
        **문서 저장소는 마치 도서관과 같습니다.**
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

    def _render_fss_ontology(self):
        """FSS 온톨로지 상세 설명"""
        st.markdown("# 🔥 FSS 온톨로지 구조")
        
        # 핵심 목적
        st.markdown("## 🎯 핵심 목적")
        st.info("""
        **IMO FSS Code의 디지털 지식화**
        
        국제해사기구(IMO)의 화재 안전 시스템 코드를 구조화된 지식 그래프로 변환하여, 
        선박 설계자, 검사관, 규제 당국이 검색 가능하고 연결된 형태로 활용할 수 있게 합니다.
        """)
        
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
        
        # 활용 가치
        st.markdown("## 🎯 활용 가치")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 사용자별 혜택")
            benefits = [
                "**선박 설계자**: 규정 준수 자동 검증",
                "**검사관**: 체계적인 검사 체크리스트", 
                "**규제 당국**: 일관된 규정 해석",
                "**연구자**: 규정 간 관계 분석"
            ]
            for benefit in benefits:
                st.markdown(f"- {benefit}")
        
        with col2:
            st.markdown("### 🚀 기술적 장점")
            advantages = [
                "**자동화**: 규정 검색 및 적용 자동화",
                "**일관성**: 표준화된 용어 및 구조",
                "**확장성**: 새로운 규정 쉽게 추가",
                "**연결성**: 관련 규정 자동 발견"
            ]
            for advantage in advantages:
                st.markdown(f"- {advantage}")
    
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