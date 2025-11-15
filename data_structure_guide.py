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
        
        st.markdown("### 📄 실제 11개 문서 목록")
        st.code("""
# 실제 Knowledge Base 문서 (11개)
1. FSS 합본 - 국제 화재 안전 시스템 코드
2. SOLAS Chapter II-2 - 해상인명안전협약 화재 방호
3. SOLAS 2017 Insulation penetration - 단열재 관통 규정
4. IGC Code - 국제 가스 운반선 코드
5. DNV-RU-SHIP Pt4 Ch6 - DNV 선급 규칙 Part 4 Chapter 6
6. DNV-RU-SHIP Pt6 Ch5 Sec4 - DNV 선급 규칙 Part 6 Chapter 5 Section 4
7. Design guidance_Support - 설계 가이드 지지 구조
8. Design guidance_Spoolcutting - 설계 가이드 스풀 절단
9. Design guidance_hull penetration - 설계 가이드 선체 관통부
10. Piping practice_Support - 배관 실무 지지 구조
11. Piping practice_hull penetration - 배관 실무 선체 관통부
        """, language="text")
        
        st.markdown("### 📚 전문 용어 추출 방법론")
        st.code("""
# 키워드 기반 엔티티 분류 (실제 Neptune Analytics 데이터)
- 시스템 관련 (224개): insulation system, containment system, membrane cargo containment systems
- 규정/챕터 (206개): chapter 19, chapter 9, SOLAS chapter, FSS code
- 파이프 시스템 (141개): pipe insulation, pipe spacing, longitudinally welded pipes
- 탱크 관련 (139개): cargo tank shell, semi-membrane tank, spherical tank construction
- 화재 안전 (109개): fire pumps, fire main, fire detection, firefighting systems
- 밸브 시스템 (72개): pressure relief valve, cargo tank valves, emergency shutdown valves
- 펌프 시스템 (59개): fire pumps, pump housings, circulating pumps, cargo pump rooms
- 안전 시스템 (23개): fire safety systems code, international code for fire safety systems
        """, language="text")
        

        
        # 5. Plan-Execute Agent 통합
        st.markdown("## 🧠 Plan-Execute Agent 통합")
        
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
질문: "파이프 절연 요구사항은?"

1️⃣ Entity 매칭:
   - "pipe insulation", "pipe spacing", "insulation system"

2️⃣ Neptune Analytics 검색:
   - 파이프 절연 관련 청크들
   - 절연 시스템 사양 청크들 (CONTAINS 관계)

3️⃣ Document 추적:
   - Design guidance_Support.pdf (FROM 관계)
   - Piping practice_Support.pdf

4️⃣ Cohere Reranking:
   - 관련성 점수 기반 재정렬
   - 상위 5개 청크 선별

