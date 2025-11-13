"""
GraphRAG Metrics - CloudWatch metrics collection for monitoring

이 모듈은 GraphRAG 시스템의 성능 메트릭을 CloudWatch에 수집합니다.
워크플로우 실행 시간, 검색 품질, 에러율 등을 추적합니다.

Requirements: 8.1-8.6 (Monitoring and Observability)
"""
import boto3
import logging
from typing import Dict, List, Optional
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class GraphRAGMetrics:
    """
    GraphRAG 시스템 메트릭 수집 및 CloudWatch 전송
    
    주요 메트릭:
    - 워크플로우 실행 시간 (단계별, 전체)
    - 검색 품질 및 청크 수
    - Reranking 점수
    - 에러율 및 에러 유형
    - Lambda 함수 호출 횟수
    
    Requirements: 8.6 (Performance metrics logging)
    """
    
    def __init__(self, namespace: str = 'GraphRAG', enabled: bool = True):
        """
        메트릭 수집기 초기화
        
        Args:
            namespace: CloudWatch 네임스페이스 (기본값: 'GraphRAG')
            enabled: 메트릭 수집 활성화 여부 (기본값: True)
        """
        self.namespace = namespace
        self.enabled = enabled
        
        if self.enabled:
            try:
                self.cloudwatch = boto3.client('cloudwatch')
                logger.info(f"CloudWatch 메트릭 수집 활성화: namespace={namespace}")
            except Exception as e:
                logger.warning(f"CloudWatch 클라이언트 초기화 실패: {str(e)}")
                self.enabled = False
        else:
            logger.info("CloudWatch 메트릭 수집 비활성화")
    
    def record_workflow_duration(self, duration: float, success: bool = True):
        """
        전체 워크플로우 실행 시간 기록
        
        Args:
            duration: 실행 시간 (초)
            success: 성공 여부
        """
        if not self.enabled:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'WorkflowDuration',
                        'Value': duration,
                        'Unit': 'Seconds',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {
                                'Name': 'Status',
                                'Value': 'Success' if success else 'Failure'
                            }
                        ]
                    }
                ]
            )
            logger.debug(f"워크플로우 실행 시간 기록: {duration:.2f}s, success={success}")
        except ClientError as e:
            logger.warning(f"메트릭 전송 실패: {str(e)}")
    
    def record_query_analysis_time(self, duration: float):
        """
        쿼리 분석 시간 기록
        
        Args:
            duration: 분석 시간 (초)
        """
        if not self.enabled:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'QueryAnalysisTime',
                        'Value': duration,
                        'Unit': 'Seconds',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
            logger.debug(f"쿼리 분석 시간 기록: {duration:.2f}s")
        except ClientError as e:
            logger.warning(f"메트릭 전송 실패: {str(e)}")
    
    def record_retrieval_time(self, duration: float, chunks_retrieved: int):
        """
        검색 실행 시간 및 검색된 청크 수 기록
        
        Args:
            duration: 검색 시간 (초)
            chunks_retrieved: 검색된 청크 수
        """
        if not self.enabled:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'RetrievalTime',
                        'Value': duration,
                        'Unit': 'Seconds',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'RetrievalCount',
                        'Value': chunks_retrieved,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
            logger.debug(f"검색 시간 기록: {duration:.2f}s, chunks={chunks_retrieved}")
        except ClientError as e:
            logger.warning(f"메트릭 전송 실패: {str(e)}")
    
    def record_synthesis_time(self, duration: float, confidence: str):
        """
        응답 합성 시간 기록
        
        Args:
            duration: 합성 시간 (초)
            confidence: 신뢰도 (high, medium, low)
        """
        if not self.enabled:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'SynthesisTime',
                        'Value': duration,
                        'Unit': 'Seconds',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {
                                'Name': 'Confidence',
                                'Value': confidence.capitalize()
                            }
                        ]
                    }
                ]
            )
            logger.debug(f"응답 합성 시간 기록: {duration:.2f}s, confidence={confidence}")
        except ClientError as e:
            logger.warning(f"메트릭 전송 실패: {str(e)}")
    
    def record_reranking_score(self, score: float):
        """
        Reranking 점수 기록
        
        Args:
            score: Reranking 평균 점수 (0.0-1.0)
        """
        if not self.enabled:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'RerankingScore',
                        'Value': score,
                        'Unit': 'None',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
            logger.debug(f"Reranking 점수 기록: {score:.2f}")
        except ClientError as e:
            logger.warning(f"메트릭 전송 실패: {str(e)}")
    
    def record_search_quality(self, quality: str, question_type: str):
        """
        검색 품질 기록
        
        Args:
            quality: 검색 품질 (excellent, good, fair, poor)
            question_type: 질문 유형 (factual, relational, multi_doc, comparative)
        """
        if not self.enabled:
            return
        
        # 품질을 숫자로 변환
        quality_map = {
            'excellent': 4,
            'good': 3,
            'fair': 2,
            'poor': 1
        }
        quality_value = quality_map.get(quality.lower(), 0)
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'SearchQuality',
                        'Value': quality_value,
                        'Unit': 'None',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {
                                'Name': 'QuestionType',
                                'Value': question_type.capitalize()
                            }
                        ]
                    }
                ]
            )
            logger.debug(f"검색 품질 기록: {quality}, type={question_type}")
        except ClientError as e:
            logger.warning(f"메트릭 전송 실패: {str(e)}")
    
    def record_error(self, error_type: str, component: str):
        """
        에러 발생 기록
        
        Args:
            error_type: 에러 유형 (lambda_error, timeout, bedrock_error, config_error, unknown)
            component: 에러 발생 컴포넌트 (query_analysis, retrieval, synthesis, workflow)
        """
        if not self.enabled:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'ErrorCount',
                        'Value': 1,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {
                                'Name': 'ErrorType',
                                'Value': error_type
                            },
                            {
                                'Name': 'Component',
                                'Value': component
                            }
                        ]
                    }
                ]
            )
            logger.debug(f"에러 기록: type={error_type}, component={component}")
        except ClientError as e:
            logger.warning(f"메트릭 전송 실패: {str(e)}")
    
    def record_lambda_invocation(self, function_name: str, duration: float, success: bool):
        """
        Lambda 함수 호출 기록
        
        Args:
            function_name: Lambda 함수 이름 (classify_query, extract_entities, kb_retrieve)
            duration: 실행 시간 (초)
            success: 성공 여부
        """
        if not self.enabled:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'LambdaInvocationCount',
                        'Value': 1,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {
                                'Name': 'FunctionName',
                                'Value': function_name
                            },
                            {
                                'Name': 'Status',
                                'Value': 'Success' if success else 'Failure'
                            }
                        ]
                    },
                    {
                        'MetricName': 'LambdaDuration',
                        'Value': duration,
                        'Unit': 'Seconds',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {
                                'Name': 'FunctionName',
                                'Value': function_name
                            }
                        ]
                    }
                ]
            )
            logger.debug(f"Lambda 호출 기록: {function_name}, duration={duration:.2f}s, success={success}")
        except ClientError as e:
            logger.warning(f"메트릭 전송 실패: {str(e)}")
    
    def record_batch_metrics(self, metrics: List[Dict]):
        """
        여러 메트릭을 배치로 전송
        
        Args:
            metrics: 메트릭 데이터 리스트
                [
                    {
                        'MetricName': str,
                        'Value': float,
                        'Unit': str,
                        'Dimensions': List[Dict]
                    },
                    ...
                ]
        """
        if not self.enabled or not metrics:
            return
        
        try:
            # CloudWatch는 한 번에 최대 20개 메트릭 전송 가능
            for i in range(0, len(metrics), 20):
                batch = metrics[i:i+20]
                
                # Timestamp 추가
                for metric in batch:
                    if 'Timestamp' not in metric:
                        metric['Timestamp'] = datetime.utcnow()
                
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=batch
                )
            
            logger.debug(f"배치 메트릭 전송 완료: {len(metrics)}개")
        except ClientError as e:
            logger.warning(f"배치 메트릭 전송 실패: {str(e)}")
    
    def get_metric_statistics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        period: int = 300,
        statistics: List[str] = None
    ) -> Optional[Dict]:
        """
        메트릭 통계 조회
        
        Args:
            metric_name: 메트릭 이름
            start_time: 시작 시간
            end_time: 종료 시간
            period: 집계 기간 (초, 기본값: 300)
            statistics: 통계 유형 (기본값: ['Average', 'Sum', 'Maximum', 'Minimum'])
            
        Returns:
            Dict: 메트릭 통계 데이터
        """
        if not self.enabled:
            return None
        
        if statistics is None:
            statistics = ['Average', 'Sum', 'Maximum', 'Minimum']
        
        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace=self.namespace,
                MetricName=metric_name,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=statistics
            )
            
            return response
        except ClientError as e:
            logger.error(f"메트릭 통계 조회 실패: {str(e)}")
            return None


# 전역 메트릭 인스턴스 (선택사항)
_global_metrics = None


def get_metrics(namespace: str = 'GraphRAG', enabled: bool = True) -> GraphRAGMetrics:
    """
    전역 메트릭 인스턴스 가져오기 또는 생성
    
    Args:
        namespace: CloudWatch 네임스페이스
        enabled: 메트릭 수집 활성화 여부
        
    Returns:
        GraphRAGMetrics: 메트릭 수집기 인스턴스
    """
    global _global_metrics
    
    if _global_metrics is None:
        _global_metrics = GraphRAGMetrics(namespace=namespace, enabled=enabled)
    
    return _global_metrics
