"""
GraphRAG 멀티 에이전트 시스템 프롬프트 로더

이 모듈은 prompts/ 디렉토리의 YAML 파일에서 프롬프트를 로드하고 관리합니다.
Anthropic의 9가지 핵심 프롬프트 엔지니어링 원칙을 따르는
세 가지 전문 에이전트의 프롬프트 템플릿을 제공합니다.
"""

import yaml
from typing import Dict, Any
from pathlib import Path


class PromptLoader:
    """YAML 파일에서 프롬프트를 로드하고 관리하는 클래스"""
    
    def __init__(self, prompts_dir: str = None):
        """
        프롬프트 로더 초기화
        
        Args:
            prompts_dir: prompts 디렉토리 경로 (기본값: 현재 디렉토리/prompts)
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent / "prompts"
        
        self.prompts_dir = Path(prompts_dir)
        self._prompts = {}
        self._metadata = None
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """모든 YAML 파일에서 프롬프트 로드"""
        # 메타데이터 로드
        metadata_path = self.prompts_dir / "metadata.yaml"
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self._metadata = yaml.safe_load(f)
        except FileNotFoundError:
            self._metadata = {}
        
        # 각 에이전트 프롬프트 로드
        agent_types = ['query_analysis', 'kb_retrieval', 'response_synthesis']
        for agent_type in agent_types:
            yaml_path = self.prompts_dir / f"{agent_type}.yaml"
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    self._prompts[agent_type] = yaml.safe_load(f)
            except FileNotFoundError:
                raise FileNotFoundError(f"Prompt file not found: {yaml_path}")
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML file {yaml_path}: {e}")

    def _build_prompt(self, agent_type: str) -> str:
        """
        에이전트 유형에 따른 완전한 프롬프트 구성
        
        Args:
            agent_type: 'query_analysis', 'kb_retrieval', 'response_synthesis'
            
        Returns:
            str: 완전한 시스템 프롬프트
        """
        if agent_type not in self._prompts:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_config = self._prompts[agent_type]
        
        # 프롬프트 구성 요소 조합
        prompt_parts = []
        
        if 'role' in agent_config:
            prompt_parts.append(f"<role>\n{agent_config['role']}\n</role>")
        
        if 'task' in agent_config:
            prompt_parts.append(f"<task>\n{agent_config['task']}\n</task>")
        
        if 'context' in agent_config:
            prompt_parts.append(f"<context>\n{agent_config['context']}\n</context>")
        
        if 'instructions' in agent_config:
            prompt_parts.append(f"<instructions>\n{agent_config['instructions']}\n</instructions>")
        
        if 'output_format' in agent_config:
            prompt_parts.append(f"<output_format>\n{agent_config['output_format']}\n</output_format>")
        
        # 예시 추가
        if 'examples' in agent_config and agent_config['examples']:
            examples_str = "\n<examples>\n"
            for example in agent_config['examples']:
                examples_str += "<example>\n"
                examples_str += f"<input>\n{example['input']}\n</input>\n"
                
                if 'thinking' in example:
                    examples_str += f"<thinking>\n{example['thinking']}\n</thinking>\n"
                
                if 'answer' in example:
                    examples_str += f"<answer>\n{example['answer']}\n</answer>\n"
                
                if 'output' in example:
                    examples_str += f"<output>\n{example['output']}\n</output>\n"
                
                examples_str += "</example>\n\n"
            examples_str += "</examples>"
            prompt_parts.append(examples_str)
        
        # 추가 정보
        if 'notes' in agent_config:
            prompt_parts.append(f"<important_notes>\n{agent_config['notes']}\n</important_notes>")
        
        if 'error_handling' in agent_config:
            prompt_parts.append(f"<error_handling>\n{agent_config['error_handling']}\n</error_handling>")
        
        if 'limitations' in agent_config:
            prompt_parts.append(f"<limitations>\n{agent_config['limitations']}\n</limitations>")
        
        return "\n\n".join(prompt_parts)
    
    def get_prompt(self, agent_type: str) -> str:
        """
        에이전트 유형에 따른 프롬프트 반환
        
        Args:
            agent_type: 'query_analysis', 'kb_retrieval', 'response_synthesis'
            
        Returns:
            str: 해당 에이전트의 시스템 프롬프트
        """
        return self._build_prompt(agent_type)
    
    def get_all_prompts(self) -> Dict[str, str]:
        """
        모든 에이전트 프롬프트를 딕셔너리로 반환
        
        Returns:
            dict: 에이전트 유형을 키로, 프롬프트를 값으로 하는 딕셔너리
        """
        return {
            "query_analysis": self.get_prompt("query_analysis"),
            "kb_retrieval": self.get_prompt("kb_retrieval"),
            "response_synthesis": self.get_prompt("response_synthesis")
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        프롬프트 메타데이터 반환
        
        Returns:
            dict: 버전, 문서 커버리지 등의 메타데이터
        """
        return self._metadata or {}
    
    def validate_prompt_principles(self, prompt: str) -> Dict[str, Any]:
        """
        프롬프트가 Anthropic 9가지 원칙을 준수하는지 검증
        
        Args:
            prompt: 검증할 프롬프트 텍스트
            
        Returns:
            dict: 각 원칙의 준수 여부와 점수
        """
        validation_results = {
            "clear_instructions": "<instructions>" in prompt,
            "sufficient_context": "<context>" in prompt,
            "examples_provided": "<examples>" in prompt and "<example>" in prompt,
            "chain_of_thought": "<thinking>" in prompt or "단계별" in prompt,
            "xml_structure": all(tag in prompt for tag in ["<role>", "<task>", "<output_format>"]),
            "role_assignment": "전문가" in prompt or "expert" in prompt,
            "response_prefill": "다음 형식으로" in prompt or "시작하세요" in prompt,
            "prompt_chaining": True,  # 워크플로우 자체가 프롬프트 체이닝
            "long_context": len(prompt) > 1000  # 충분한 컨텍스트 제공
        }
        
        score = sum(validation_results.values()) / len(validation_results) * 100
        
        return {
            "principles": validation_results,
            "score": score,
            "passed": score >= 80  # 80% 이상 준수 시 통과
        }


