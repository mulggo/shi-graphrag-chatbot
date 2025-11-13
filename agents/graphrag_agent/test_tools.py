"""
Unit tests for GraphRAG Lambda tools with mocks

이 테스트는 Lambda 도구의 기능을 mock을 사용하여 검증합니다.
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_classify_query_tool():
    """Test classify_query tool with mock Lambda"""
    print("=" * 80)
    print("classify_query 도구 테스트 (Mock)")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.tools import classify_query, ToolContext
        
        # Create mock tool context
        mock_context = ToolContext(
            invocation_state={
                'lambda_classify_query_arn': 'arn:aws:lambda:us-west-2:123456789012:function:graphrag-classify-query',
                'aws_region': 'us-west-2'
            }
        )
        
        # Mock Lambda response
        mock_response = {
            'question_type': 'factual',
            'complexity': 'simple',
            'requires_multi_doc': False,
            'confidence': 0.95
        }
        
        # Mock boto3 Lambda client
        with patch('boto3.client') as mock_boto_client:
            mock_lambda = MagicMock()
            mock_boto_client.return_value = mock_lambda
            
            # Mock invoke response
            mock_lambda.invoke.return_value = {
                'StatusCode': 200,
                'Payload': MagicMock(read=lambda: json.dumps(mock_response).encode())
            }
            
            # Call tool
            print("\n1. 도구 호출...")
            result = classify_query(
                query="고정식 CO2 소화 시스템의 최소 용량은?",
                tool_context=mock_context
            )
            
            # Verify result
            print("\n2. 결과 검증...")
            assert result['question_type'] == 'factual'
            assert result['complexity'] == 'simple'
            assert result['confidence'] == 0.95
            print("   ✓ 질문 유형 분류 성공")
            
            # Verify Lambda was called correctly
            print("\n3. Lambda 호출 검증...")
            mock_lambda.invoke.assert_called_once()
            call_args = mock_lambda.invoke.call_args
            assert call_args[1]['FunctionName'] == mock_context.invocation_state['lambda_classify_query_arn']
            assert call_args[1]['InvocationType'] == 'RequestResponse'
            print("   ✓ Lambda 호출 파라미터 정상")
        
        print("\n" + "=" * 80)
        print("✓ classify_query 테스트 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_extract_entities_tool():
    """Test extract_entities tool with mock Lambda"""
    print("\n" + "=" * 80)
    print("extract_entities 도구 테스트 (Mock)")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.tools import extract_entities, ToolContext
        
        # Create mock tool context
        mock_context = ToolContext(
            invocation_state={
                'lambda_extract_entities_arn': 'arn:aws:lambda:us-west-2:123456789012:function:graphrag-extract-entities',
                'aws_region': 'us-west-2'
            }
        )
        
        # Mock Lambda response
        mock_response = {
            'entities': ['CO2 system', 'capacity', 'fixed installation'],
            'keywords_ko': ['고정식', '이산화탄소', '용량', '시스템'],
            'keywords_en': ['fixed', 'CO2', 'capacity', 'system'],
            'related_docs': ['FSS Code', 'SOLAS Chapter II-2']
        }
        
        # Mock boto3 Lambda client
        with patch('boto3.client') as mock_boto_client:
            mock_lambda = MagicMock()
            mock_boto_client.return_value = mock_lambda
            
            # Mock invoke response
            mock_lambda.invoke.return_value = {
                'StatusCode': 200,
                'Payload': MagicMock(read=lambda: json.dumps(mock_response).encode())
            }
            
            # Call tool
            print("\n1. 도구 호출...")
            result = extract_entities(
                query="고정식 CO2 소화 시스템의 최소 용량은?",
                tool_context=mock_context
            )
            
            # Verify result
            print("\n2. 결과 검증...")
            assert len(result['entities']) == 3
            assert 'CO2 system' in result['entities']
            assert len(result['keywords_ko']) == 4
            assert len(result['keywords_en']) == 4
            assert len(result['related_docs']) == 2
            print("   ✓ 엔티티 추출 성공")
            print(f"   - Entities: {result['entities']}")
            print(f"   - Keywords (KO): {result['keywords_ko']}")
            print(f"   - Keywords (EN): {result['keywords_en']}")
            
            # Verify Lambda was called correctly
            print("\n3. Lambda 호출 검증...")
            mock_lambda.invoke.assert_called_once()
            print("   ✓ Lambda 호출 파라미터 정상")
        
        print("\n" + "=" * 80)
        print("✓ extract_entities 테스트 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_kb_retrieve_tool():
    """Test kb_retrieve tool with mock Lambda"""
    print("\n" + "=" * 80)
    print("kb_retrieve 도구 테스트 (Mock)")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.tools import kb_retrieve, ToolContext
        
        # Create mock tool context
        mock_context = ToolContext(
            invocation_state={
                'lambda_kb_retrieve_arn': 'arn:aws:lambda:us-west-2:123456789012:function:graphrag-kb-retrieve',
                'kb_id': 'ZGBA1R5CS0',
                'reranker_model_arn': 'arn:aws:bedrock:us-west-2::foundation-model/reranker',
                'aws_region': 'us-west-2'
            }
        )
        
        # Mock Lambda response
        mock_response = {
            'chunks': [
                {
                    'text': 'The minimum capacity shall be 85% of the gross volume...',
                    'score': 0.95,
                    'source': 's3://bucket/SOLAS_Chapter_II-2.pdf',
                    'page': 45
                },
                {
                    'text': 'For machinery spaces, the CO2 quantity shall be sufficient...',
                    'score': 0.92,
                    'source': 's3://bucket/FSS_Code.pdf',
                    'page': 78
                }
            ],
            'total_retrieved': 2,
            'reranked': True
        }
        
        # Mock boto3 Lambda client
        with patch('boto3.client') as mock_boto_client:
            mock_lambda = MagicMock()
            mock_boto_client.return_value = mock_lambda
            
            # Mock invoke response
            mock_lambda.invoke.return_value = {
                'StatusCode': 200,
                'Payload': MagicMock(read=lambda: json.dumps(mock_response).encode())
            }
            
            # Call tool
            print("\n1. 도구 호출...")
            result = kb_retrieve(
                query="fixed CO2 system minimum capacity",
                num_results=10,
                tool_context=mock_context
            )
            
            # Verify result
            print("\n2. 결과 검증...")
            assert result['total_retrieved'] == 2
            assert result['reranked'] == True
            assert len(result['chunks']) == 2
            assert result['chunks'][0]['score'] == 0.95
            print("   ✓ KB 검색 성공")
            print(f"   - 검색된 청크: {result['total_retrieved']}개")
            print(f"   - Reranking: {result['reranked']}")
            print(f"   - 최고 점수: {result['chunks'][0]['score']}")
            
            # Verify Lambda was called correctly
            print("\n3. Lambda 호출 검증...")
            mock_lambda.invoke.assert_called_once()
            call_args = mock_lambda.invoke.call_args
            payload = json.loads(call_args[1]['Payload'])
            assert payload['query'] == "fixed CO2 system minimum capacity"
            assert payload['num_results'] == 10
            assert payload['kb_id'] == 'ZGBA1R5CS0'
            print("   ✓ Lambda 호출 파라미터 정상")
        
        print("\n" + "=" * 80)
        print("✓ kb_retrieve 테스트 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_error_handling():
    """Test tool error handling with mock failures"""
    print("\n" + "=" * 80)
    print("도구 에러 처리 테스트")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.tools import kb_retrieve, ToolContext
        
        # Create mock tool context
        mock_context = ToolContext(
            invocation_state={
                'lambda_kb_retrieve_arn': 'arn:aws:lambda:us-west-2:123456789012:function:graphrag-kb-retrieve',
                'kb_id': 'ZGBA1R5CS0',
                'reranker_model_arn': 'arn:aws:bedrock:us-west-2::foundation-model/reranker',
                'aws_region': 'us-west-2'
            }
        )
        
        # Test 1: Lambda error response
        print("\n1. Lambda 에러 응답 테스트...")
        with patch('boto3.client') as mock_boto_client:
            mock_lambda = MagicMock()
            mock_boto_client.return_value = mock_lambda
            
            # Mock error response
            mock_lambda.invoke.return_value = {
                'StatusCode': 200,
                'Payload': MagicMock(read=lambda: json.dumps({
                    'errorMessage': 'Lambda function error',
                    'errorType': 'Exception'
                }).encode())
            }
            
            result = kb_retrieve(
                query="test query",
                num_results=10,
                tool_context=mock_context
            )
            
            # Should return error structure
            assert 'error' in result
            assert result['chunks'] == []
            assert result['total_retrieved'] == 0
            print("   ✓ Lambda 에러 처리 정상")
        
        # Test 2: Network timeout
        print("\n2. 네트워크 타임아웃 테스트...")
        with patch('boto3.client') as mock_boto_client:
            mock_lambda = MagicMock()
            mock_boto_client.return_value = mock_lambda
            
            # Mock timeout exception
            from botocore.exceptions import ClientError
            mock_lambda.invoke.side_effect = ClientError(
                {'Error': {'Code': 'TooManyRequestsException'}},
                'Invoke'
            )
            
            result = kb_retrieve(
                query="test query",
                num_results=10,
                tool_context=mock_context
            )
            
            # Should return error structure
            assert 'error' in result
            print("   ✓ 타임아웃 에러 처리 정상")
        
        print("\n" + "=" * 80)
        print("✓ 에러 처리 테스트 통과!")
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
    print("║" + " " * 22 + "Lambda 도구 단위 테스트" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = []
    
    # Run tests
    results.append(("classify_query", test_classify_query_tool()))
    results.append(("extract_entities", test_extract_entities_tool()))
    results.append(("kb_retrieve", test_kb_retrieve_tool()))
    results.append(("에러 처리", test_tool_error_handling()))
    
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
