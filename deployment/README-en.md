# CloudFront Deployment Guide

## Overview
Set up CloudFront CDN in front of the Ship Firefighting Rules Chatbot Streamlit application.

## Deployment Methods

### 1. Automated Deployment (Recommended)
```bash
cd deployment
./deploy-cloudfront.sh
```

### 2. Manual Deployment
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

## CloudFront Configuration Features

### Caching Policies
- **Default**: Caching disabled (dynamic content)
- **Static files** (`/static/*`): Caching optimized
- **Streamlit core** (`/_stcore/*`): Caching disabled

### Security Settings
- **HTTPS enforcement**: HTTP → HTTPS redirect
- **Compression enabled**: Gzip compression for transmission optimization
- **CORS support**: Cross-origin request support

### WebSocket Support
- WebSocket connection support for Streamlit's real-time updates
- Required header forwarding: Host, Origin, User-Agent, etc.

## Post-Deployment Verification

### 1. Check Deployment Status
```bash
aws cloudfront get-distribution --id <DISTRIBUTION_ID>
```

### 2. Cache Invalidation (if needed)
```bash
aws cloudfront create-invalidation \
    --distribution-id <DISTRIBUTION_ID> \
    --paths "/*"
```

### 3. Access Testing
- Access via CloudFront URL to verify normal operation
- Test knowledge graph visualization features
- Test chat functionality

## Important Notes

1. **Deployment time**: CloudFront deployment takes 15-20 minutes
2. **Cache policy**: Dynamic content is not cached
3. **WebSocket**: Supports Streamlit's real-time features
4. **Cost**: Charges based on CloudFront usage

## Troubleshooting

### Connection Issues
1. Verify EC2 security group allows port 8501
2. Check Streamlit application running status
3. Verify CloudFront deployment status

### Cache Issues
```bash
# Invalidate all cache
aws cloudfront create-invalidation \
    --distribution-id <DISTRIBUTION_ID> \
    --paths "/*"
```