5️⃣ 응답 생성:
   "파이프 절연은 화재 등급에 따라 A-60 기준으로..."
   + 참조 문서 메타데이터 포함
        """, language="text")
        

        


    def _render_kb_explanation_old(self):
        """Knowledge Base 쉬운 설명"""
        st.markdown("## 📚 GraphRAG (Knowledge Base)")
        st.markdown("""
        **Knowledge Base는 마치 도서관과 같습니다.**
        선박 소방 규정 문서들을 컴퓨터가 빠르게 찾을 수 있도록 정리해둔 곳입니다.
        """)
        
        st.info("""
        **데이터 출처:** Neptune Analytics (OpenCypher 엔드포인트)  
        **그래프 모델:** Property Graph (속성 그래프)  
        **그래프 DB:** Knowledge Graph 기반 RAG (Retrieval-Augmented Generation)  
        **쿼리 언어:** OpenCypher
        """)
        
        # Property Graph 모델 설명 추가
        st.markdown("### 🏗️ Property Graph 모델")
        st.markdown("""
        **Property Graph는 노드와 엣지에 속성을 저장할 수 있는 그래프 모델입니다.**
        
        - **노드(Node)**: 라벨과 속성을 가진 개체 (Document, Chunk, Entity)
        - **엣지(Edge)**: 노드 간의 관계 (CONTAINS, FROM)
        - **속성(Property)**: 각 노드와 엣지에 저장된 키-값 데이터
        - **라벨(Label)**: 노드의 타입을 구분하는 분류자
        
        **RDF/SPARQL과의 차이점:**
        - RDF: 트리플(주어-술어-목적어) 기반, SPARQL 쿼리
        - Property Graph: 노드-엣지 기반, OpenCypher 쿼리
        """)
        
        # 그래프 구조 설명 (맨 위로 이동)
        st.markdown("## 🕸️ GraphRAG 구조")
        
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
        
        st.markdown("#### 🎯 왜 이 두 관계만 있을까?")
        st.info("""
        **GraphRAG의 설계 목적: 빠른 문서 검색**
        
        **1. 단순한 계층 구조**
        ```
        Document (원본 문서)
            ↓ FROM
        Chunk (문서 조각)
            ↓ CONTAINS  
        Entity (핵심 개념)
        ```
        
        **2. AWS Bedrock Knowledge Base의 제약**
        - RAG(검색 증강 생성)에 특화된 시스템
        - Entity 간 복잡한 관계(예: Entity ↔ Entity)는 지원하지 않음
        - 문서 → 청크 → 엔티티의 단방향 흐름만 지원
        
        **3. 검색 최적화**
        - 사용자 질문 → 관련 Entity 찾기 → Entity가 포함된 Chunk 검색 → 원본 Document 추적
        - 복잡한 관계보다는 **빠른 검색 속도**가 우선
        
        **FSS 온톨로지와의 차이점:**
        - FSS: 개념 간 복잡한 의미적 관계 모델링 (SPARQL)
        - GraphRAG: 빠른 문서 검색에 집중 (OpenCypher)
        """)

        st.markdown("### 🔍 GraphRAG 검색 과정")
        st.markdown("""
        **단순한 관계 구조가 빠른 검색을 가능하게 합니다:**
        
        1. **질문 입력** → 사용자가 "파이프 규정" 질문
        2. **Entity 매칭** → "pipe" Entity 식별
        3. **Chunk 검색** → CONTAINS 관계로 관련 Chunk 찾기
        4. **Document 추적** → FROM 관계로 원본 문서 확인
        5. **결과 제공** → 답변과 원본 이미지 표시
        
        **이 과정에서 복잡한 Entity 간 관계는 필요하지 않습니다.**
        """)

        st.markdown("---")
        
        # 11개 문서 목록
        st.markdown("## 📄 Documents")
        st.markdown("**선박 소방 규정 관련 11개 문서**")
        
        # Plan-Execute Agent에서 실제 사용하는 11개 문서
        documents = [
            {"번호": "1", "문서명": "DNV-RU-SHIP-Pt4 Ch6", "설명": "DNV 선급 규칙 - Fire Safety Systems"},
            {"번호": "2", "문서명": "DNV-RU-SHIP-Pt6 Ch5 Sec4", "설명": "DNV 선급 규칙 - Safety Equipment"},
            {"번호": "3", "문서명": "Design guidance - Spoolcutting", "설명": "설계 가이드 - 스풀 절단"},
            {"번호": "4", "문서명": "Design guidance - Support Systems", "설명": "설계 가이드 - 지지 시스템"},
            {"번호": "5", "문서명": "Design guidance - Hull Penetration", "설명": "설계 가이드 - 선체 관통부"},
            {"번호": "6", "문서명": "SOLAS Chapter II-2", "설명": "해상인명안전협약 - Fire Protection & Detection"},
            {"번호": "7", "문서명": "FSS Code", "설명": "국제 화재 안전 시스템 코드"},
            {"번호": "8", "문서명": "IGC Code", "설명": "국제 가스 운반선 안전 코드"},
            {"번호": "9", "문서명": "SOLAS Insulation Penetration Guidelines", "설명": "SOLAS 단열재 관통 가이드라인"},
            {"번호": "10", "문서명": "Piping Practice - Support Systems", "설명": "배관 실무 - 지지 시스템"},
            {"번호": "11", "문서명": "Piping Practice - Hull Penetration", "설명": "배관 실무 - 선체 관통부"}
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
            **실제 Neptune Analytics 키워드 기반 분류 결과:**
            - **시스템 관련 (224개)**: insulation system, containment system, membrane cargo containment systems, gas fuel piping systems, vent piping system 등
            - **규정/챕터 (206개)**: chapter 19, chapter 9, chapter, part 4 chapter 6 section 1, SOLAS chapter ii-2, FSS code 등
            - **파이프 시스템 (141개)**: pipe insulation, pipe spacing, pipe lengths, longitudinally welded pipes, seamless pipes 등
            - **탱크 관련 (139개)**: cargo tank shell, semi-membrane tank, spherical tank construction, pressure type tank, gas tanker 등
            - **화재 안전 (109개)**: fire pumps, fire main, fire detection, firefighting systems, fire safety systems code 등
            - **밸브 시스템 (72개)**: pressure relief valve, relief valve, cargo tank valves, emergency shutdown valves, PRV 등
            - **펌프 시스템 (59개)**: fire pumps, pump housings, circulating pumps, thermal oil circulation pumps, cargo pump rooms 등
            - **안전 시스템 (23개)**: fire safety systems code, international code for fire safety systems, fire safety systems 등
            
            **참고**: 총 5,010개 엔티티 중 키워드 매칭된 항목만 표시. 실제 Neptune Analytics에서 2024년 11월 확인된 데이터입니다.
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
            
            st.metric("CONTAINS", "9,418개", help="Chunk → Entity")
            st.markdown("**의미**: 청크가 엔티티를 포함")
            st.markdown("**예시**: 특정 청크 → pipe, tank, valve 등")
            
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
        
        # 1. 온톨로지 통계
        st.markdown("## 📊 통계")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("총 트리플", "653개 ✅")
        with col2:
            st.metric("총 클래스", "42개 ✅")
        with col3:
            st.metric("총 인스턴스", "186개 ✅")
        with col4:
            st.metric("총 프로퍼티", "69개 ✅")
        with col5:
            st.metric("FSS 챕터", "17개 ✅")
        
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
        체계적으로 표현하기 위한 시맨틱 웹 온톨로지입니다.
        
        653개 트리플과 42개 클래스로 구성되어 
        선박 소방 시스템의 복잡한 관계와 규칙을 기계가 이해할 수 있도록 표현합니다.
        """)
        
        st.info("""
        **📝 참고:** FSS 온톨로지는 RDFS(RDF Schema) 기반입니다.  
        RDF는 트리플만 저장하지만, RDFS는 클래스와 계층 구조를 추가해 의미적 검색을 가능하게 합니다.
        """)
        
        # 3. RDF/RDFS 기본 개념
        st.markdown("## 📚 RDF/RDFS 기본 개념")
        
        st.markdown("""
        **RDF 기본 요소:**
        - **리소스(Resource)**: URI로 식별되는 표현 대상 개체
        - **속성(Property)**: 자원 간 관계를 나타내는 술어(Predicate) - rdf:type, hasComponent 등
        - **값(Value)**: 속성의 값 (다른 리소스 또는 리터럴)
        - **트리플(Triple)**: 주어-술어-목적어 구조의 기본 데이터 단위
        
        **RDFS 추가 요소:**
        - **클래스(Class)**: 개념의 분류 또는 타입 (ExtinguishingSystem, FireSystem 등)
        - **인스턴스(Instance)**: 클래스의 구체적인 예 (CO2System, Chapter5 등)
        - **계층 구조**: rdfs:subClassOf로 클래스 간 상하 관계 정의
        - **제약 조건**: rdfs:domain, rdfs:range로 속성 사용 규칙 정의
        """)
        
        st.code("""
RDF 예시: "CO2System은 hasComponent 관계로 CO2_Valve를 가진다"
-> 주어(Subject): CO2System
-> 술어(Predicate): hasComponent (순수 RDF 트리플)
-> 목적어(Object): CO2_Valve

RDFS 예시: "ExtinguishingSystem은 FireSystem의 하위클래스다"
-> 주어(Subject): ExtinguishingSystem
-> 술어(Predicate): rdfs:subClassOf (RDFS 클래스 계층 관계)
-> 목적어(Object): FireSystem
        """, language="text")
        

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
        
        st.markdown("### 🔗 주요 속성(Property) 예시")
        st.code("""
# 트리플의 술어 위치에 오는 속성들 (28개)
- rdf:type: 인스턴스와 클래스 관계
- hasComponent: 시스템이 구성요소를 포함
- locatedIn: 장비가 특정 위치에 설치
- compliesWith: 규정 준수 관계
- connectedTo: 물리적 연결 관계
- requiresTest: 시험 요구사항 연결
- hasCapacity: 용량 및 성능 속성
        """, language="text")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🏷️ 클래스 예시**")
            st.code("""
# 개념의 분류
Chapter
ExtinguishingSystem
ProtectedSpace
Capacity
            """, language="text")
        
        with col2:
            st.markdown("**📦 인스턴스 예시**")
            st.code("""
# 구체적인 예 (주어/목적어 위치)
Chapter5
CO2System
CargoSpace
CO2_Pressure
            """, language="text")
        
        with col3:
            st.markdown("**🔗 속성(Property) 예시**")
            st.code("""
# 트리플의 술어 위치
rdf:type
detailsSystem
appliesTo
hasSpecification
hasComponent
            """, language="text")

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
|-- [detailsSystem]
    |-- CO2System : ExtinguishingSystem
        |-- [appliesTo]
        |   |-- CargoSpace : ProtectedSpace
        |   |-- MachinerySpace : ProtectedSpace
        |   |-- RoRoSpace : ProtectedSpace
        |-- [hasSpecification]
            |-- CO2_CargoVolPercentage : Capacity
            |-- CO2_MachineryVolPercentage : Capacity
            |-- CO2_Pressure : Pressure
            |-- CO2_Temperature : Temperature
            |-- CO2_DischargeTime : Performance
            |-- CO2_Controls : Control

