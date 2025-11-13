"""
GraphRAG Performance Testing - 평균 응답 시간 30초 이내 검증

이 스크립트는 GraphRAG 멀티 에이전트 시스템의 성능을 테스트하고
평균 응답 시간이 30초 이내인지 검증합니다.

Requirements: 9.7 (Performance testing - 응답 시간 30초 이내)

테스트 시나리오:
1. 단순 사실 확인 질문 (예상: 15-20초)
2. 다중 문서 추론 질문 (예상: 20-25초)
3. 복잡한 비교 분석 질문 (예상: 25-30초)
4. 11개 문서 커버리지 테스트 (다양한 문서 유형)

성능 목표:
- 평균 응답 시간: < 30초
- 95 percentile: < 35초
- 최대 응답 시간: < 45초
"""
import time
import statistics
import json
from typing import List, Dict, Tuple
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceTestResult:
    """성능 테스트 결과"""
    
    def __init__(self, query: str, duration: float, success: bool, metadata: Dict = None):
        self.query = query
        self.duration = duration
        self.success = success
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'query': self.query,
            'duration': self.duration,
            'success': self.success,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class PerformanceTester:
    """GraphRAG 성능 테스터"""
    
    def __init__(self, agent):
        """
        성능 테스터 초기화
        
        Args:
            agent: GraphRAG Agent 인스턴스
        """
        self.agent = agent
        self.results: List[PerformanceTestResult] = []
    
    def run_single_test(self, query: str, session_id: str = "perf-test") -> PerformanceTestResult:
        """
        단일 쿼리 성능 테스트
        
        Args:
            query: 테스트 쿼리
            session_id: 세션 ID
            
        Returns:
            PerformanceTestResult: 테스트 결과
        """
        logger.info(f"테스트 시작: '{query[:50]}...'")
        
        start_time = time.time()
        
        try:
            response = self.agent.process_message(query, session_id)
            duration = time.time() - start_time
            
            success = response.get('success', False)
            metadata = response.get('metadata', {})
            
            result = PerformanceTestResult(
                query=query,
                duration=duration,
                success=success,
                metadata=metadata
            )
            
            logger.info(f"테스트 완료: duration={duration:.2f}s, success={success}")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"테스트 실패: {str(e)}")
            
            return PerformanceTestResult(
                query=query,
                duration=duration,
                success=False,
                metadata={'error': str(e)}
            )
    
    def run_test_suite(self, test_queries: List[Tuple[str, str]]) -> List[PerformanceTestResult]:
        """
        테스트 스위트 실행
        
        Args:
            test_queries: (query, category) 튜플 리스트
            
        Returns:
            List[PerformanceTestResult]: 테스트 결과 리스트
        """
        logger.info(f"테스트 스위트 시작: {len(test_queries)}개 쿼리")
        
        results = []
        
        for i, (query, category) in enumerate(test_queries, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"테스트 {i}/{len(test_queries)}: {category}")
            logger.info(f"{'='*80}")
            
            result = self.run_single_test(query, f"perf-test-{i}")
            result.metadata['category'] = category
            results.append(result)
            
            # 결과 저장
            self.results.append(result)
            
            # 테스트 간 간격 (Lambda 콜드 스타트 방지)
            if i < len(test_queries):
                time.sleep(2)
        
        return results
    
    def analyze_results(self, results: List[PerformanceTestResult]) -> Dict:
        """
        테스트 결과 분석
        
        Args:
            results: 테스트 결과 리스트
            
        Returns:
            Dict: 분석 결과
        """
        if not results:
            return {
                'error': 'No test results available'
            }
        
        # 성공한 테스트만 분석
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return {
                'error': 'No successful tests',
                'total_tests': len(results),
                'failed_tests': len(results)
            }
        
        durations = [r.duration for r in successful_results]
        
        # 기본 통계
        avg_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        # 표준 편차
        stdev_duration = statistics.stdev(durations) if len(durations) > 1 else 0
        
        # Percentiles
        sorted_durations = sorted(durations)
        p95_index = int(len(sorted_durations) * 0.95)
        p99_index = int(len(sorted_durations) * 0.99)
        p95_duration = sorted_durations[p95_index] if p95_index < len(sorted_durations) else max_duration
        p99_duration = sorted_durations[p99_index] if p99_index < len(sorted_durations) else max_duration
        
        # 카테고리별 분석
        category_stats = {}
        for result in successful_results:
            category = result.metadata.get('category', 'unknown')
            if category not in category_stats:
                category_stats[category] = []
            category_stats[category].append(result.duration)
        
        category_analysis = {}
        for category, durations in category_stats.items():
            category_analysis[category] = {
                'count': len(durations),
                'avg_duration': statistics.mean(durations),
                'min_duration': min(durations),
                'max_duration': max(durations)
            }
        
        # 성능 목표 달성 여부
        meets_avg_target = avg_duration < 30.0
        meets_p95_target = p95_duration < 35.0
        meets_max_target = max_duration < 45.0
        
        analysis = {
            'total_tests': len(results),
            'successful_tests': len(successful_results),
            'failed_tests': len(results) - len(successful_results),
            'success_rate': len(successful_results) / len(results) * 100,
            'duration_stats': {
                'average': avg_duration,
                'median': median_duration,
                'min': min_duration,
                'max': max_duration,
                'stdev': stdev_duration,
                'p95': p95_duration,
                'p99': p99_duration
            },
            'performance_targets': {
                'avg_under_30s': {
                    'target': 30.0,
                    'actual': avg_duration,
                    'met': meets_avg_target,
                    'margin': 30.0 - avg_duration
                },
                'p95_under_35s': {
                    'target': 35.0,
                    'actual': p95_duration,
                    'met': meets_p95_target,
                    'margin': 35.0 - p95_duration
                },
                'max_under_45s': {
                    'target': 45.0,
                    'actual': max_duration,
                    'met': meets_max_target,
                    'margin': 45.0 - max_duration
                }
            },
            'category_analysis': category_analysis,
            'overall_pass': meets_avg_target and meets_p95_target and meets_max_target
        }
        
        return analysis
    
    def print_results(self, analysis: Dict):
        """
        테스트 결과 출력
        
        Args:
            analysis: 분석 결과
        """
        print("\n" + "="*80)
        print("GraphRAG 성능 테스트 결과")
        print("="*80)
        
        if 'error' in analysis:
            print(f"\n❌ 에러: {analysis['error']}")
            return
        
        # 기본 통계
        print(f"\n📊 테스트 통계:")
        print(f"  - 총 테스트: {analysis['total_tests']}")
        print(f"  - 성공: {analysis['successful_tests']}")
        print(f"  - 실패: {analysis['failed_tests']}")
        print(f"  - 성공률: {analysis['success_rate']:.1f}%")
        
        # 응답 시간 통계
        stats = analysis['duration_stats']
        print(f"\n⏱️  응답 시간 통계:")
        print(f"  - 평균: {stats['average']:.2f}초")
        print(f"  - 중앙값: {stats['median']:.2f}초")
        print(f"  - 최소: {stats['min']:.2f}초")
        print(f"  - 최대: {stats['max']:.2f}초")
        print(f"  - 표준편차: {stats['stdev']:.2f}초")
        print(f"  - 95 percentile: {stats['p95']:.2f}초")
        print(f"  - 99 percentile: {stats['p99']:.2f}초")
        
        # 성능 목표 달성 여부
        targets = analysis['performance_targets']
        print(f"\n🎯 성능 목표 달성:")
        
        for target_name, target_data in targets.items():
            met = target_data['met']
            icon = "✅" if met else "❌"
            print(f"  {icon} {target_name}:")
            print(f"     목표: {target_data['target']:.1f}초")
            print(f"     실제: {target_data['actual']:.2f}초")
            print(f"     여유: {target_data['margin']:.2f}초")
        
        # 카테고리별 분석
        if analysis['category_analysis']:
            print(f"\n📁 카테고리별 분석:")
            for category, cat_stats in analysis['category_analysis'].items():
                print(f"  - {category}:")
                print(f"    테스트 수: {cat_stats['count']}")
                print(f"    평균: {cat_stats['avg_duration']:.2f}초")
                print(f"    범위: {cat_stats['min_duration']:.2f}초 ~ {cat_stats['max_duration']:.2f}초")
        
        # 전체 결과
        overall_pass = analysis['overall_pass']
        print(f"\n{'='*80}")
        if overall_pass:
            print("✅ 전체 성능 테스트 통과!")
            print("   평균 응답 시간이 30초 이내이며, 모든 성능 목표를 달성했습니다.")
        else:
            print("❌ 성능 테스트 실패")
            print("   일부 성능 목표를 달성하지 못했습니다. 최적화가 필요합니다.")
        print("="*80 + "\n")
    
    def save_results(self, filename: str = "performance_test_results.json"):
        """
        테스트 결과를 JSON 파일로 저장
        
        Args:
            filename: 저장할 파일명
        """
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'results': [r.to_dict() for r in self.results],
            'analysis': self.analyze_results(self.results)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"테스트 결과 저장: {filename}")


