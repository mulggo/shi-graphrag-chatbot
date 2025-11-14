"""
멀티 에이전트 관리자
새로운 에이전트 추가 시 설정 파일만 수정하면 되는 확장 가능한 구조
"""
import yaml
import importlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AgentConfig:
    """에이전트 설정 데이터 클래스"""
    name: str
    display_name: str
    description: str
    module_path: str
    bedrock_agent_id: str
    bedrock_alias_id: str
    knowledge_base_id: str
    lambda_function_name: Optional[str] = None
    ui_config: Optional[Dict] = None
    enabled: bool = True
    bedrock_model_id: Optional[str] = None
    lambda_function_names: Optional[Dict] = None
    reranker_model_arn: Optional[str] = None

class AgentManager:
    """에이전트 관리자 - 모든 에이전트의 등록, 관리, 라우팅 담당"""
    
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config_path = config_path
        self.agents: Dict[str, AgentConfig] = {}
        self.agent_instances: Dict[str, Any] = {}
        self.load_agents()
    
    def load_agents(self):
        """설정 파일에서 에이전트 정보 로드"""
        import os
        from dotenv import load_dotenv
        
        # 환경변수 로드
        load_dotenv()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            for agent_name, agent_config in config.get('agents', {}).items():
                # lambda_function_names에서 환경변수 치환
                if 'lambda_function_names' in agent_config:
                    lambda_names = agent_config['lambda_function_names']
                    if isinstance(lambda_names, dict):
                        for key, value in lambda_names.items():
                            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                                env_var = value[2:-1]  # ${ 와 } 제거
                                lambda_names[key] = os.getenv(env_var, '')
                
                self.agents[agent_name] = AgentConfig(
                    name=agent_name,
                    **agent_config
                )
                
                # 에이전트가 활성화되어 있으면 인스턴스 생성
                if agent_config.get('enabled', True):
                    self._load_agent_instance(agent_name)
                    
        except FileNotFoundError:
            print(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
        except Exception as e:
            print(f"에이전트 로드 중 오류: {e}")
    
    def _load_agent_instance(self, agent_name: str):
        """에이전트 인스턴스 동적 로딩"""
        try:
            agent_config = self.agents[agent_name]
            module = importlib.import_module(agent_config.module_path)
            
            # Plan-Execute Agent는 PlanExecuteAgent 클래스 사용
            if agent_name == 'plan_execute':
                agent_class = getattr(module, 'PlanExecuteAgent')
            else:
                agent_class = getattr(module, 'Agent')
            
            self.agent_instances[agent_name] = agent_class(agent_config)
            
        except Exception as e:
            print(f"에이전트 {agent_name} 로드 실패: {e}")
    
    def get_available_agents(self) -> List[AgentConfig]:
        """사용 가능한 에이전트 목록 반환"""
        return [config for config in self.agents.values() if config.enabled]
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """특정 에이전트 인스턴스 반환"""
        return self.agent_instances.get(agent_name)
    
    def route_message(self, agent_name: str, message: str, session_id: str, kb_id: str = None) -> Dict:
        """메시지를 해당 에이전트로 라우팅"""
        agent = self.get_agent(agent_name)
        if not agent:
            return {
                "error": f"에이전트 '{agent_name}'를 찾을 수 없습니다.",
                "success": False
            }
        
        try:
            # Plan-Execute Agent인 경우 KB ID 설정
            if agent_name == 'plan_execute' and kb_id:
                agent.kb_id = kb_id
            
            return agent.process_message(message, session_id)
        except Exception as e:
            return {
                "error": f"에이전트 처리 중 오류: {str(e)}",
                "success": False
            }
    
    def add_agent(self, agent_config: AgentConfig):
        """런타임에 새 에이전트 추가"""
        self.agents[agent_config.name] = agent_config
        if agent_config.enabled:
            self._load_agent_instance(agent_config.name)
    
    def reload_agents(self):
        """에이전트 설정 다시 로드"""
        self.agents.clear()
        self.agent_instances.clear()
        self.load_agents()