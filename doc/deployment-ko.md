# 배포 가이드

## 개요

이 가이드는 선박 소방 규정 챗봇의 로컬 개발부터 CDN 및 로드 밸런싱을 포함한 프로덕션 배포까지의 배포 옵션을 다룹니다.

## 로컬 개발

### 사전 요구사항

- Python 3.11+
- 구성된 AWS CLI
- 가상 환경

### 설정

```bash
# 저장소 복제
git clone <repository-url>
cd shi-graphrag-chatbot

# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
streamlit run app.py
```

**접속**: http://localhost:8501

## 프로덕션 배포 옵션

### 옵션 1: 직접 EC2 배포 (현재)

**현재 설정:**
- EC2 인스턴스: `35.162.142.5`
- 포트: `8501`
- 접속: http://35.162.142.5:8501

**장점:**
- 간단한 설정
- 직접 접속
- 완전한 WebSocket 지원

**단점:**
- SSL/HTTPS 없음
- 단일 장애점
- 글로벌 CDN 없음

### 옵션 2: Application Load Balancer (권장)

SSL 종료 및 고가용성을 위한 ALB 배포.

**템플릿**: `deployment/alb-streamlit.yaml`

```bash
# ALB 스택 배포
aws cloudformation deploy \
    --template-file deployment/alb-streamlit.yaml \
    --stack-name streamlit-alb \
    --region us-west-2 \
    --parameter-overrides \
        VpcId=vpc-xxxxxxxxx \
        SubnetIds=subnet-xxxxxxxx,subnet-yyyyyyyy \
        EC2InstanceId=i-xxxxxxxxx \
    --capabilities CAPABILITY_IAM
```

**기능:**
- SSL/TLS 종료
- 헬스 체크
- 자동 확장 준비
- WebSocket 지원

### 옵션 3: CloudFront CDN (실험적)

전 세계 접속을 위한 글로벌 CDN 배포.

**템플릿**: `deployment/cloudfront-simple.yaml`

```bash
# CloudFront 배포
cd deployment
./deploy-cloudfront.sh
```

**현재 URL**: https://ds400wl3np0vm.cloudfront.net

**알려진 문제:**
- WebSocket 호환성 문제
- Streamlit 실시간 기능이 작동하지 않을 수 있음
- 직접 접속보다 느림

**상태**: ⚠️ WebSocket 문제로 인해 프로덕션에서 권장하지 않음

## AWS 리소스 요구사항

### 필수 서비스

1. **Amazon Bedrock**
   - Agent: `WT3ZJ25XCL`
   - Alias: `3RWZZLJDY1`
   - Knowledge Base: `ZGBA1R5CS0`

2. **Amazon Neptune**
   - Analytics: `g-gqisj8edd6`
   - SPARQL: `shi-neptune-2.cluster-ct0is2emg3pe.us-west-2.neptune.amazonaws.com`

3. **Amazon S3**
   - 문서 저장
   - 참조 이미지

4. **Amazon EC2**
   - 애플리케이션 호스팅
   - 현재: `35.162.142.5`

### IAM 권한

애플리케이션에 필요한 권한:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeAgent",
                "bedrock:Retrieve"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2:*:agent/*",
                "arn:aws:bedrock:us-west-2:*:knowledge-base/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "neptune-graph:ExecuteQuery"
            ],
            "Resource": "arn:aws:neptune-graph:us-west-2:*:graph/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "neptune-db:ReadDataViaQuery"
            ],
            "Resource": "arn:aws:neptune-db:us-west-2:*:cluster/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::*/*"
        }
    ]
}
```

## 구성 관리

### 환경별 구성

**개발** (`config/agents.yaml`):
```yaml
global_config:
  aws_region: "us-west-2"
  default_language: "ko"
  enable_tracing: true
```

**프로덕션** (권장):
```yaml
global_config:
  aws_region: "us-west-2"
  default_language: "ko"
  enable_tracing: false
  session_timeout: 1800
```

### Streamlit 구성

**파일**: `.streamlit/config.toml`

```toml
[server]
headless = true
runOnSave = false
port = 8501
enableCORS = true
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"