def get_test_queries() -> List[Tuple[str, str]]:
    """
    성능 테스트 쿼리 목록
    
    11개 문서를 균형있게 커버하는 다양한 질문 유형
    
    Returns:
        List[Tuple[str, str]]: (query, category) 튜플 리스트
    """
    return [
        # 1. 단순 사실 확인 (FSS Code)
        ("고정식 CO2 소화 시스템의 최소 용량은?", "simple_factual"),
        
        # 2. 단순 사실 확인 (SOLAS)
        ("화재 감지 시스템의 설치 요구사항은?", "simple_factual"),
        
        # 3. 설계 지침 (Design guidance)
        ("배관 지지대 설계 시 고려사항은?", "design_guidance"),
        
        # 4. 실무 문서 (Piping practice)
        ("배관 관통부 시공 시 주의사항은?", "practice"),
        
        # 5. DNV 규정
        ("DNV 선급 규칙에서 단열재 요구사항은?", "dnv_rules"),
        
        # 6. IGC Code
        ("IGC Code에 따른 가스 운반선의 소화 시스템은?", "igc_code"),
        
        # 7. 다중 문서 추론 (SOLAS + Design guidance)
        ("선체 관통부의 단열재 설계 기준과 시공 방법을 설명해주세요", "multi_doc"),
        
        # 8. 비교 분석 (Design guidance vs Practice)
        ("배관 지지대 설계 가이드와 실제 시공 방법의 차이점은?", "comparative"),
        
        # 9. 복잡한 다중 문서 (DNV + Design guidance + Practice)
        ("DNV 규정에 따른 배관 지지대 설계 기준과 실제 시공 시 주의사항을 비교해주세요", "complex_multi_doc"),
        
        # 10. 절차 문서 (Spoolcutting)
        ("스풀 절단 작업 시 안전 절차는?", "procedure"),
        
        # 11. 종합 질문 (여러 문서 통합)
        ("선박 기관실의 화재 안전 시스템 전체 구성과 각 규정별 요구사항을 설명해주세요", "comprehensive"),
    ]


