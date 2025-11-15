"""
데이터 구조 안내서 - 새 버전
선박 소방 규정 챗봇이 사용하는 데이터의 구조와 관계를 보고서 형식으로 설명
"""
import streamlit as st
import pandas as pd

def render_graphrag_report():
    """보고서 형식 GraphRAG 설명"""
    
    # 요약
    st.markdown("# 📊 GraphRAG 데이터 구조 보고서")
    
    st.markdown("## 1. 요약 (Executive Summary)")
    st.success("""
    선박 소방 규정 문서를 빠르게 검색하기 위한 그래프 데이터베이스
    
    11개 PDF 문서 → 2,531개 청크 → 5,010개 엔티티로 구조화하여
    사용자 질문에 관련된 문서를 즉시 찾아 답변을 생성합니다.
    """)
    
    # 데이터 개요
    st.markdown("## 2. 데이터 개요 (Data Overview)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("문서 수", "11개", help="원본 PDF 문서")
    with col2:
        st.metric("청크 수", "2,531개", help="검색 가능 단위")
    with col3:
        st.metric("엔티티 수", "5,010개", help="추출된 핵심 용어")
    with col4:
        st.metric("총 관계 수", "11,949개", help="노드 간 연결")
    
    # AWS GraphRAG 구성 요소
    st.markdown("## 3. AWS GraphRAG 구성 요소 (AWS GraphRAG Components)")
    
    components = pd.DataFrame([
        {"구성요소": "AWS Bedrock Knowledge Base", "역할": "문서 저장 및 벡터 검색", "기능": "PDF 파싱, 청크 분할, 임베딩 생성"},
        {"구성요소": "Amazon Neptune Analytics", "역할": "그래프 데이터베이스", "기능": "노드-엣지 관계 저장, OpenCypher 쿼리"},
        {"구성요소": "AWS Bedrock Agent", "역할": "지능형 질의응답", "기능": "자연어 처리, 추론, 답변 생성"},
        {"구성요소": "Lambda Functions", "역할": "GraphRAG 도구", "기능": "엔티티 추출, 쿼리 분류, 검색 실행"}
    ])
    st.dataframe(components, use_container_width=True, hide_index=True)
    
    # 데이터 처리 개요
    st.markdown("## 4. 데이터 처리 개요 (Data Processing Overview)")
    
    st.markdown("""
    **기본 처리 플로우:**
    PDF 파싱 → 청크 분할 → 임베딩 생성 → 엔티티 추출 → 그래프 구축
    
    **핵심 기술:**
    - AWS Textract: PDF 텍스트 추출
    - Amazon Titan Embeddings: 1536차원 벡터 생성
    - Named Entity Recognition: 선박 도메인 특화 용어 추출
    """)
    
    st.markdown("### 4.2 임베딩 생성 과정")
    st.info("""
    **Amazon Titan Embeddings 모델 사용:**
    - 1536차원 벡터로 의미 표현
    - 선박 도메인 특화 용어 최적화
    - 의미적 유사도 기반 검색 지원
    - 벡터 데이터베이스에 저장되어 빠른 검색 가능
    """)
    
    # 온톨로지 구성 (핵심 섹션)
    st.markdown("## 5. 온톨로지 구성 (Ontology Construction)")
    
    st.markdown("### 5.1 엔티티 추출 과정")
    st.info("""
    **AWS Bedrock Knowledge Base에서 자동 추출된 엔티티:**
    - 선박 구조물: pipe, tank, valve, deck, bulkhead
    - 규정 참조: SOLAS, FSS, IGC, DNV 규칙 번호
    - 기술 사양: 압력, 온도, 재질, 치수
    - 시스템명: fire detection, CO2 system, foam system
    
    **도메인 특화 처리:**
    - 선박 용어 사전 기반 정규화
    - 약어 확장 (FSS → Fire Safety Systems)
    - 다국어 용어 매핑 (한국어 ↔ 영어)
    """)
    
    # 시스템 아키텍처
    st.markdown("## 5. 시스템 아키텍처 (System Architecture)")
    
    st.markdown("### 5.1 데이터 플로우")
    
    # 데이터 플로우 다이어그램
    st.code("""
    📄 Document Layer (11개 문서)
         │
         │ FROM 관계 (2,531개)
         ↓
    📝 Chunk Layer (2,531개 청크)
         │
         │ CONTAINS 관계 (9,418개)
         ↓
    🏷️ Entity Layer (5,010개 엔티티)
    """, language="text")
    
    st.markdown("""
    **계층별 설명:**
    - 📄 **Document Layer**: 원본 PDF 문서 (FSS, SOLAS, IGC 등)
    - 📝 **Chunk Layer**: 검색 가능한 문단 단위 조각
    - 🏷️ **Entity Layer**: 추출된 핵심 용어 (pipe, tank, valve 등)
    """)
    
    st.markdown("### 3.2 기술 스택")
    tech_stack = pd.DataFrame([
        {"구성요소": "Graph Database", "기술": "Amazon Neptune Analytics", "역할": "그래프 데이터 저장 및 쿼리"},
        {"구성요소": "Graph Model", "기술": "Property Graph", "역할": "노드-엣지 기반 데이터 모델링"},
        {"구성요소": "Query Language", "기술": "OpenCypher", "역할": "그래프 쿼리 실행"},
        {"구성요소": "Knowledge Base", "기술": "AWS Bedrock KB", "역할": "RAG 기반 문서 검색"}
    ])
    st.dataframe(tech_stack, use_container_width=True, hide_index=True)
    
    st.markdown("### 5.2 그래프 구조 생성")
    st.markdown("""
    **Property Graph 모델 구축:**
    - Document 노드: 원본 PDF 문서 (11개)
    - Chunk 노드: 문서 조각 (2,531개)
    - Entity 노드: 추출된 핵심 용어 (5,010개)
    - FROM 관계: Chunk → Document (2,531개)
    - CONTAINS 관계: Chunk → Entity (9,418개)
    """)
    
    # 내부 온톨로지 구성
    st.markdown("## 6. 내부 온톨로지 구성 (Internal Ontology Structure)")
    
    st.markdown("### 6.1 GraphRAG vs FSS 온톨로지 비교")
    
    comparison = pd.DataFrame([
        {"구분": "목적", "GraphRAG": "빠른 문서 검색", "FSS 온톨로지": "의미적 관계 모델링"},
        {"구분": "모델", "GraphRAG": "Property Graph", "FSS 온톨로지": "RDF Triple Store"},
        {"구분": "관계 복잡도", "GraphRAG": "단순 (2가지)", "FSS 온톨로지": "복잡 (69가지)"},
        {"구분": "쿼리 언어", "GraphRAG": "OpenCypher", "FSS 온톨로지": "SPARQL"},
        {"구분": "응답 속도", "GraphRAG": "~3초", "FSS 온톨로지": "~10초"}
    ])
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    
    st.markdown("### 6.2 GraphRAG 온톨로지 설계 원칙")
    st.markdown("""
    **단순성 우선 설계:**
    - Entity 간 직접 관계 배제 → 검색 성능 향상
    - 계층적 구조 채택 → 명확한 데이터 흐름
    - 속성 기반 분류 → 복잡한 추론 과정 생략
    
    **선박 도메인 특화:**
    - 시스템별 엔티티 그룹핑 (화재안전, 배관, 구조)
    - 규정 계층 구조 반영 (Chapter → Section → Regulation)
    - 실무 용어 우선 (기술 명세서 용어 기준)
    """)
    
    # 에이전트 구조
    st.markdown("## 7. 에이전트 역할 및 내부 구조 (Agent Architecture)")
    
    st.markdown("### 7.1 Plan-Execute Agent 구조")
    
    # 에이전트 구조 다이어그램
    st.code("""
    사용자 질문 → Plan Agent → Execute Agent → 답변 생성
                        │              │
                   계획 수립      GraphRAG Tools
                                   │
                              • classify_query
                              • extract_entities  
                              • kb_retrieve
    """, language="text")
    
    st.markdown("### 7.2 에이전트별 역할")
    
    agent_roles = pd.DataFrame([
        {"에이전트": "Plan Agent", "역할": "질문 분석 및 검색 전략 수립", "주요 기능": "의도 파악, 검색 키워드 추출, 단계별 계획"},
        {"에이전트": "Execute Agent", "역할": "계획 실행 및 도구 활용", "주요 기능": "GraphRAG 도구 호출, 결과 검증, 재시도 로직"},
        {"에이전트": "Lambda Tools", "역할": "특화된 검색 및 분석", "주요 기능": "엔티티 추출, 쿼리 분류, 지식베이스 검색"}
    ])
    st.dataframe(agent_roles, use_container_width=True, hide_index=True)
    
    st.markdown("### 7.3 Lambda 도구 상세")
    st.markdown("""
    **classify_query**: 질문 유형 분류
    - 기술 질문 vs 규정 질문 vs 절차 질문
    - 적절한 검색 전략 선택
    - 응답 형식 결정
    
    **extract_entities**: 핵심 용어 추출
    - 선박 구조물, 시스템명, 규정 번호 식별
    - 동의어 및 약어 처리
    - 검색 키워드 우선순위 결정
    
    **kb_retrieve**: 지식베이스 검색
    - 벡터 유사도 기반 문서 검색
    - 그래프 관계 기반 연관 문서 탐색
    - 검색 결과 랭킹 및 필터링
    """)
    
    # 설계 원칙
    st.markdown("## 8. 설계 원칙 (Design Principles)")
    
    st.markdown("### 8.1 단순성 우선 (Simplicity First)")
    st.info("""
    **설계 철학**: 복잡한 의미적 관계보다 빠른 검색 성능을 우선  
    **구현 방법**: 3단계 선형 계층 구조 채택  
    **기대 효과**: 평균 3초 이내 응답 시간 달성
    """)
    
    st.markdown("### 8.2 제약 사항 (Constraints)")
    constraints = pd.DataFrame([
        {"제약": "AWS Bedrock KB 한계", "내용": "Entity 간 직접 관계 지원 안함", "대응": "단방향 계층 구조 채택"},
        {"제약": "검색 속도 요구사항", "내용": "3초 이내 응답 필수", "대응": "복잡한 그래프 순회 배제"},
        {"제약": "데이터 규모", "내용": "11개 문서, 7,552개 노드", "대응": "인덱스 최적화 및 캐싱"}
    ])
    st.dataframe(constraints, use_container_width=True, hide_index=True)
    
    # 성능 분석
    st.markdown("## 9. 성능 분석 (Performance Analysis)")
    
    st.markdown("### 9.1 검색 프로세스")
    st.markdown("""
    **단계별 처리 시간:**
    1. Entity 매칭: ~0.1초 (인덱스 기반)
    2. Chunk 검색: ~0.5초 (CONTAINS 관계 순회)
    3. Document 추적: ~0.1초 (FROM 관계 직접 접근)
    4. 답변 생성: ~2.0초 (LLM 처리)
    
    **총 소요 시간: 평균 2.7초**
    """)
    
    st.markdown("### 9.2 데이터 분포")
    distribution = pd.DataFrame([
        {"카테고리": "탱크 관련", "엔티티 수": "144개", "비율": "2.9%"},
        {"카테고리": "파이프 시스템", "엔티티 수": "127개", "비율": "2.5%"},
        {"카테고리": "화재 안전", "엔티티 수": "121개", "비율": "2.4%"},
        {"카테고리": "규정/챕터", "엔티티 수": "126개", "비율": "2.5%"},
        {"카테고리": "기타", "엔티티 수": "4,492개", "비율": "89.7%"}
    ])
    st.dataframe(distribution, use_container_width=True, hide_index=True)
    

    
    # 부록: 상세 데이터
    st.markdown("## 부록: 상세 데이터 (Appendix)")
    
    with st.expander("📄 원본 문서 목록"):
        documents = [
            {"ID": "DOC001", "문서명": "FSS 합본", "설명": "국제 화재 안전 시스템 코드", "청크 수": "450개"},
            {"ID": "DOC002", "문서명": "SOLAS Chapter II-2", "설명": "해상인명안전협약", "청크 수": "380개"},
            {"ID": "DOC003", "문서명": "IGC Code", "설명": "국제 가스 운반선 코드", "청크 수": "290개"},
            {"ID": "DOC004-008", "문서명": "DNV 선급 규칙", "설명": "Part 4 Ch6, Part 6 Ch5 Sec4", "청크 수": "680개"},
            {"ID": "DOC009-011", "문서명": "설계/배관 가이드", "설명": "실무 지침서", "청크 수": "731개"}
        ]
        st.dataframe(pd.DataFrame(documents), use_container_width=True, hide_index=True)
    
    with st.expander("📝 청크 속성 상세"):
        st.markdown("""
        **청크 메타데이터 구조:**
        - `metadata_x-amz-bedrock-kb-source-uri`: S3 원본 문서 경로
        - `AMAZON_BEDROCK_TEXT`: 청크 텍스트 내용
        - `AMAZON_BEDROCK_METADATA`: JSON 메타데이터 (이미지, 컨텍스트)
        - `metadata_x-amz-bedrock-kb-data-source-id`: 데이터 소스 ID
        - `metadata_x-amz-bedrock-kb-document-page-number`: 문서 페이지 번호
        """)
    
    with st.expander("🏷️ 엔티티 분류 상세"):
        entity_details = pd.DataFrame([
            {"카테고리": "탱크 관련", "예시": "tank top, cargo tank, oil fuel tanks", "사용 빈도": "높음"},
            {"카테고리": "파이프 시스템", "예시": "pipe, sampling pipes, stainless steel pipe", "사용 빈도": "높음"},
            {"카테고리": "화재 안전", "예시": "fire safety systems, fire detection", "사용 빈도": "높음"},
            {"카테고리": "규정/챕터", "예시": "SOLAS chapter, FSS code, regulation", "사용 빈도": "중간"},
            {"카테고리": "밸브 시스템", "예시": "relief valves, gas regulation valves", "사용 빈도": "중간"}
        ])
        st.dataframe(entity_details, use_container_width=True, hide_index=True)