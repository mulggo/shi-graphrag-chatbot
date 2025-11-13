"""
UI 통합 검증 스크립트
Task 11: UI 통합 요구사항 검증

Requirements: 10.5-10.10
"""
import sys
import yaml
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_config_yaml():
    """Test 1: config/agents.yaml 설정 확인"""
    print('=' * 60)
    print('Test 1: config/agents.yaml 설정 확인')
    print('=' * 60)
    
    config_path = project_root / 'config' / 'agents.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    graphrag_config = config['agents'].get('graphrag')
    
    if not graphrag_config:
        print('❌ GraphRAG 에이전트 설정 없음')
        return False
    
    print('✅ GraphRAG 에이전트 설정 존재')
    print(f'  - display_name: {graphrag_config["display_name"]}')
    print(f'  - module_path: {graphrag_config["module_path"]}')
    print(f'  - enabled: {graphrag_config["enabled"]}')
    print(f'  - icon: {graphrag_config["ui_config"]["icon"]}')
    print(f'  - color: {graphrag_config["ui_config"]["color"]}')
    print(f'  - lambda_functions: {list(graphrag_config.get("lambda_function_names", {}).keys())}')
    
    # enabled 확인
    if not graphrag_config['enabled']:
        print('⚠️  경고: GraphRAG 에이전트가 비활성화되어 있습니다')
        return False
    
    print('✅ GraphRAG 에이전트가 활성화되어 있습니다')
    return True

