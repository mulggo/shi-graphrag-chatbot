# 데이터 구조 안내서 문서

## 개요

데이터 구조 안내서는 선박 소방 규정 챗봇의 기본 데이터 아키텍처를 사용자가 이해할 수 있도록 돕는 대화형 문서 기능입니다. Neptune Analytics(GraphRAG)와 Neptune DB(SPARQL) 데이터 구조에 대한 포괄적인 정보를 접근 가능한 형식으로 제공합니다.

## 목적

이 가이드는 여러 대상을 위해 제공됩니다:
- **최종 사용자**: 시스템이 정보를 구성하고 검색하는 방법 이해
- **개발자**: 시스템 유지보수 및 확장을 위한 기술 구조 학습
- **데이터 분석가**: 데이터 모델 및 관계 탐색
- **시스템 관리자**: 데이터 통계 및 시스템 상태 모니터링

## 구현

**파일**: `data_structure_guide.py`

**클래스**: `DataSchemaExplorer`

### 주요 구성 요소

```python
class DataSchemaExplorer:
    """데이터 구조 안내서 클래스"""
    
    def render_schema_explorer(self):
        """탭 인터페이스를 사용한 메인 렌더링 함수"""
        tab1, tab2 = st.tabs([
            "📚 GraphRAG", 
            "🕸️ GraphDB"
        ])
```

## 사용자 인터페이스

### 탭 구조

가이드는 두 개의 탭 인터페이스를 사용합니다:

1. **📚 GraphRAG 탭**: Neptune Analytics 구조 및 통계
2. **🕸️ GraphDB 탭**: Neptune SPARQL 온톨로지 세부사항

### 접근 방법

사용자는 사이드바를 통해 가이드에 접근합니다:

```python
# ui/sidebar.py에서
if st.button("📊 데이터 구조 안내서", use_container_width=True):
    st.session_state.show_data_schema = True
    st.rerun()
```

## GraphRAG 탭 (Neptune Analytics)

### 개요 섹션

**목적**: Knowledge Base 개념을 쉬운 용어로 설명

**내용**:
- 쉬운 이해를 위한 도서관 비유
- 데이터 소스 정보 (Neptune Analytics)
- 쿼리 언어 (OpenCypher)
- 목적 및 기능

```python
def _render_kb_explanation(self):
    """Knowledge Base 쉬운 설명"""
    st.markdown("## 📚 GraphRAG (Knowledge Base)")
    st.markdown("""
    **Knowledge Base는 마치 도서관과 같습니다.**
    선박 소방 규정 문서들을 컴퓨터가 빠르게 찾을 수 있도록 정리해둔 곳입니다.
    """)
```

### 그래프 구조 섹션

**노드 구성**:
- **총 노드 수**: 7,552개
  - Document (11개): 원본 PDF 문서
  - Chunk (2,531개): 문서 조각
  - Entity (5,010개): 추출된 개념

**엣지 구성**:
- **총 관계 수**: 11,949개
  - CONTAINS (9,418개): Chunk → Entity
  - FROM (2,531개): Chunk → Document

**시각적 표시**:
```python
# 노드와 엣지를 위한 2열 레이아웃
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 노드(Node) 구성")
    # 노드 통계 및 라벨 테이블
    
with col2:
    st.markdown("### 🔗 엣지(Edge) 구성")
    # 엣지 통계 및 유형 테이블
```

### 검색 과정 섹션

**목적**: 시스템이 정보를 검색하는 방법 설명

**단계**:
1. **질문 입력** → 사용자가 질문
2. **의미 분석** → AI가 질문 이해
3. **문서 검색** → 관련 문서 찾기
4. **점수 계산** → 관련도 점수 부여
5. **결과 제공** → 답변과 원본 이미지 제공

### 문서 목록 섹션

**목적**: Knowledge Base의 모든 11개 문서 표시

**형식**:
```python
documents = [
    {"번호": "1", "문서명": "FSS 합본", "설명": "국제 화재 안전 시스템 코드"},
    {"번호": "2", "문서명": "SOLAS Chapter II-2", "설명": "해상인명안전협약"},
    # ... 더 많은 문서
]
df_documents = pd.DataFrame(documents)
st.dataframe(df_documents, use_container_width=True, hide_index=True)
```