Chapter6 (Fixed foam fire-extinguishing system)
|-- [detailsSystem]
    |-- HighExpansionFoamSystem : ExtinguishingSystem
        |-- [appliesTo]
        |   |-- CargoSpace : ProtectedSpace
        |   |-- MachinerySpace : ProtectedSpace
        |   |-- RoRoSpace : ProtectedSpace
        |-- [hasSpecification]
            |-- DeckHeightSpec : Specification
            |-- FoamGeneratorClearance : Performance
            |-- HighFoam_FillingTime : Performance

Chapter7 (Water-spraying systems)
|-- [detailsSystem]
    |-- WaterSprayingSystem : ExtinguishingSystem
        |-- [appliesTo]
            |-- MachinerySpace : ProtectedSpace
        """, language="text")
        
        # 실제 예시로 설명
        st.markdown("""
        **4단계 계층 구조로 정보가 연결됩니다:**
        """)
        
        st.code("""
1단계: 클래스 정의
   Chapter (클래스) ← "챕터"라는 개념
   
2단계: 인스턴스 생성
   Chapter5 (인스턴스) ← Chapter 클래스의 구체적 예
   rdf:type -> Chapter
   rdfs:label -> "Chapter 5 Fixed gas fire-extinguishing systems"
   
3단계: 프로퍼티로 연결
   Chapter5 --[detailsSystem]--> CO2System
   (Chapter5가 CO2System을 다룬다)
   
4단계: 하위 구조 확장
   CO2System --[appliesTo]--> CargoSpace
   CO2System --[hasSpecification]--> CO2_Pressure
   CO2System --[hasSpecification]--> CO2_Temperature
   
5단계: 구체적 값
   CO2_Pressure --[value]--> "15 bar"
   CO2_Temperature --[value]--> "-18C"
        """, language="text")
        
        st.markdown("""
        **이렇게 트리플들이 연결되어 복잡한 규정 구조를 표현합니다.**
        - 총 653개의 트리플이 이런 방식으로 연결되어 있습니다
        - 42개 클래스, 186개 인스턴스가 서로 관계를 맺고 있습니다
        """)
        



        st.markdown("""
        **각 화살표는 프로퍼티(관계)를 나타내며, 이를 통해 정보가 연결됩니다.**
        - Chapter5 -> `detailsSystem` -> CO2System
        - CO2System -> `appliesTo` -> CargoSpace
        - CO2System -> `hasSpecification` -> CO2_Pressure, CO2_Temperature
        """)
        
        st.markdown("---")
        
# 전역 인스턴스
schema_explorer = DataSchemaExplorer()