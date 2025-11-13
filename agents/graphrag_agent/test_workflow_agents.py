"""
Test script for Workflow Agents

This script tests the three workflow agents to ensure they are properly implemented.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.graphrag_agent.workflow_agents import (
    QueryAnalysisAgent,
    RetrievalAgent,
    SynthesisAgent
)
from agents.graphrag_agent.prompts import get_prompt_by_agent_type


def test_query_analysis_agent():
    """Test QueryAnalysisAgent initialization and structure"""
    print("=" * 80)
    print("Testing QueryAnalysisAgent")
    print("=" * 80)
    
    try:
        # Get prompt
        prompt = get_prompt_by_agent_type("query_analysis")
        print(f"✓ Prompt loaded: {len(prompt)} characters")
        
        # Initialize agent
        agent = QueryAnalysisAgent(system_prompt=prompt)
        print(f"✓ Agent initialized")
        print(f"  - System prompt length: {len(agent.system_prompt)}")
        print(f"  - Tools available: {len(agent.tools)}")
        
        # Check methods
        assert hasattr(agent, 'analyze'), "Missing analyze method"
        print(f"✓ analyze() method exists")
        
        # Check helper methods
        assert hasattr(agent, '_determine_document_categories'), "Missing _determine_document_categories"
        assert hasattr(agent, '_generate_search_params'), "Missing _generate_search_params"
        print(f"✓ Helper methods exist")
        
        print("\n✓ QueryAnalysisAgent: PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n✗ QueryAnalysisAgent: FAILED - {str(e)}\n")
        return False


def test_retrieval_agent():
    """Test RetrievalAgent initialization and structure"""
    print("=" * 80)
    print("Testing RetrievalAgent")
    print("=" * 80)
    
    try:
        # Get prompt
        prompt = get_prompt_by_agent_type("kb_retrieval")
        print(f"✓ Prompt loaded: {len(prompt)} characters")
        
        # Initialize agent
        agent = RetrievalAgent(system_prompt=prompt)
        print(f"✓ Agent initialized")
        print(f"  - System prompt length: {len(agent.system_prompt)}")
        print(f"  - Tools available: {len(agent.tools)}")
        
        # Check methods
        assert hasattr(agent, 'retrieve'), "Missing retrieve method"
        print(f"✓ retrieve() method exists")
        
        # Check helper methods
        assert hasattr(agent, '_construct_search_query'), "Missing _construct_search_query"
        assert hasattr(agent, '_evaluate_search_quality'), "Missing _evaluate_search_quality"
        assert hasattr(agent, '_enrich_chunks'), "Missing _enrich_chunks"
        print(f"✓ Helper methods exist")
        
        print("\n✓ RetrievalAgent: PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n✗ RetrievalAgent: FAILED - {str(e)}\n")
        return False


def test_synthesis_agent():
    """Test SynthesisAgent initialization and structure"""
    print("=" * 80)
    print("Testing SynthesisAgent")
    print("=" * 80)
    
    try:
        # Get prompt
        prompt = get_prompt_by_agent_type("response_synthesis")
        print(f"✓ Prompt loaded: {len(prompt)} characters")
        
        # Initialize agent
        agent = SynthesisAgent(system_prompt=prompt)
        print(f"✓ Agent initialized")
        print(f"  - System prompt length: {len(agent.system_prompt)}")
        print(f"  - Model ID: {agent.model_id}")
        
        # Check methods
        assert hasattr(agent, 'synthesize'), "Missing synthesize method"
        print(f"✓ synthesize() method exists")
        
        # Check helper methods
        assert hasattr(agent, '_prepare_context'), "Missing _prepare_context"
        assert hasattr(agent, '_generate_response'), "Missing _generate_response"
        assert hasattr(agent, '_format_references'), "Missing _format_references"
        assert hasattr(agent, '_assess_quality'), "Missing _assess_quality"
        print(f"✓ Helper methods exist")
        
        print("\n✓ SynthesisAgent: PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n✗ SynthesisAgent: FAILED - {str(e)}\n")
        return False


def test_helper_methods():
    """Test helper methods with sample data"""
    print("=" * 80)
    print("Testing Helper Methods")
    print("=" * 80)
    
    try:
        # Test QueryAnalysisAgent helpers
        prompt = get_prompt_by_agent_type("query_analysis")
        qa_agent = QueryAnalysisAgent(system_prompt=prompt)
        
        # Test _determine_document_categories
        categories = qa_agent._determine_document_categories(
            message="SOLAS 규정에 따른 CO2 시스템",
            entities=["CO2", "system"],
            keywords_ko=["규정", "시스템"],
            keywords_en=["regulation", "system"],
            related_docs=[]
        )
        assert isinstance(categories, list), "Categories should be a list"
        assert len(categories) > 0, "Should return at least one category"
        print(f"✓ _determine_document_categories: {categories}")
        
        # Test _generate_search_params
        params = qa_agent._generate_search_params("factual", ["규정"])
        assert "num_results" in params, "Should have num_results"
        assert "rerank" in params, "Should have rerank"
        print(f"✓ _generate_search_params: {params}")
        
        # Test RetrievalAgent helpers
        prompt = get_prompt_by_agent_type("kb_retrieval")
        ret_agent = RetrievalAgent(system_prompt=prompt)
        
        # Test _construct_search_query
        query = ret_agent._construct_search_query(["CO2", "system", "capacity"])
        assert isinstance(query, str), "Query should be a string"
        assert len(query) > 0, "Query should not be empty"
        print(f"✓ _construct_search_query: '{query}'")
        
        # Test _evaluate_search_quality
        sample_chunks = [
            {"score": 0.9, "source": "doc1.pdf"},
            {"score": 0.85, "source": "doc2.pdf"},
            {"score": 0.8, "source": "doc3.pdf"}
        ]
        quality = ret_agent._evaluate_search_quality(sample_chunks, {})
        assert quality in ['excellent', 'good', 'fair', 'poor'], "Invalid quality value"
        print(f"✓ _evaluate_search_quality: {quality}")
        
        # Test SynthesisAgent helpers
        prompt = get_prompt_by_agent_type("response_synthesis")
        syn_agent = SynthesisAgent(system_prompt=prompt)
        
        # Test _format_references
        sample_chunks = [
            {
                "source": "s3://bucket/SOLAS_Chapter_II-2.pdf",
                "page": 45,
                "text": "The minimum capacity shall be..."
            }
        ]
        references = syn_agent._format_references(sample_chunks)
        assert isinstance(references, list), "References should be a list"
        assert len(references) == 1, "Should have one reference"
        assert "source_file" in references[0], "Should have source_file"
        assert "page_number" in references[0], "Should have page_number"
        print(f"✓ _format_references: {len(references)} references")
        
        # Test _assess_quality
        confidence, coverage = syn_agent._assess_quality(sample_chunks, "This is a test response.")
        assert confidence in ['high', 'medium', 'low'], "Invalid confidence value"
        assert coverage in ['complete', 'partial', 'limited'], "Invalid coverage value"
        print(f"✓ _assess_quality: confidence={confidence}, coverage={coverage}")
        
        print("\n✓ Helper Methods: PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Helper Methods: FAILED - {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("WORKFLOW AGENTS TEST SUITE")
    print("=" * 80 + "\n")
    
    results = []
    
    # Run tests
    results.append(("QueryAnalysisAgent", test_query_analysis_agent()))
    results.append(("RetrievalAgent", test_retrieval_agent()))
    results.append(("SynthesisAgent", test_synthesis_agent()))
    results.append(("Helper Methods", test_helper_methods()))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:30s} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