[client]
caching = false
displayEnabled = true
showErrorDetails = false  # 프로덕션에서는 false로 설정
```

## 보안 고려사항

### 네트워크 보안

1. **보안 그룹**:
   - 인바운드: ALB에서만 포트 8501
   - 아웃바운드: AWS 서비스로 HTTPS

2. **VPC 구성**:
   - 애플리케이션용 프라이빗 서브넷
   - 로드 밸런서용 퍼블릭 서브넷
   - 아웃바운드 접속용 NAT Gateway

### 애플리케이션 보안

1. **AWS 자격 증명**:
   - IAM 역할 사용 (하드코딩된 키 없음)
   - 최소 권한 원칙
   - 정기적인 자격 증명 순환

2. **입력 검증**:
   - 사용자 입력 정화
   - 속도 제한
   - 세션 관리

3. **데이터 보호**:
   - 전송 중 데이터 암호화 (HTTPS)
   - 안전한 S3 버킷 정책
   - AWS 서비스용 VPC 엔드포인트

## 모니터링 및 로깅

### CloudWatch 통합

**모니터링할 메트릭**:
- 애플리케이션 응답 시간
- 오류율
- 메모리/CPU 사용량
- 활성 세션

**로그 그룹**:
- 애플리케이션 로그: `/aws/ec2/streamlit`
- 접속 로그: `/aws/alb/access`
- 오류 로그: `/aws/alb/error`

### 헬스 체크

**ALB 헬스 체크**:
```yaml
HealthCheckPath: /
HealthCheckProtocol: HTTP
HealthCheckIntervalSeconds: 30
HealthyThresholdCount: 2
UnhealthyThresholdCount: 5
```

**사용자 정의 헬스 엔드포인트** (권장):
```python
# app.py에 추가
@st.cache_data
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# 라우트 추가: /health
```

## 확장 고려사항

### 수평 확장

**Auto Scaling Group**:
```yaml
AutoScalingGroup:
  MinSize: 1
  MaxSize: 3
  DesiredCapacity: 2
  TargetGroupARNs:
    - !Ref StreamlitTargetGroup
```

**세션 고정성**:
- ALB 세션 고정성 활성화
- 또는 상태 비저장 세션 구현

### 수직 확장

**인스턴스 유형**:
- 개발: `t3.medium`
- 프로덕션: `t3.large` 또는 `t3.xlarge`
- 높은 트래픽: `c5.large` 또는 `c5.xlarge`

## 백업 및 복구

### 애플리케이션 백업

1. **코드 저장소**:
   - Git 버전 제어
   - 자동화된 배포
   - 코드형 구성

2. **구성 백업**:
   - 구성 파일의 S3 백업
   - 비밀 정보용 Parameter Store
   - CloudFormation 템플릿

### 데이터 백업

1. **Neptune 백업**:
   - 자동화된 스냅샷
   - 특정 시점 복구
   - 교차 리전 복제

2. **S3 백업**:
   - 버전 관리 활성화
   - 교차 리전 복제
   - 수명 주기 정책

## 문제 해결

### 일반적인 문제

1. **애플리케이션이 시작되지 않음**:
   ```bash
   # 로그 확인
   tail -f /var/log/streamlit.log
   
   # 의존성 확인
   pip list
   
   # AWS 연결 테스트
   aws bedrock list-foundation-models --region us-west-2
   ```

2. **느린 성능**:
   - Neptune 연결 확인
   - CloudWatch 메트릭 모니터링
   - 그래프 쿼리 최적화
   - 캐싱 활성화

3. **WebSocket 문제**:
   - ALB 구성 확인
   - 보안 그룹 확인
   - 직접 연결 테스트

### 디버그 모드

디버그 로깅 활성화:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# streamlit 구성에 추가
[logger]
level = "debug"
```

## 배포 체크리스트

### 배포 전

- [ ] AWS 자격 증명 구성됨
- [ ] 모든 의존성 설치됨
- [ ] 구성 파일 업데이트됨
- [ ] 보안 그룹 구성됨
- [ ] IAM 역할 생성됨

### 배포

- [ ] 애플리케이션 배포됨
- [ ] 헬스 체크 통과
- [ ] SSL 인증서 설치됨
- [ ] DNS 레코드 업데이트됨
- [ ] 모니터링 구성됨

### 배포 후

- [ ] 기능 테스트
- [ ] 성능 테스트
- [ ] 보안 스캔
- [ ] 백업 확인
- [ ] 문서 업데이트

## 비용 최적화

### AWS 비용 요소

1. **EC2 인스턴스**: 적절한 인스턴스 유형 사용
2. **Neptune**: 쿼리 비용 모니터링
3. **Bedrock**: API 사용량 추적
4. **S3**: 수명 주기 정책 구현
5. **CloudFront**: 데이터 전송 모니터링

### 최적화 전략

1. **예약 인스턴스**: 예측 가능한 워크로드용
2. **스팟 인스턴스**: 개발 환경용
3. **자동 확장**: 수요에 따른 확장
4. **캐싱**: API 호출 감소
5. **모니터링**: 사용량 추적 및 최적화

## 향후 개선사항

### 계획된 개선사항

1. **컨테이너 배포**:
   - Docker 컨테이너화
   - ECS/EKS 배포
   - 블루-그린 배포

2. **CI/CD 파이프라인**:
   - 자동화된 테스트
   - 배포 자동화
   - 코드형 인프라

3. **멀티 리전**:
   - 글로벌 배포
   - 재해 복구
   - 성능 최적화

4. **고급 모니터링**:
   - 애플리케이션 성능 모니터링
   - 사용자 분석
   - 비용 최적화 알림