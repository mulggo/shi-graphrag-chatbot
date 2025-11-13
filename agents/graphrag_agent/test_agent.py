"""
Test script for GraphRAG Agent

이 스크립트는 GraphRAG Agent의 기본 기능을 테스트합니다.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class MockAgentConfig:
    """Mock AgentConfig for testing"""
    name: str = "graphrag"
    display_name: str = "GraphRAG 검색"
    description: str = "지능형 그래프 기반 문서 검색"
    module_path: str = "agents.graphrag_agent.agent"
    bedrock_agent_id: str = ""
    bedrock_alias_id: str = ""
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    knowledge_base_id: str = "ZGBA1R5CS0"
    lambda_function_names: Dict = None
    reranker_model_arn: Optional[str] = None
    ui_config: Optional[Dict] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.lambda_function_names is None:
            self.lambda_function_names = {
                'classify_query': 'arn:aws:lambda:us-west-2:123456789012:function:graphrag-classify-query',
                'extract_entities': 'arn:aws:lambda:us-west-2:123456789012:function:graphrag-extract-entities',
                'kb_retrieve': 'arn:aws:lambda:us-west-2:123456789012:function:graphrag-kb-retrieve'
            }
        if self.ui_config is None:
            self.ui_config = {
                'icon': '🕸️',
                'color': '#9B59B6'
            }


def test_agent_initialization():
    """Test agent initialization"""
    print("=" * 80)
    print("GraphRAG Agent 초기화 테스트")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.agent import Agent
        
        # Create mock config
        config = MockAgentConfig()
        
        # Initialize agent
        print("\n1. Agent 초기화 중...")
        agent = Agent(config)
        print("   ✓ Agent 초기화 성공")
        
        # Check attributes
        print("\n2. Agent 속성 확인...")
        assert agent.name == "graphrag"
        assert agent.display_name == "GraphRAG 검색"
        assert agent.knowledge_base_id == "ZGBA1R5CS0"
        print("   ✓ 기본 속성 확인 완료")
        
        # Check workflow agents
        print("\n3. Workflow Agents 확인...")
        assert hasattr(agent, 'query_analysis_agent')
        assert hasattr(agent, 'retrieval_agent')
        assert hasattr(agent, 'synthesis_agent')
        print("   ✓ 모든 워크플로우 에이전트 초기화됨")
        
        # Check tool context
        print("\n4. ToolContext 확인...")
        assert hasattr(agent, 'tool_context')
        assert agent.tool_context.invocation_state['kb_id'] == "ZGBA1R5CS0"
        print("   ✓ ToolContext 설정 완료")
        
        # Check capabilities
        print("\n5. Capabilities 확인...")
        capabilities = agent.get_capabilities()
        assert len(capabilities) > 0
        assert "지능형 쿼리 분석" in capabilities
        print(f"   ✓ {len(capabilities)}개 기능 확인")
        for cap in capabilities:
            print(f"     - {cap}")
        
        # Check workflow status
        print("\n6. Workflow Status 확인...")
        status = agent.get_workflow_status()
        assert status['agent_name'] == 'graphrag'
        assert status['workflow_agents']['query_analysis']['initialized']
        assert status['workflow_agents']['retrieval']['initialized']
        assert status['workflow_agents']['synthesis']['initialized']
        print("   ✓ 워크플로우 상태 정상")
        
        print("\n" + "=" * 80)
        print("✓ 모든 테스트 통과!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 80)
    print("에러 처리 테스트")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.agent import Agent
        
        config = MockAgentConfig()
        agent = Agent(config)
        
        # Test error classification
        print("\n1. 에러 분류 테스트...")
        
        test_errors = [
            ("Lambda function not found", "lambda_error"),
            ("Request timeout exceeded", "timeout"),
            ("Bedrock KB error", "bedrock_error"),
            ("invocation_state missing", "config_error"),
            ("Unknown error", "unknown")
        ]
        
        for error_msg, expected_type in test_errors:
            error_type = agent._classify_error(error_msg)
            assert error_type == expected_type, f"Expected {expected_type}, got {error_type}"
            print(f"   ✓ '{error_msg[:30]}...' → {error_type}")
        
        # Test user-friendly error messages
        print("\n2. 사용자 친화적 에러 메시지 테스트...")
        
        for error_msg, _ in test_errors:
            friendly_msg = agent._generate_user_friendly_error_message(error_msg)
            assert len(friendly_msg) > 0
            assert "죄송합니다" in friendly_msg
            print(f"   ✓ '{error_msg[:30]}...' → 메시지 생성됨")
        
        print("\n" + "=" * 80)
        print("✓ 에러 처리 테스트 통과!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_response_formatting():
    """Test response formatting"""
    print("\n" + "=" * 80)
    print("응답 포맷팅 테스트")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.agent import Agent
        
        config = MockAgentConfig()
        agent = Agent(config)
        
        # Mock results
        synthesis_results = {
            'content': '테스트 응답입니다.',
            'references': [
                {
                    'source_file': 'test.pdf',
                    'page_number': 1,
                    'ocr_text': 'test text',
                    'image_uri': 's3://bucket/test.pdf'
                }
            ],
            'confidence': 'high',
            'coverage': 'complete'
        }
        
        search_strategy = {
            'question_type': 'factual',
            'document_categories': ['규정']
        }
        
        retrieval_results = {
            'total_retrieved': 5,
            'search_quality': 'excellent',
            'reranked': True
        }
        
        durations = {
            'query_analysis': 1.5,
            'retrieval': 2.3,
            'synthesis': 3.1,
            'total': 6.9
        }
        
        # Format response
        print("\n1. 응답 포맷팅...")
        response = agent._format_response(
            synthesis_results=synthesis_results,
            search_strategy=search_strategy,
            retrieval_results=retrieval_results,
            durations=durations
        )
        
        # Verify response structure
        print("\n2. 응답 구조 검증...")
        assert response['success'] == True
        assert response['content'] == '테스트 응답입니다.'
        assert len(response['references']) == 1
        assert response['agent_name'] == 'graphrag'
        print("   ✓ 기본 구조 확인")
        
        # Verify metadata
        print("\n3. 메타데이터 검증...")
        metadata = response['metadata']
        assert metadata['question_type'] == 'factual'
        assert metadata['total_chunks_retrieved'] == 5
        assert metadata['search_quality'] == 'excellent'
        assert metadata['confidence'] == 'high'
        assert metadata['reranked'] == True
        print("   ✓ 메타데이터 확인")
        
        # Verify durations
        print("\n4. 소요 시간 검증...")
        assert metadata['durations']['total'] == 6.9
        print(f"   ✓ 총 소요 시간: {metadata['durations']['total']}초")
        
        print("\n" + "=" * 80)
        print("✓ 응답 포맷팅 테스트 통과!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "GraphRAG Agent 테스트 스위트" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = []
    
    # Run tests
    results.append(("초기화", test_agent_initialization()))
    results.append(("에러 처리", test_error_handling()))
    results.append(("응답 포맷팅", test_response_formatting()))
    
    # Summary
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 32 + "테스트 요약" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    
    for test_name, passed in results:
        status = "✓ 통과" if passed else "✗ 실패"
        print(f"  {test_name:20s} : {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print("\n" + "=" * 80)
    print(f"결과: {total_passed}/{total_tests} 테스트 통과")
    print("=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if total_passed == total_tests else 1)