**문서 목록**:
1. FSS 합본 (국제 화재 안전 시스템 코드)
2. SOLAS Chapter II-2
3. SOLAS 2017 Insulation penetration
4. IGC Code (국제 가스 운반선 코드)
5. DNV-RU-SHIP Pt.6 Ch.7 (화재 안전)
6. DNV-RU-SHIP Pt.6 Ch.8 (화재 감지 및 경보)
7. DNV-RU-SHIP Pt.6 Ch.9 (소화)
8. DNV-RU-SHIP Pt.6 Ch.10 (화재 방호)
9. DNV-RU-SHIP Pt.6 Ch.11 (탈출 경로)
10. DNV-RU-SHIP Pt.6 Ch.12 (헬리콥터 시설)
11. DNV-RU-SHIP Pt.6 Ch.13 (운영 요구사항)

## GraphDB 탭 (Neptune SPARQL)

### FSS 온톨로지 섹션

**목적**: SPARQL 기반 온톨로지 구조 설명

**내용**:
- RDF 트리플 구조 설명
- 온톨로지 클래스 계층구조
- 인스턴스 관계
- SPARQL 쿼리 예제

```python
def _render_fss_ontology(self):
    """FSS 온톨로지 설명"""
    st.markdown("## 🕸️ GraphDB (FSS Ontology)")
    st.markdown("""
    **SPARQL 기반 의미론적 온톨로지**
    FSS(Fire Safety Systems) 규정의 구조화된 지식 표현입니다.
    """)
```

### 온톨로지 통계

**구조**:
- **총 트리플 수**: 653개 RDF 트리플
- **클래스**: 42개 온톨로지 클래스
- **인스턴스**: 186개 구체적 인스턴스
- **FSS 챕터**: 17개 구조화된 챕터

### RDF 트리플 설명

**목적**: 사용자가 RDF 구조를 이해하도록 돕기

**형식**: 주어 - 술어 - 목적어

**예제**:
```
fss:Chapter1 rdf:type fss:FireSafetyChapter
fss:Chapter1 fss:hasTitle "General"
fss:Chapter1 fss:contains fss:Section1_1
```

### SPARQL 쿼리 예제

**목적**: 온톨로지를 쿼리하는 방법 표시

**기본 쿼리**:
```sparql
PREFIX fss: <http://www.semanticweb.org/fss#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-schema#>

SELECT ?chapter ?title
WHERE {
    ?chapter rdf:type fss:FireSafetyChapter .
    ?chapter fss:hasTitle ?title .
}
```

## 데이터 시각화

### 테이블 및 DataFrame

가이드는 구조화된 데이터 표시를 위해 Pandas DataFrame을 사용합니다:

```python
import pandas as pd

# 노드 라벨 테이블
labels = [
    {"라벨": "Document", "개수": "11개", "설명": "원본 PDF 문서"},
    {"라벨": "Chunk", "개수": "2,531개", "설명": "문서의 작은 조각"},
    {"라벨": "Entity", "개수": "5,010개", "설명": "추출된 핵심 개념"}
]
df_labels = pd.DataFrame(labels)
st.dataframe(df_labels, use_container_width=True, hide_index=True)
```

### 통계 표시

**메트릭**:
- 유형별 노드 수
- 관계별 엣지 수
- 문서 수
- 트리플 수
- 클래스 및 인스턴스 수

### 시각적 포맷팅

**색상 코딩**:
- 중요 정보를 위한 정보 박스
- 통계를 위한 성공 박스
- 제한사항을 위한 경고 박스
- 문제를 위한 오류 박스

```python
st.info("""
**데이터 출처:** Neptune Analytics (OpenCypher 엔드포인트)  
**그래프 DB:** Knowledge Graph 기반 RAG
**쿼리 언어:** OpenCypher
""")
```

## 메인 애플리케이션과의 통합

### 세션 상태 관리

```python
# app.py에서
if st.session_state.get('show_data_schema', False):
    from data_structure_guide import schema_explorer
    schema_explorer.render_schema_explorer()
```

### 네비게이션 흐름

1. 사용자가 사이드바에서 "📊 데이터 구조 안내서" 클릭
2. `show_data_schema` 플래그가 True로 설정됨
3. 채팅 인터페이스가 숨겨짐
4. 데이터 구조 안내서가 표시됨
5. 사용자가 닫기를 눌러 채팅으로 돌아갈 수 있음

### 닫기 버튼

```python
if st.button("❌ 닫기", use_container_width=True):
    st.session_state.show_data_schema = False
    st.rerun()
```

## 기술 세부사항

