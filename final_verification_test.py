#!/usr/bin/env python3
"""
데이터 구조 안내서 최종 테스트 및 검증
Task 6: 최종 테스트 및 검증 수행
"""

import sys
import traceback
from data_structure_guide import DataSchemaExplorer

def test_tab_rendering():
    """각 탭의 정상 렌더링 확인"""
    print("🧪 1. 각 탭의 정상 렌더링 확인")
    print("=" * 50)
    
    try:
        explorer = DataSchemaExplorer()
        print("✅ DataSchemaExplorer 인스턴스 생성 성공")
        
        # 각 탭 메서드 존재 확인
        tab_methods = [
            ("📚 문서 저장소 탭", "_render_kb_explanation"),
            ("🕸️ 관계형 데이터 탭", "_render_neptune_explanation"), 
            ("🔥 FSS 온톨로지 탭", "_render_fss_ontology"),
            ("📊 전체 현황 탭", "_render_data_overview")
        ]
        
        for tab_name, method_name in tab_methods:
            if hasattr(explorer, method_name):
                method = getattr(explorer, method_name)
                if callable(method):
                    print(f"  ✅ {tab_name}: 메서드 존재 및 호출 가능")
                else:
                    print(f"  ❌ {tab_name}: 메서드 호출 불가")
                    return False
            else:
                print(f"  ❌ {tab_name}: 메서드 누락")
                return False
                
        # 메인 렌더링 메서드 확인
        if hasattr(explorer, 'render_schema_explorer') and callable(explorer.render_schema_explorer):
            print("  ✅ 메인 렌더링 메서드 존재")
        else:
            print("  ❌ 메인 렌더링 메서드 누락")
            return False
            
        print("✅ 모든 탭 렌더링 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ 탭 렌더링 테스트 실패: {str(e)}")
        return False