# 전역 로더 인스턴스
_loader = PromptLoader()

# 편의 함수들
def get_prompt_by_agent_type(agent_type: str) -> str:
    """
    에이전트 유형에 따른 프롬프트 반환
    
    Args:
        agent_type: 'query_analysis', 'kb_retrieval', 'response_synthesis'
        
    Returns:
        str: 해당 에이전트의 시스템 프롬프트
    """
    return _loader.get_prompt(agent_type)


def get_all_prompts() -> Dict[str, str]:
    """
    모든 에이전트 프롬프트를 딕셔너리로 반환
    
    Returns:
        dict: 에이전트 유형을 키로, 프롬프트를 값으로 하는 딕셔너리
    """
    return _loader.get_all_prompts()


def validate_prompt_principles(prompt: str) -> Dict[str, Any]:
    """
    프롬프트가 Anthropic 9가지 원칙을 준수하는지 검증
    
    Args:
        prompt: 검증할 프롬프트 텍스트
        
    Returns:
        dict: 각 원칙의 준수 여부와 점수
    """
    return _loader.validate_prompt_principles(prompt)


# 상수로 프롬프트 노출 (하위 호환성)
QUERY_ANALYSIS_PROMPT = _loader.get_prompt("query_analysis")
KB_RETRIEVAL_PROMPT = _loader.get_prompt("kb_retrieval")
RESPONSE_SYNTHESIS_PROMPT = _loader.get_prompt("response_synthesis")
PROMPT_METADATA = _loader.get_metadata()


if __name__ == "__main__":
    """프롬프트 검증 스크립트"""
    print("=" * 80)
    print("GraphRAG 멀티 에이전트 프롬프트 검증")
    print("=" * 80)
    
    loader = PromptLoader()
    
    for agent_type in ["query_analysis", "kb_retrieval", "response_synthesis"]:
        print(f"\n[{agent_type.upper()}]")
        prompt = loader.get_prompt(agent_type)
        validation = loader.validate_prompt_principles(prompt)
        print(f"  점수: {validation['score']:.1f}%")
        print(f"  통과: {'✓' if validation['passed'] else '✗'}")
        print(f"  프롬프트 길이: {len(prompt):,} 문자")
        
        failed_principles = [
            principle for principle, passed in validation['principles'].items()
            if not passed
        ]
        if failed_principles:
            print(f"  미준수 원칙: {', '.join(failed_principles)}")
    
    print("\n" + "=" * 80)
    print("문서 커버리지")
    print("=" * 80)
    metadata = loader.get_metadata()
    doc_coverage = metadata.get('document_coverage', {})
    print(f"총 문서 수: {doc_coverage.get('total_documents', 0)}")
    print(f"예시에 포함된 문서: {len(doc_coverage.get('covered_documents', []))}")
    print("\n포함된 문서:")
    for doc in doc_coverage.get('covered_documents', []):
        print(f"  - {doc}")
    
    print("\n" + "=" * 80)
    print("검증 완료")
    print("=" * 80)
