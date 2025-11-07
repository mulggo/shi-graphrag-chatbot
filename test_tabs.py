#!/usr/bin/env python3
"""
데이터 구조 안내서 탭 테스트
"""

from data_structure_guide import DataSchemaExplorer

def test_tabs():
    print("🧪 데이터 구조 안내서 탭 테스트")
    
    try:
        explorer = DataSchemaExplorer()
        print("✅ DataSchemaExplorer 인스턴스 생성 성공")
        
        # 데이터 통계 확인
        print(f"📊 KB 문서: {explorer.kb_stats['documents']}개")
        print(f"📊 KB 청크: {explorer.kb_stats['chunks']:,}개") 
        print(f"📊 KB 엔티티: {explorer.kb_stats['entities']:,}개")
        print(f"📊 FSS 트리플: {explorer.fss_stats['total_triples']}개")
        
        # 메서드 존재 확인
        methods = [
            '_render_kb_explanation',
            '_render_neptune_explanation', 
            '_render_fss_ontology',
            '_render_data_overview'
        ]
        
        for method_name in methods:
            if hasattr(explorer, method_name):
                print(f"✅ {method_name} 메서드 존재")
            else:
                print(f"❌ {method_name} 메서드 누락")
                
        print("✅ 모든 탭 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_tabs()