def run_performance_test(agent, save_results: bool = True) -> Dict:
    """
    성능 테스트 실행
    
    Args:
        agent: GraphRAG Agent 인스턴스
        save_results: 결과 저장 여부
        
    Returns:
        Dict: 분석 결과
    """
    tester = PerformanceTester(agent)
    
    # 테스트 쿼리 가져오기
    test_queries = get_test_queries()
    
    # 테스트 실행
    logger.info(f"성능 테스트 시작: {len(test_queries)}개 쿼리")
    results = tester.run_test_suite(test_queries)
    
    # 결과 분석
    analysis = tester.analyze_results(results)
    
    # 결과 출력
    tester.print_results(analysis)
    
    # 결과 저장
    if save_results:
        tester.save_results()
    
    return analysis


if __name__ == "__main__":
    """
    성능 테스트 실행
    
    주의: 이 테스트는 Lambda 함수가 배포된 후에만 실행 가능합니다.
    """
    print("\n" + "="*80)
    print("GraphRAG 성능 테스트")
    print("="*80)
    print("\n⚠️  주의: 이 테스트는 Lambda 함수가 배포된 후에만 실행 가능합니다.")
    print("   Lambda 함수 배포 방법:")
    print("   1. cd lambda_package/graphrag_tools/")
    print("   2. ./deploy.sh")
    print("   3. config/agents.yaml에 Lambda ARN 설정")
    print("\n" + "="*80 + "\n")
    
    # Agent 초기화 (실제 환경에서는 config에서 로드)
    try:
        from agents.graphrag_agent.agent import Agent
        from core.agent_manager import AgentConfig
        import os
        
        # 환경 변수 확인
        required_env_vars = [
            'BEDROCK_KB_ID',
            'LAMBDA_CLASSIFY_QUERY_ARN',
            'LAMBDA_EXTRACT_ENTITIES_ARN',
            'LAMBDA_KB_RETRIEVE_ARN'
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ 필수 환경 변수가 설정되지 않았습니다:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n.env 파일을 확인하고 필요한 환경 변수를 설정해주세요.")
            exit(1)
        
        # Agent 설정
        config = AgentConfig(
            name='graphrag',
            display_name='GraphRAG 검색',
            knowledge_base_id=os.getenv('BEDROCK_KB_ID'),
            lambda_function_names={
                'classify_query': os.getenv('LAMBDA_CLASSIFY_QUERY_ARN'),
                'extract_entities': os.getenv('LAMBDA_EXTRACT_ENTITIES_ARN'),
                'kb_retrieve': os.getenv('LAMBDA_KB_RETRIEVE_ARN')
            },
            reranker_model_arn=os.getenv('RERANKER_MODEL_ARN'),
            bedrock_model_id=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0'),
            metrics_enabled=True
        )
        
        # Agent 초기화
        agent = Agent(config)
        
        # 성능 테스트 실행
        analysis = run_performance_test(agent, save_results=True)
        
        # 종료 코드 설정 (CI/CD 통합용)
        exit_code = 0 if analysis.get('overall_pass', False) else 1
        exit(exit_code)
        
    except ImportError as e:
        print(f"❌ 모듈 임포트 실패: {str(e)}")
        print("   agents/graphrag_agent/ 디렉토리가 올바르게 설정되었는지 확인해주세요.")
        exit(1)
    except Exception as e:
        print(f"❌ 테스트 실행 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
