"""
Prompt quality validation tests

이 테스트는 모든 프롬프트가 Anthropic 9가지 원칙을 준수하는지 검증합니다.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_anthropic_principle_1_clear_instructions():
    """원칙 1: 명확하고 구체적인 지시"""
    print("=" * 80)
    print("원칙 1: 명확하고 구체적인 지시")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.prompts import get_prompt_by_agent_type
        
        agent_types = ['query_analysis', 'kb_retrieval', 'response_synthesis']
        
        for agent_type in agent_types:
            print(f"\n{agent_type} 프롬프트 검증...")
            prompt = get_prompt_by_agent_type(agent_type)
            
            # Check for specific instructions
            assert "<instructions>" in prompt, f"{agent_type}: <instructions> 태그 누락"
            assert "단계별" in prompt or "step" in prompt.lower(), f"{agent_type}: 단계별 지시 누락"
            
            # Check for concrete actions
            concrete_verbs = ["분석", "생성", "검색", "합성", "식별", "결정", "analyze", "generate", "retrieve"]
            has_concrete_verb = any(verb in prompt for verb in concrete_verbs)
            assert has_concrete_verb, f"{agent_type}: 구체적인 동사 누락"
            
            print(f"   ✓ {agent_type}: 명확하고 구체적인 지시 확인")
        
        print("\n" + "=" * 80)
        print("✓ 원칙 1 검증 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 검증 실패: {str(e)}")
        return False


def test_anthropic_principle_2_context():
    """원칙 2: 충분한 맥락 제공"""
    print("\n" + "=" * 80)
    print("원칙 2: 충분한 맥락 제공")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.prompts import get_prompt_by_agent_type
        
        agent_types = ['query_analysis', 'kb_retrieval', 'response_synthesis']
        
        for agent_type in agent_types:
            print(f"\n{agent_type} 프롬프트 검증...")
            prompt = get_prompt_by_agent_type(agent_type)
            
            # Check for context tag
            assert "<context>" in prompt, f"{agent_type}: <context> 태그 누락"
            
            # Check for domain information
            domain_keywords = ["선박", "소방", "규정", "ship", "fire", "regulation", "Knowledge Base"]
            has_domain = any(keyword in prompt for keyword in domain_keywords)
            assert has_domain, f"{agent_type}: 도메인 정보 누락"
            
            # Check for target audience
            audience_keywords = ["사용자", "전문가", "설계자", "엔지니어", "user", "expert"]
            has_audience = any(keyword in prompt for keyword in audience_keywords)
            assert has_audience, f"{agent_type}: 대상 청중 정보 누락"
            
            print(f"   ✓ {agent_type}: 충분한 맥락 제공 확인")
        
        print("\n" + "=" * 80)
        print("✓ 원칙 2 검증 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 검증 실패: {str(e)}")
        return False


def test_anthropic_principle_3_examples():
    """원칙 3: 예시 사용 (멀티샷)"""
    print("\n" + "=" * 80)
    print("원칙 3: 예시 사용 (멀티샷)")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.prompts import get_prompt_by_agent_type
        
        # Query analysis should have examples
        print("\nquery_analysis 프롬프트 검증...")
        prompt = get_prompt_by_agent_type('query_analysis')
        
        # Check for examples section
        assert "<examples>" in prompt, "query_analysis: <examples> 태그 누락"
        assert "<example>" in prompt, "query_analysis: <example> 태그 누락"
        
        # Count examples
        example_count = prompt.count("<example>")
        assert example_count >= 5, f"query_analysis: 예시 부족 (최소 5개 필요, 현재 {example_count}개)"
        print(f"   ✓ query_analysis: {example_count}개 예시 확인")
        
        # Check for input/output structure
        assert "<input>" in prompt, "query_analysis: <input> 태그 누락"
        assert "<answer>" in prompt, "query_analysis: <answer> 태그 누락"
        print(f"   ✓ query_analysis: 입출력 구조 확인")
        
        # Response synthesis should have examples
        print("\nresponse_synthesis 프롬프트 검증...")
        prompt = get_prompt_by_agent_type('response_synthesis')
        
        assert "<examples>" in prompt, "response_synthesis: <examples> 태그 누락"
        example_count = prompt.count("<example>")
        assert example_count >= 3, f"response_synthesis: 예시 부족 (최소 3개 필요, 현재 {example_count}개)"
        print(f"   ✓ response_synthesis: {example_count}개 예시 확인")
        
        print("\n" + "=" * 80)
        print("✓ 원칙 3 검증 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 검증 실패: {str(e)}")
        return False


def test_anthropic_principle_4_thinking():
    """원칙 4: Claude가 생각하게 하기 (사고 연쇄)"""
    print("\n" + "=" * 80)
    print("원칙 4: Claude가 생각하게 하기 (사고 연쇄)")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.prompts import get_prompt_by_agent_type
        
        # Query analysis should encourage thinking
        print("\nquery_analysis 프롬프트 검증...")
        prompt = get_prompt_by_agent_type('query_analysis')
        
        # Check for thinking prompts
        thinking_keywords = ["<thinking>", "추론", "단계별", "생각", "reasoning", "step by step"]
        has_thinking = any(keyword in prompt for keyword in thinking_keywords)
        assert has_thinking, "query_analysis: 사고 연쇄 프롬프트 누락"
        print(f"   ✓ query_analysis: 사고 연쇄 프롬프트 확인")
        
        # Check examples have thinking sections
        if "<thinking>" in prompt:
            thinking_count = prompt.count("<thinking>")
            print(f"   ✓ query_analysis: {thinking_count}개 thinking 섹션 확인")
        
        print("\n" + "=" * 80)
        print("✓ 원칙 4 검증 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 검증 실패: {str(e)}")
        return False


def test_anthropic_principle_5_xml_structure():
    """원칙 5: XML 태그 구조화"""
    print("\n" + "=" * 80)
    print("원칙 5: XML 태그 구조화")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.prompts import get_prompt_by_agent_type
        
        agent_types = ['query_analysis', 'kb_retrieval', 'response_synthesis']
        required_tags = ['<role>', '<task>', '<instructions>', '<output_format>']
        
        for agent_type in agent_types:
            print(f"\n{agent_type} 프롬프트 검증...")
            prompt = get_prompt_by_agent_type(agent_type)
            
            # Check for required XML tags
            for tag in required_tags:
                assert tag in prompt, f"{agent_type}: {tag} 태그 누락"
            
            print(f"   ✓ {agent_type}: 필수 XML 태그 확인")
            
            # Check for proper nesting
            assert prompt.count('<') == prompt.count('>'), f"{agent_type}: XML 태그 불균형"
            print(f"   ✓ {agent_type}: XML 태그 균형 확인")
        
        print("\n" + "=" * 80)
        print("✓ 원칙 5 검증 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 검증 실패: {str(e)}")
        return False


def test_anthropic_principle_6_role():
    """원칙 6: Claude에게 역할 부여"""
    print("\n" + "=" * 80)
    print("원칙 6: Claude에게 역할 부여")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.prompts import get_prompt_by_agent_type
        
        agent_types = ['query_analysis', 'kb_retrieval', 'response_synthesis']
        
        for agent_type in agent_types:
            print(f"\n{agent_type} 프롬프트 검증...")
            prompt = get_prompt_by_agent_type(agent_type)
            
            # Check for role tag
            assert "<role>" in prompt, f"{agent_type}: <role> 태그 누락"
            
            # Check for expertise level
            expertise_keywords = ["전문가", "expert", "specialist", "경력", "years"]
            has_expertise = any(keyword in prompt for keyword in expertise_keywords)
            assert has_expertise, f"{agent_type}: 전문성 수준 명시 누락"
            
            print(f"   ✓ {agent_type}: 역할 및 전문성 확인")
        
        print("\n" + "=" * 80)
        print("✓ 원칙 6 검증 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 검증 실패: {str(e)}")
        return False


def test_anthropic_principle_7_prefill():
    """원칙 7: Claude의 응답 미리 채우기"""
    print("\n" + "=" * 80)
    print("원칙 7: Claude의 응답 미리 채우기")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.prompts import get_prompt_by_agent_type
        
        agent_types = ['query_analysis', 'kb_retrieval', 'response_synthesis']
        
        for agent_type in agent_types:
            print(f"\n{agent_type} 프롬프트 검증...")
            prompt = get_prompt_by_agent_type(agent_type)
            
            # Check for output format guidance
            assert "<output_format>" in prompt, f"{agent_type}: <output_format> 태그 누락"
            
            # Check for prefill instructions
            prefill_keywords = ["다음 형식으로", "시작하세요", "응답을", "format", "start with"]
            has_prefill = any(keyword in prompt for keyword in prefill_keywords)
            assert has_prefill, f"{agent_type}: 응답 미리 채우기 지시 누락"
            
            print(f"   ✓ {agent_type}: 응답 형식 지정 확인")
        
        print("\n" + "=" * 80)
        print("✓ 원칙 7 검증 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 검증 실패: {str(e)}")
        return False


def test_document_coverage_in_examples():
    """11개 문서 커버리지 검증"""
    print("\n" + "=" * 80)
    print("11개 문서 커버리지 검증")
    print("=" * 80)
    
    try:
        from agents.graphrag_agent.prompts import get_prompt_by_agent_type
        
        # 11개 개별 문서 목록
        documents = [
            "FSS 합본",
            "SOLAS Chapter II-2",
            "SOLAS 2017 Insulation penetration",
            "IGC Code",
            "DNV-RU-SHIP Pt4 Ch6",
            "DNV-RU-SHIP Pt6 Ch5 Sec4",
            "Design guidance_Support",
            "Design guidance_Spoolcutting",
            "Design guidance_hull penetration",
            "Piping practice_Support",
            "Piping practice_hull penetration"
        ]
        
        print("\nquery_analysis 프롬프트 예시 검증...")
        prompt = get_prompt_by_agent_type('query_analysis')
        
        # Check if examples cover different documents
        found_documents = []
        for doc in documents:
            if doc in prompt:
                found_documents.append(doc)
        
        print(f"\n발견된 문서: {len(found_documents)}/11개")
        for doc in found_documents:
            print(f"   ✓ {doc}")
        
        if len(found_documents) < 11:
            print(f"\n누락된 문서:")
            for doc in documents:
                if doc not in found_documents:
                    print(f"   ✗ {doc}")
        
        # Should have at least 8 out of 11 documents in examples
        assert len(found_documents) >= 8, f"문서 커버리지 부족 (최소 8개 필요, 현재 {len(found_documents)}개)"
        
        print("\n" + "=" * 80)
        print("✓ 문서 커버리지 검증 통과!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 검증 실패: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "프롬프트 품질 검증 테스트" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = []
    
    # Run Anthropic 9 principles tests
    results.append(("원칙 1: 명확한 지시", test_anthropic_principle_1_clear_instructions()))
    results.append(("원칙 2: 충분한 맥락", test_anthropic_principle_2_context()))
    results.append(("원칙 3: 예시 사용", test_anthropic_principle_3_examples()))
    results.append(("원칙 4: 사고 연쇄", test_anthropic_principle_4_thinking()))
    results.append(("원칙 5: XML 구조화", test_anthropic_principle_5_xml_structure()))
    results.append(("원칙 6: 역할 부여", test_anthropic_principle_6_role()))
    results.append(("원칙 7: 응답 미리 채우기", test_anthropic_principle_7_prefill()))
    results.append(("문서 커버리지", test_document_coverage_in_examples()))
    
    # Summary
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 32 + "테스트 요약" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    
    for test_name, passed in results:
        status = "✓ 통과" if passed else "✗ 실패"
        print(f"  {test_name:30s} : {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print("\n" + "=" * 80)
    print(f"결과: {total_passed}/{total_tests} 테스트 통과")
    print("=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if total_passed == total_tests else 1)
