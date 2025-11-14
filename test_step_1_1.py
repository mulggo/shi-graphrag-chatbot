#!/usr/bin/env python3
"""
1.1 AWS 클라이언트 초기화 테스트
"""
import sys
sys.path.append('/home/ec2-user/workshops/shi-graphrag-chatbot')

def test_aws_client_init():
    print("🔍 1.1 AWS 클라이언트 초기화 테스트 시작...")
    
    try:
        from agents.plan_execute_agent.agent import PlanExecuteAgent
        
        agent = PlanExecuteAgent()
        print("✅ AWS 클라이언트 초기화 성공")
        print(f"   - bedrock_client: {type(agent.bedrock_client)}")
        print(f"   - bedrock_runtime: {type(agent.bedrock_runtime)}")
        return True
        
    except Exception as e:
        print(f"❌ AWS 클라이언트 초기화 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_aws_client_init()
    exit(0 if success else 1)