def test_agent_manager():
    """Test 2: AgentManager에 GraphRAG 에이전트 등록 확인"""
    print('\n' + '=' * 60)
    print('Test 2: AgentManager 등록 확인')
    print('=' * 60)
    
    try:
        from core.agent_manager import AgentManager
        manager = AgentManager()
        
        print('✅ AgentManager 초기화 완료')
        print(f'  - 등록된 에이전트: {list(manager.agents.keys())}')
        
        if 'graphrag' not in manager.agents:
            print('❌ GraphRAG 에이전트가 AgentManager에 등록되지 않음')
            return False
        
        print('✅ GraphRAG 에이전트가 AgentManager에 등록됨')
        
        graphrag = manager.agents['graphrag']
        print(f'  - display_name: {graphrag.display_name}')
        print(f'  - enabled: {graphrag.enabled}')
        print(f'  - module_path: {graphrag.module_path}')
        
        # 인스턴스 로드 확인
        if 'graphrag' in manager.agent_instances:
            print('✅ GraphRAG 에이전트 인스턴스 로드됨')
        else:
            print('⚠️  GraphRAG 에이전트 인스턴스가 로드되지 않음 (enabled=false일 수 있음)')
        
        return True
        
    except Exception as e:
        print(f'❌ AgentManager 테스트 실패: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_base_agent_interface():
    """Test 3: BaseAgent 인터페이스 준수 확인"""
    print('\n' + '=' * 60)
    print('Test 3: BaseAgent 인터페이스 준수 확인')
    print('=' * 60)
    
    try:
        from agents.base_agent import BaseAgent
        from agents.graphrag_agent.agent import Agent as GraphRAGAgent
        
        # 상속 확인
        is_subclass = issubclass(GraphRAGAgent, BaseAgent)
        print(f'✅ GraphRAG Agent가 BaseAgent 상속: {is_subclass}')
        
        if not is_subclass:
            print('❌ GraphRAG Agent가 BaseAgent를 상속하지 않음')
            return False
        
        # 필수 메서드 확인
        required_methods = ['process_message', 'log_interaction', 'get_capabilities']
        
        for method in required_methods:
            has_method = hasattr(GraphRAGAgent, method)
            status = '✅' if has_method else '❌'
            print(f'{status} {method} 메서드 존재: {has_method}')
            
            if not has_method:
                return False
        
        print('✅ 모든 필수 메서드가 구현되어 있습니다')
        return True
        
    except Exception as e:
        print(f'❌ BaseAgent 인터페이스 테스트 실패: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_ui_selector_compatibility():
    """Test 4: Streamlit UI에서 에이전트 선택 가능 확인"""
    print('\n' + '=' * 60)
    print('Test 4: UI Selector 호환성 확인')
    print('=' * 60)
    
    try:
        from core.agent_manager import AgentManager
        from ui.agent_selector import AgentSelector
        
        manager = AgentManager()
        selector = AgentSelector(manager)
        
        print('✅ AgentSelector 초기화 완료')
        
        # 사용 가능한 에이전트 목록 확인
        available_agents = manager.get_available_agents()
        print(f'  - 사용 가능한 에이전트 수: {len(available_agents)}')
        
        graphrag_available = any(agent.name == 'graphrag' for agent in available_agents)
        
        if graphrag_available:
            print('✅ GraphRAG 에이전트가 UI 선택 목록에 포함됨')
            
            # UI 설정 확인
            graphrag_agent = next(agent for agent in available_agents if agent.name == 'graphrag')
            print(f'  - UI icon: {graphrag_agent.ui_config.get("icon")}')
            print(f'  - UI color: {graphrag_agent.ui_config.get("color")}')
            print(f'  - Topics: {len(graphrag_agent.ui_config.get("topics", []))}개')
        else:
            print('❌ GraphRAG 에이전트가 UI 선택 목록에 없음')
            return False
        
        return True
        
    except Exception as e:
        print(f'❌ UI Selector 호환성 테스트 실패: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_reference_display_compatibility():
    """Test 5: ReferenceDisplay 호환성 확인"""
    print('\n' + '=' * 60)
    print('Test 5: ReferenceDisplay 호환성 확인')
    print('=' * 60)
    
    try:
        from ui.reference_display import ReferenceDisplay
        
        display = ReferenceDisplay()
        print('✅ ReferenceDisplay 초기화 완료')
        
        # 샘플 참조 데이터 생성 (GraphRAG 에이전트 출력 형식)
        sample_references = [
            {
                'source_file': 'test_document.pdf',
                'page_number': 1,
                'ocr_text': 'Sample OCR text content',
                'image_uri': 's3://test-bucket/test-image.png'
            }
        ]
        
        # render_references 메서드 존재 확인
        has_render = hasattr(display, 'render_references')
        print(f'✅ render_references 메서드 존재: {has_render}')
        
        if not has_render:
            print('❌ ReferenceDisplay에 render_references 메서드가 없음')
            return False
        
        # 메서드 시그니처 확인 (실제 호출은 Streamlit 환경 필요)
        import inspect
        sig = inspect.signature(display.render_references)
        params = list(sig.parameters.keys())
        print(f'  - 메서드 파라미터: {params}')
        
        if 'references' in params:
            print('✅ ReferenceDisplay가 GraphRAG 출력 형식과 호환됨')
        else:
            print('❌ ReferenceDisplay 파라미터가 예상과 다름')
            return False
        
        return True
        
    except Exception as e:
        print(f'❌ ReferenceDisplay 호환성 테스트 실패: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    """모든 UI 통합 테스트 실행"""
    print('\n' + '=' * 60)
    print('GraphRAG Agent UI 통합 검증')
    print('Task 11: UI 통합 (Requirements 10.5-10.10)')
    print('=' * 60 + '\n')
    
    tests = [
        ('config/agents.yaml 설정', test_config_yaml),
        ('AgentManager 등록', test_agent_manager),
        ('BaseAgent 인터페이스', test_base_agent_interface),
        ('UI Selector 호환성', test_ui_selector_compatibility),
        ('ReferenceDisplay 호환성', test_reference_display_compatibility),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f'\n❌ {test_name} 테스트 중 예외 발생: {e}')
            results.append((test_name, False))
    
    # 결과 요약
    print('\n' + '=' * 60)
    print('테스트 결과 요약')
    print('=' * 60)
    
    for test_name, result in results:
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'{status}: {test_name}')
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    print(f'\n총 {total_tests}개 테스트 중 {passed_tests}개 통과')
    
    if passed_tests == total_tests:
        print('\n🎉 모든 UI 통합 테스트 통과!')
        return 0
    else:
        print(f'\n⚠️  {total_tests - passed_tests}개 테스트 실패')
        return 1

if __name__ == '__main__':
    sys.exit(main())