### 데이터 소스

**Neptune Analytics**:
- Graph ID: `g-gqisj8edd6`
- 리전: `us-west-2`
- 쿼리 언어: OpenCypher
- 목적: 문서-엔티티 관계

**Neptune SPARQL**:
- 엔드포인트: `shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com`
- 포트: 8182
- 쿼리 언어: SPARQL 1.1
- 목적: 의미론적 온톨로지

### 성능 고려사항

**캐싱**:
- 정적 콘텐츠가 캐시됨
- 통계는 세션당 한 번 계산됨
- 실시간 쿼리 없음 (사전 계산된 값 사용)

**지연 로딩**:
- 가이드 콘텐츠는 접근할 때만 로드됨
- 초기 페이지 로드 시간 감소
- 전체 애플리케이션 성능 향상

## 사용 사례

### 최종 사용자용

1. **검색 결과 이해**: 시스템이 정보를 찾는 방법 학습
2. **문서 발견**: 사용 가능한 문서 확인
3. **시스템 투명성**: 답변 뒤의 데이터 이해
4. **학습 리소스**: 시스템에 대한 교육 콘텐츠

### 개발자용

1. **시스템 문서화**: 데이터 구조에 대한 기술 참조
2. **쿼리 개발**: 쿼리 작성을 위한 예제
3. **데이터 모델 이해**: 그래프 스키마 학습
4. **디버깅**: 데이터 구조 및 통계 확인

### 데이터 분석가용

1. **데이터 탐색**: 사용 가능한 데이터 이해
2. **관계 분석**: 데이터가 연결되는 방법 학습
3. **통계 검토**: 데이터 증가 및 분포 모니터링
4. **쿼리 계획**: 분석 쿼리 계획

## 모범 사례

### 콘텐츠 업데이트

가이드를 업데이트할 때:
1. 설명을 간단하고 접근 가능하게 유지
2. 복잡한 개념에 비유 사용
3. 시각적 예제 제공
4. 실제 통계 포함
5. 새 문서 추가 시 문서 목록 업데이트

### 사용자 경험

1. **점진적 공개**: 간단하게 시작하여 점진적으로 세부사항 추가
2. **시각적 계층구조**: 헤더와 포맷팅을 효과적으로 사용
3. **대화형 요소**: 테이블 및 확장 가능한 섹션
4. **명확한 네비게이션**: 가이드를 쉽게 찾고 돌아올 수 있음

### 유지보수

1. **정기 업데이트**: 통계를 최신 상태로 유지
2. **정확성**: 모든 숫자와 예제 확인
3. **일관성**: 실제 시스템 동작과 일치
4. **문서화**: 향후 유지보수자를 위한 코드 주석

## 향후 개선사항

### 계획된 기능

1. **실시간 통계**: Neptune에서 실제 카운트 쿼리
2. **대화형 다이어그램**: 시각적 스키마 표현
3. **샘플 쿼리**: 실행 가능한 쿼리 예제
4. **데이터 품질 메트릭**: 데이터 완전성 및 품질 표시
5. **내보내기 기능**: 스키마 문서 다운로드
6. **검색 기능**: 가이드 내 검색
7. **버전 히스토리**: 시간에 따른 스키마 변경 추적

### 기술 개선사항

1. **동적 콘텐츠**: 실제 데이터에서 콘텐츠 생성
2. **성능 모니터링**: 쿼리 성능 통계 표시
3. **데이터 계보**: 데이터 흐름 및 변환 표시
4. **스키마 검증**: 스키마 일관성 확인
5. **자동 업데이트**: 데이터 변경 시 자동 업데이트

## 문제 해결

### 일반적인 문제

**가이드가 표시되지 않음**:
- 세션 상태 플래그 확인
- import 문 확인
- 콘솔에서 Python 오류 확인

**잘못된 통계**:
- 하드코딩된 값 업데이트
- Neptune 연결 확인
- 쿼리 결과 확인

**포맷팅 문제**:
- Markdown 구문 확인
- DataFrame 렌더링 확인
- 다른 브라우저에서 테스트

## 참고 자료

- **Neptune Analytics 문서**: https://docs.aws.amazon.com/neptune-analytics/
- **Neptune SPARQL 문서**: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-api.html
- **Streamlit DataFrames**: https://docs.streamlit.io/library/api-reference/data/st.dataframe
- **Pandas 문서**: https://pandas.pydata.org/docs/
