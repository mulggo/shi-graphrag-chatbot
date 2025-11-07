# CloudFront 배포 가이드

## 개요
선박 소방 규정 챗봇 Streamlit 애플리케이션 앞에 CloudFront CDN을 설정합니다.

## 배포 방법

### 1. 자동 배포 (권장)
```bash
cd deployment
./deploy-cloudfront.sh
```

### 2. 수동 배포
```bash
aws cloudformation deploy \
    --template-file cloudfront-streamlit.yaml \
    --stack-name ship-firefighting-chatbot-cloudfront \
    --region us-west-2 \
    --parameter-overrides \
        StreamlitOriginDomain=35.162.142.5 \
        StreamlitPort=8501 \
    --capabilities CAPABILITY_IAM
```

## CloudFront 설정 특징

### 캐싱 정책
- **기본**: 캐싱 비활성화 (동적 콘텐츠)
- **정적 파일** (`/static/*`): 캐싱 최적화
- **Streamlit 코어** (`/_stcore/*`): 캐싱 비활성화

### 보안 설정
- **HTTPS 강제**: HTTP → HTTPS 리다이렉트
- **압축 활성화**: Gzip 압축으로 전송 최적화
- **CORS 지원**: 크로스 오리진 요청 허용

### WebSocket 지원
- Streamlit의 실시간 업데이트를 위한 WebSocket 연결 지원
- 필요한 헤더 전달: Host, Origin, User-Agent 등

## 배포 후 확인사항

### 1. 배포 상태 확인
```bash
aws cloudfront get-distribution --id <DISTRIBUTION_ID>
```

### 2. 캐시 무효화 (필요시)
```bash
aws cloudfront create-invalidation \
    --distribution-id <DISTRIBUTION_ID> \
    --paths "/*"
```

### 3. 접속 테스트
- CloudFront URL로 접속하여 정상 동작 확인
- 지식 그래프 시각화 기능 테스트
- 채팅 기능 테스트

## 주의사항

1. **배포 시간**: CloudFront 배포는 15-20분 소요
2. **캐시 정책**: 동적 콘텐츠는 캐싱하지 않음
3. **WebSocket**: Streamlit의 실시간 기능 지원
4. **비용**: CloudFront 사용량에 따른 과금

## 문제 해결

### 접속 불가 시
1. EC2 보안 그룹에서 8501 포트 허용 확인
2. Streamlit 애플리케이션 실행 상태 확인
3. CloudFront 배포 상태 확인

### 캐시 문제 시
```bash
# 전체 캐시 무효화
aws cloudfront create-invalidation \
    --distribution-id <DISTRIBUTION_ID> \
    --paths "/*"
```