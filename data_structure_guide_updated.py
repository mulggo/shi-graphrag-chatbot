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
        """사실 기반 GraphRAG 설명"""
        st.markdown("# 📚 GraphRAG 구조")
        
        st.info("""
        **데이터 출처:** Neptune Analytics (OpenCypher 엔드포인트)  
        **그래프 모델:** Property Graph 기반 GraphRAG  
        **쿼리 언어:** OpenCypher
        """)
        
        # 1. 시스템 통계 (맨 앞으로 이동)
        st.markdown("## 📊 시스템 개요")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 노드", "7,552개")
        with col2:
            st.metric("총 관계", "11,949개")
        with col3:
            st.metric("문서 수", "11개")
        
        st.markdown("""
        **Property 그래프 구조:**
        - **Document (11개)** ← FROM ← **Chunk (2,531개)** ← CONTAINS ← **Entity (5,010개)**
        - **CONTAINS 관계**: 9,418개 (Chunk → Entity)
        - **FROM 관계**: 2,531개 (Chunk → Document)
        """)
        
        st.success("""
        **현재 시스템 특징:**
        - 단순한 계층 구조 (Document → Chunk → Entity)
        - CONTAINS와 FROM 두 가지 관계 타입만 사용
        - 도메인 특화 엔티티 분류 (선박 소방 규정)
        - 벡터 검색과 그래프 순회 결합
        """)
        
        # 2. GraphRAG 개요
        st.markdown("## 📚 GraphRAG 개요")
        st.markdown("""
        **GraphRAG (Graph Retrieval-Augmented Generation)**는 벡터 검색과 그래프 분석을 결합하여 
        생성형 AI의 정확성과 설명 가능성을 향상시키는 기술입니다.
        
        선박 소방 규정 문서 11개를 2,531개 청크와 5,010개 엔티티로 구조화하여 
        다중 홉 연결을 통해 포괄적이고 관련성 높은 정보를 검색합니다.
        """)
        
        # 3. Property Graph 핵심 개념
        st.markdown("## 🔍 Property Graph 핵심 개념")
        
        st.markdown("""
        **Property Graph는 노드와 엣지에 속성을 저장할 수 있는 그래프 모델입니다.**
        
        **핵심 개념:** 노드는 내부에 속성을 직접 소유, 스키마리스 구조
        
        - **노드(Node)**: 라벨과 속성을 가진 개체 (Document, Chunk, Entity)
        - **엣지(Edge)**: 노드 간의 관계 (CONTAINS, FROM)
        - **속성(Property)**: 각 노드와 엣지에 저장된 키-값 데이터
        - **라벨(Label)**: 노드의 타입을 구분하는 분류자
        """)

        # 4. 선박 소방 규정 온톨로지 설계
        st.markdown("## 🚢 선박 소방 규정 온톨로지 설계")
        
        st.markdown("""
        **국제 해양 규정 체계 기반 도메인 모델링:**
        """)
        
        st.markdown("### 📄 국제 규정 문서 체계")
        st.code("""
# 국제 해양 규정 계층 구조 (11개 문서)
- IMO 국제 규정: SOLAS, FSS Code, FTP Code
- 선급 규정: ABS Rules, DNV Rules
- 국가별 규정: USCG, MCA 가이드라인
- 기술 표준: ISO, IEC 표준
- 업계 모범사례: OCIMF, SIGTTO 가이드
        """, language="text")
        
        st.markdown("### 📚 전문 용어 추출 방법론")
        st.code("""
# 키워드 기반 엔티티 분류 (실제 데이터)
- 탱크 관련 (144개): tank top, cargo tank
- 파이프 시스템 (127개): pipe, sampling pipes  
- 화재 안전 (121개): fire safety systems
- 규정/챕터 (126개): SOLAS chapter, FSS code
- 밸브 시스템 (59개): relief valves, ESD valves
- 펌프 시스템 (56개): fire pumps, sprinkler pump
        """, language="text")
        
        # 5. Plan-Execute Agent 통합
        st.markdown("## 🤖 Plan-Execute Agent 통합")
        
        st.markdown("""
        **실제 구현 기반 에이전트 아키텍처:**
        """)
        
        # 아키텍처 이미지 추가
        try:
            st.image("architecture.png", caption="시스템 아키텍처 다이어그램", use_container_width=True)
        except:
            st.warning("아키텍처 이미지를 찾을 수 없습니다. (architecture.png)")
        
        st.markdown("""
        **아키텍처 구성 요소:**
        """)
        
        st.code("""
1. Plan 단계:
   - 사용자 질문 분석
   - 관련 문서 선택 (11개 중)
   - 영어 검색 쿼리 생성

2. Execute 단계:
   - Neptune Analytics KB 검색 (bedrock_client.retrieve)
   - 관련 청크 및 엔티티 검색

3. Rerank 단계:
   - Cohere Rerank v3.5 (bedrock_runtime.invoke_model)
   - 상위 5개 결과 선별

4. Response 단계:
   - Claude 3.5 Sonnet 응답 생성
   - 참조 문서 메타데이터 포함
        """, language="text")
        
        st.info("""
        **기술 스택:**
        - **Bedrock Agent Runtime**: 직접 KB 검색
        - **Cohere Rerank v3.5**: [문서 재순위화](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-cohere-rerank.html)
        - **Claude 3.5 Sonnet**: 최종 응답 생성
        """)
        
        # 6. 실제 검색 예시
        st.markdown("## 🔍 실제 검색 예시")
        
        st.markdown("### 💡 CO2 시스템 압력 규정 검색")
        
        st.code("""
질문: "CO2 시스템의 압력 규정은?"

1️⃣ Entity 매칭:
   - "CO2System", "pressure", "regulation", "chapter 5"

2️⃣ Neptune Analytics 검색:
   - FSS Chapter 5 관련 청크들
   - CO2 압력 사양 청크들 (CONTAINS 관계)

3️⃣ Document 추적:
   - FSS 합본.pdf (FROM 관계)
   - SOLAS Chapter II-2.pdf

4️⃣ Cohere Reranking:
   - 관련성 점수 기반 재정렬
   - 상위 5개 청크 선별

5️⃣ 응답 생성:
   "CO2 시스템은 15 bar 압력으로 설계되며..."
   + 참조 문서 메타데이터 포함
        """, language="text")

    def _render_fss_ontology(self):
        """FSS 온톨로지 상세 설명"""
        st.markdown("# 🔥 FSS 온톨로지 구조")
        
        st.info("""
        **데이터 출처:** Neptune DB (SPARQL 엔드포인트)  
        **온톨로지:** FSS (Fire Safety Systems) 규정 구조화  
        **쿼리 언어:** SPARQL
        """)
        
        # 1. 시스템 개요
        st.markdown("## 📊 시스템 개요")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 트리플", "653개")
        with col2:
            st.metric("총 클래스", "42개")
        with col3:
            st.metric("속성 수", "28개")
        
        st.markdown("""
        **RDF 그래프 구조:**
        - **주어-술어-목적어** 트리플 구조
        - **URI 기반** 리소스 식별
        - **데이터 모델: RDF, 언어: SPARQL**
        """) 
        
        st.success("""
        **현재 시스템 특징:**
        - 시맨틱 웹 기반 지식 표현
        - 도메인 특화 온톨로지 (선박 소방 규정)
        - 상호 운영성과 확장성 지원
        - 트리플 기반 그래프 연결
        """)
        
        # 2. FSS 온톨로지 개요
        st.markdown("## 📚 FSS 온톨로지 개요")
        st.markdown("""
        **FSS (Fire Safety Systems) 온톨로지**는 선박 소방 규정 도메인의 지식을 
        체계적으로 표현하기 위해 RDF 모델로 설계된 시맨틱 웹 온톨로지입니다.
        
        653개 트리플과 42개 클래스로 구성되어 
        선박 소방 시스템의 복잡한 관계와 규칙을 기계가 이해할 수 있도록 표현합니다.
        """)
        
        # 3. RDF vs RDFS 차이점
        st.markdown("## 🔍 RDF vs RDFS 차이점")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔹 RDF (Resource Description Framework)")
            st.info("""
            **기본 데이터 모델**
            
            - 트리플(주어-술어-목적어) 구조만 제공
            - URI 기반 리소스 식별
            - 단순한 그래프 구조
            - 데이터 저장 형식의 역할
            """)
            
            st.code("""
# RDF 트리플 예시
<CO2System> <locatedIn> <EngineRoom>
<Valve> <connectedTo> <Pipe>
<Chapter5> <describes> <FireSafety>
            """, language="text")
        
        with col2:
            st.markdown("### 🔹 RDFS (RDF Schema)")
            st.success("""
            **RDF + 온톨로지 구조**
            
            - RDF 위에 클래스/인스턴스 개념 추가
            - 계층 구조 및 제약 조건 정의
            - 의미적 추론 가능
            - 온톨로지 스키마 언어 역할
            """)
            
            st.code("""
# RDFS 확장 예시
CO2System rdf:type ExtinguishingSystem
ExtinguishingSystem rdfs:subClassOf FireSystem
hasCapacity rdfs:domain CO2System
            """, language="text")
        
        st.warning("""
        **핵심 차이점:**  
        - **RDF**: "데이터를 어떻게 저장할까?" (트리플 형식)
        - **RDFS**: "데이터가 무엇을 의미하는가?" (클래스, 계층, 제약)
        """)
        
        # RDFS가 RDF에 추가하는 것들
        st.markdown("## 🔧 RDFS가 RDF에 추가하는 핵심 기능")
        
        st.markdown("### 🎯 왜 RDFS가 필요한가?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ❌ RDF만으로는 부족한 것들")
            st.code("""
# RDF 트리플만으로는...
<CO2System> <hasCapacity> "50bar"
<SprinklerSystem> <hasCapacity> "12bar"

❌ CO2System이 무엇인지 모름
❌ 두 시스템의 관계를 모름
❌ hasCapacity가 어떤 타입에만 적용되는지 모름
            """, language="text")
        
        with col2:
            st.markdown("#### ✅ RDFS로 해결되는 것들")
            st.code("""
# RDFS 추가 정보
CO2System rdf:type ExtinguishingSystem
SprinklerSystem rdf:type ExtinguishingSystem
ExtinguishingSystem rdfs:subClassOf FireSystem
hasCapacity rdfs:domain ExtinguishingSystem

✅ 둘 다 소화시스템임을 알 수 있음
✅ 소화시스템은 화재시스템의 하위 개념
✅ hasCapacity는 소화시스템에만 적용
            """, language="text")
        
        st.success("""
        **RDFS의 핵심 가치:**  
        RDF 트리플에 **의미(Semantics)**를 부여하여 기계가 데이터의 구조와 관계를 이해할 수 있게 합니다.
        """)
        
        st.markdown("### 🔗 FSS 온톨로지에서의 실제 활용")
        
        st.markdown("""
        **우리 시스템에서 RDFS가 어떻게 활용되는지 살펴보세요:**
        """)
        
        st.code("""
# 실제 FSS 온톨로지 구조 예시

1️⃣ 클래스 정의 (rdf:type)
Chapter5 rdf:type Chapter
CO2System rdf:type ExtinguishingSystem

2️⃣ 계층 구조 (rdfs:subClassOf)
ExtinguishingSystem rdfs:subClassOf FireSystem
FireSystem rdfs:subClassOf SafetySystem

3️⃣ 속성 제약 (rdfs:domain, rdfs:range)
hasCapacity rdfs:domain ExtinguishingSystem
hasCapacity rdfs:range Capacity

4️⃣ 관계 연결
CO2System hasCapacity CO2_Pressure
CO2System appliesTo CargoSpace
        """, language="text")
        
        st.markdown("### 📋 RDFS 구성 요소 정리")
        
        components_data = [
            {
                "구성요소": "🏷️ 클래스 (Class)",
                "역할": "개념의 분류/타입",
                "FSS 예시": "Chapter, ExtinguishingSystem, ProtectedSpace",
                "설명": "'동물', '식물' 같은 카테고리"
            },
            {
                "구성요소": "📦 인스턴스 (Instance)", 
                "역할": "클래스의 구체적인 예",
                "FSS 예시": "Chapter5, CO2System, CargoSpace",
                "설명": "'진돗개', '장미' 같은 구체적 개체"
            },
            {
                "구성요소": "🔗 프로퍼티 (Property)",
                "역할": "인스턴스 간의 관계", 
                "FSS 예시": "hasComponent, appliesTo, detailsSystem",
                "설명": "'소유하다', '포함하다' 같은 관계"
            },
            {
                "구성요소": "📏 제약조건 (Constraint)",
                "역할": "속성 사용 규칙 정의",
                "FSS 예시": "rdfs:domain, rdfs:range", 
                "설명": "어떤 클래스가 어떤 속성을 가질 수 있는지"
            }
        ]
        
        df_components = pd.DataFrame(components_data)
        st.dataframe(df_components, use_container_width=True, hide_index=True)
        
        st.markdown("### 🎯 실제 검색에서의 활용")
        
        st.markdown("""
        **사용자 질문:** "CO2 시스템의 용량 요구사항은?"
        """)
        
        st.code("""
# SPARQL 쿼리에서 RDFS 활용
SELECT ?system ?capacity WHERE {
  ?system rdf:type fss:ExtinguishingSystem .    # 클래스 정보 활용
  ?system rdfs:label "CO2System" .
  ?system fss:hasCapacity ?capacity .           # 프로퍼티 관계 활용
  ?capacity rdf:type fss:Capacity .             # 타입 제약 확인
}

# RDFS 추론으로 더 많은 결과 발견:
# - ExtinguishingSystem의 상위 클래스 FireSystem도 검색
# - hasCapacity의 하위 속성들도 포함
        """, language="text")
        
        st.info("""
        **RDFS의 실용적 가치:**  
        단순한 키워드 매칭이 아닌 **의미 기반 검색**이 가능해집니다.  
        시스템이 "CO2System이 소화시스템의 일종"임을 이해하고 관련 규정을 찾아줍니다.
        """)
        
        # 4. RDF 기본 개념
        st.markdown("## 📚 RDF 기본 개념")
        
        st.markdown("""
        **모든 정보를 트리플(Subject-Predicate-Object) 형식으로 표현:**
        
        - **리소스(Resource)**: URI로 식별되는 표현 대상 개체
        - **속성(Property)**: 자원의 특성이나 자원 간 관계
        - **값(Value)**: 속성의 값 (다른 리소스 또는 리터럴)
        - **트리플(Triple)**: 주어-술어-목적어 구조의 기본 데이터 단위
        """)
        
        # 4. FSS 도메인 온톨로지 설계
        st.markdown("## 🚢 FSS 도메인 온톨로지 설계")
        
        st.markdown("""
        **선박 소방 규정 체계 기반 시맨틱 모델링:**
        """)
        
        st.markdown("### 🏷️ 주요 클래스 체계")
        st.code("""
# FSS 온톨로지 클래스 계층 구조 (42개 클래스)
- 소방 시스템: FireSystem, CO2System, SprinklerSystem
- 장비 구성요소: Pump, Valve, Tank, Pipe
- 규정 및 기준: Regulation, Standard, Code
- 선박 구조: Deck, Compartment, BulkHead
- 안전 요구사항: SafetyRequirement, TestProcedure
        """, language="text")
        
        st.markdown("### 🔗 주요 관계 속성")
        st.code("""
# 객체 간 관계 정의 (28개 속성)
- hasComponent: 시스템이 구성요소를 포함
- locatedIn: 장비가 특정 위치에 설치
- compliesWith: 규정 준수 관계
- connectedTo: 물리적 연결 관계
- requiresTest: 시험 요구사항 연결
- hasCapacity: 용량 및 성능 속성
        """, language="text")
        
        st.info("""
        **기술 스택:**
        - **RDF 저장소**: Apache Jena TDB 또는 메모리 저장소
        - **SPARQL 엔드포인트**: Apache Jena Fuseki 서버
        - **온톨로지 관리**: RDF 스키마 언어 (RDFS)
        """)
        
        # 6. 실제 검색 예시
        st.markdown("## 🔍 실제 검색 예시")
        
        st.markdown("### 💡 스프링클러 시스템 규정 검색")
        
        st.code("""
질문: "스프링클러 시스템의 압력 요구사항은?"

1️⃣ 리소스 식별:
   - fss:SprinklerSystem, fss:PressureRequirement

2️⃣ SPARQL 쿼리 실행:
   - 스프링클러 시스템 관련 트리플 검색
   - hasComponent, requiresPressure 관계 순회

3️⃣ 규정 추적:
   - compliesWith 관계로 관련 규정 확인
   - SOLAS Chapter II-2, FSS Code 참조

4️⃣ 결과 생성:
   "스프링클러 시스템은 12 bar 이상의 압력을 유지해야..."
   + 관련 규정 및 온톨로지 관계 표시
        """, language="text")
        
        # 도메인 특화 처리 설명 추가
        st.markdown("## 🚢 도메인 특화 온톨로지 설계")
        
        st.markdown("""
        **FSS 온톨로지는 선박 소방 규정 도메인에 특화되어 설계되었습니다:**
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📚 전문 용어 분류")
            st.code("""
# 엔티티 카테고리 (키워드 기반)
- 탱크 관련: tank top, cargo tank
- 파이프 시스템: pipe, sampling pipes  
- 화재 안전: fire safety systems
- 규정/챕터: SOLAS chapter, FSS code
            """, language="text")
        
        with col2:
            st.markdown("### 📄 선박 규정 문서 구조")
            st.code("""
# 국제 해양 규정 표준
- FSS 합본: 국제 화재 안전 시스템 코드
- SOLAS Chapter II-2: 해상인명안전협약
- IGC Code: 국제 가스 운반선 코드
- DNV 선급 규칙: Part 4 Ch6, Part 6 Ch5
            """, language="text")
        
        st.warning("""
        **온톨로지 구성 시 활용:**
        - 이러한 도메인 지식을 바탕으로 클래스 계층 구조 설계
        - 선박 소방 시스템의 실제 관계를 온톨로지에 반영
        - 국제 규정 체계에 맞는 프로퍼티 정의
        """)
        
        st.markdown("---")
        
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

# 전역 인스턴스
schema_explorer = DataSchemaExplorer()