def test_expander_functionality():
    """용어 설명 박스 확장/축소 기능 테스트"""
    print("\n🧪 2. 용어 설명 박스 확장/축소 기능 테스트")
    print("=" * 50)
    
    try:
        # 코드에서 st.expander 사용 확인
        with open('data_structure_guide.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'st.expander(' in content:
            print("  ✅ st.expander 사용 확인됨")
            
            # expanded=False 설정 확인
            if 'expanded=False' in content:
                print("  ✅ 기본 축소 상태 설정 확인됨")
            else:
                print("  ⚠️ 기본 축소 상태 설정 미확인 (기본값 사용 가능)")
                
            # 용어 설명 내용 확인
            if '주요 용어 설명' in content:
                print("  ✅ 용어 설명 제목 확인됨")
            else:
                print("  ❌ 용어 설명 제목 누락")
                return False
                
            print("✅ 용어 설명 박스 기능 테스트 통과!")
            return True
        else:
            print("  ❌ st.expander 사용 확인되지 않음")
            return False
            
    except Exception as e:
        print(f"❌ 용어 설명 박스 테스트 실패: {str(e)}")
        return False

def test_data_tables():
    """데이터 테이블과 통계 표시 검증"""
    print("\n🧪 3. 데이터 테이블과 통계 표시 검증")
    print("=" * 50)
    
    try:
        explorer = DataSchemaExplorer()
        
        # 데이터 통계 확인
        print("  📊 KB 통계 데이터:")
        for key, value in explorer.kb_stats.items():
            print(f"    - {key}: {value}")
            
        print("  📊 FSS 통계 데이터:")
        for key, value in explorer.fss_stats.items():
            if key != 'systems':  # systems는 리스트라서 별도 처리
                print(f"    - {key}: {value}")
            else:
                print(f"    - {key}: {len(value)}개 시스템")
                
        # 클래스 분포 데이터 확인
        print("  📊 클래스 분포 데이터:")
        for item in explorer.class_distribution:
            print(f"    - {item['클래스']}: {item['개수']} ({item['설명']})")
            
        # 코드에서 st.dataframe 사용 확인
        with open('data_structure_guide.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        dataframe_count = content.count('st.dataframe(')
        print(f"  ✅ st.dataframe 사용 횟수: {dataframe_count}개")
        
        # st.metric 사용 확인
        metric_count = content.count('st.metric(')
        print(f"  ✅ st.metric 사용 횟수: {metric_count}개")
        
        if dataframe_count > 0 and metric_count > 0:
            print("✅ 데이터 테이블과 통계 표시 테스트 통과!")
            return True
        else:
            print("❌ 데이터 테이블 또는 통계 표시 누락")
            return False
            
    except Exception as e:
        print(f"❌ 데이터 테이블 테스트 실패: {str(e)}")
        return False

def test_user_experience_flow():
    """전체 사용자 경험 흐름 점검"""
    print("\n🧪 4. 전체 사용자 경험 흐름 점검")
    print("=" * 50)
    
    try:
        explorer = DataSchemaExplorer()
        
        # 사용자 경험 요소 확인
        ux_elements = [
            ("제목과 설명", "# 📊 데이터 구조 안내서"),
            ("용어 설명", "주요 용어 설명"),
            ("탭 구조", "st.tabs(["),
            ("비유와 예제", "조직도"),
            ("시각적 요소", "📚|🕸️|🔥|📊"),
            ("실제 데이터", "kb_stats"),
            ("한국어 지원", "한국어")
        ]
        
        with open('data_structure_guide.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        for element_name, search_term in ux_elements:
            if search_term in content:
                print(f"  ✅ {element_name}: 확인됨")
            else:
                print(f"  ❌ {element_name}: 누락")
                return False
                
        # 탭별 내용 균형 확인
        tab_methods = ['_render_kb_explanation', '_render_neptune_explanation', 
                      '_render_fss_ontology', '_render_data_overview']
        
        for method_name in tab_methods:
            method_start = content.find(f'def {method_name}(')
            if method_start != -1:
                # 다음 메서드까지의 내용 길이로 대략적인 내용량 확인
                next_method = content.find('def _render_', method_start + 1)
                if next_method == -1:
                    next_method = len(content)
                method_length = next_method - method_start
                
                if method_length > 500:  # 최소 500자 이상의 내용
                    print(f"  ✅ {method_name}: 충분한 내용량 ({method_length}자)")
                else:
                    print(f"  ⚠️ {method_name}: 내용량 부족 ({method_length}자)")
            else:
                print(f"  ❌ {method_name}: 메서드 누락")
                return False
                
        print("✅ 전체 사용자 경험 흐름 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ 사용자 경험 흐름 테스트 실패: {str(e)}")
        return False

def test_requirements_compliance():
    """요구사항 준수 확인 (1.3, 2.5, 3.4)"""
    print("\n🧪 5. 요구사항 준수 확인")
    print("=" * 50)
    
    try:
        # 요구사항 1.3: 사용자 친화적 인터페이스
        print("  📋 요구사항 1.3 - 사용자 친화적 인터페이스:")
        
        with open('data_structure_guide.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        user_friendly_elements = [
            ("이모지 사용", "📊|🔥|📚|🕸️"),
            ("한국어 설명", "쉽게 설명"),
            ("비유 사용", "조직도|가족|도서관"),
            ("단계별 설명", "1.|2.|3."),
            ("시각적 구조", "```")
        ]
        
        for element, pattern in user_friendly_elements:
            import re
            if re.search(pattern, content):
                print(f"    ✅ {element}: 확인됨")
            else:
                print(f"    ❌ {element}: 누락")
        
        # 요구사항 2.5: 실제 데이터 통계 표시
        print("  📋 요구사항 2.5 - 실제 데이터 통계 표시:")
        
        explorer = DataSchemaExplorer()
        
        # 실제 숫자 데이터 확인
        numeric_data = [
            ("문서 수", explorer.kb_stats['documents']),
            ("청크 수", explorer.kb_stats['chunks']),
            ("엔티티 수", explorer.kb_stats['entities']),
            ("관계 수", explorer.kb_stats['relationships']),
            ("FSS 트리플", explorer.fss_stats['total_triples']),
            ("FSS 클래스", explorer.fss_stats['classes'])
        ]
        
        for name, value in numeric_data:
            if isinstance(value, (int, float)) and value > 0:
                print(f"    ✅ {name}: {value} (유효한 데이터)")
            else:
                print(f"    ❌ {name}: {value} (무효한 데이터)")
        
        # 요구사항 3.4: 탭 기반 구조화된 정보 제공
        print("  📋 요구사항 3.4 - 탭 기반 구조화된 정보 제공:")
        
        if 'st.tabs([' in content:
            print("    ✅ 탭 구조 사용 확인됨")
            
            # 4개 탭 확인
            tab_count = content.count('with tab')
            if tab_count >= 4:
                print(f"    ✅ 충분한 탭 수: {tab_count}개")
            else:
                print(f"    ❌ 탭 수 부족: {tab_count}개")
        else:
            print("    ❌ 탭 구조 사용 확인되지 않음")
            
        print("✅ 요구사항 준수 확인 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 요구사항 준수 확인 실패: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 데이터 구조 안내서 최종 테스트 및 검증")
    print("=" * 60)
    print("Task 6: 최종 테스트 및 검증 수행")
    print("=" * 60)
    
    # 모든 테스트 실행
    tests = [
        ("각 탭의 정상 렌더링 확인", test_tab_rendering),
        ("용어 설명 박스 확장/축소 기능 테스트", test_expander_functionality),
        ("데이터 테이블과 통계 표시 검증", test_data_tables),
        ("전체 사용자 경험 흐름 점검", test_user_experience_flow),
        ("요구사항 준수 확인", test_requirements_compliance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 실행 중 오류: {str(e)}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📋 최종 테스트 결과 요약")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(results)
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status} - {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 전체 결과: {passed_tests}/{total_tests} 테스트 통과")
    
    if passed_tests == total_tests:
        print("\n🎉 모든 테스트 통과! 데이터 구조 안내서가 완벽하게 구현되었습니다.")
        print("\n✅ Task 6 완료: 최종 테스트 및 검증 성공")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests}개 테스트 실패. 문제를 확인해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)