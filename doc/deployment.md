# Deployment Guide

## Overview

This guide covers deployment options for the Ship Firefighting Rules Chatbot, from local development to production deployment with CDN and load balancing.

## Local Development

### Prerequisites

- Python 3.11+
- AWS CLI configured
- Virtual environment

### Setup

```bash
# Clone repository
git clone <repository-url>
cd shi-graphrag-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

**Access**: http://localhost:8501

## Production Deployment Options

### Option 1: Direct EC2 Deployment (Current)

**Current Setup:**
- EC2 Instance: `35.162.142.5`
- Port: `8501`
- Access: http://35.162.142.5:8501

**Advantages:**
- Simple setup
- Direct access
- Full WebSocket support

**Disadvantages:**
- No SSL/HTTPS
- Single point of failure
- No global CDN

### Option 2: Application Load Balancer (Recommended)

Deploy with ALB for SSL termination and high availability.

**Template**: `deployment/alb-streamlit.yaml`

```bash
# Deploy ALB stack
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

**Features:**
- SSL/TLS termination
- Health checks
- Auto-scaling ready
- WebSocket support

### Option 3: CloudFront CDN (Experimental)

Global CDN distribution for worldwide access.

**Template**: `deployment/cloudfront-simple.yaml`

```bash
# Deploy CloudFront
cd deployment
./deploy-cloudfront.sh
```

**Current URL**: https://ds400wl3np0vm.cloudfront.net

**Known Issues:**
- WebSocket compatibility problems
- Streamlit real-time features may not work
- Slower than direct access

**Status**: ⚠️ Not recommended for production due to WebSocket issues

## AWS Resource Requirements

### Required Services

1. **Amazon Bedrock**
   - Agent: `WT3ZJ25XCL`
   - Alias: `3RWZZLJDY1`
   - Knowledge Base: `CDPB5AI6BH` (BDA), `PWRU19RDNE` (Claude)

2. **Amazon Neptune**
   - Analytics BDA: `g-goxs5d7fi3`
   - Analytics Claude: `g-ryb6suoa69`
   - SPARQL: FSS Ontology endpoint

3. **Amazon DynamoDB**
   - OCR Storage: `ship-firefighting-ocr`

3. **Amazon S3**
   - Document storage
   - Reference images

4. **Amazon EC2**
   - Application hosting
   - Current: `35.162.142.5`

### IAM Permissions

Required permissions for the application:

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

## Configuration Management

### Environment-Specific Configs

**Development** (`config/agents.yaml`):
```yaml
global_config:
  aws_region: "us-west-2"
  default_language: "ko"
  enable_tracing: true
```

**Production** (recommended):
```yaml
global_config:
  aws_region: "us-west-2"
  default_language: "ko"
  enable_tracing: false
  session_timeout: 1800
```

### Streamlit Configuration

**File**: `.streamlit/config.toml`

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
showErrorDetails = false  # Set to false in production
```

## Security Considerations

### Network Security

1. **Security Groups**:
   - Inbound: Port 8501 from ALB only
   - Outbound: HTTPS to AWS services

2. **VPC Configuration**:
   - Private subnets for application
   - Public subnets for load balancer
   - NAT Gateway for outbound access

### Application Security

1. **AWS Credentials**:
   - Use IAM roles (no hardcoded keys)
   - Principle of least privilege
   - Regular credential rotation

2. **Input Validation**:
   - Sanitize user inputs
   - Rate limiting
   - Session management

3. **Data Protection**:
   - Encrypt data in transit (HTTPS)
   - Secure S3 bucket policies
   - VPC endpoints for AWS services

## Monitoring & Logging

### CloudWatch Integration

**Metrics to Monitor**:
- Application response time
- Error rates
- Memory/CPU usage
- Active sessions

**Log Groups**:
- Application logs: `/aws/ec2/streamlit`
- Access logs: `/aws/alb/access`
- Error logs: `/aws/alb/error`

### Health Checks

**ALB Health Check**:
```yaml
HealthCheckPath: /
HealthCheckProtocol: HTTP
HealthCheckIntervalSeconds: 30
HealthyThresholdCount: 2
UnhealthyThresholdCount: 5
```

**Custom Health Endpoint** (recommended):
```python
# Add to app.py
@st.cache_data
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Add route: /health
```

## Scaling Considerations

### Horizontal Scaling

**Auto Scaling Group**:
```yaml
AutoScalingGroup:
  MinSize: 1
  MaxSize: 3
  DesiredCapacity: 2
  TargetGroupARNs:
    - !Ref StreamlitTargetGroup
```

**Session Stickiness**:
- Enable ALB session stickiness
- Or implement stateless sessions

### Vertical Scaling

**Instance Types**:
- Development: `t3.medium`
- Production: `t3.large` or `t3.xlarge`
- High traffic: `c5.large` or `c5.xlarge`

## Backup & Recovery

### Application Backup

1. **Code Repository**:
   - Git version control
   - Automated deployments
   - Configuration as code

2. **Configuration Backup**:
   - S3 backup of config files
   - Parameter Store for secrets
   - CloudFormation templates

### Data Backup

1. **Neptune Backup**:
   - Automated snapshots
   - Point-in-time recovery
   - Cross-region replication

2. **S3 Backup**:
   - Versioning enabled
   - Cross-region replication
   - Lifecycle policies

## Troubleshooting

### Common Issues

1. **Application Won't Start**:
   ```bash
   # Check logs
   tail -f /var/log/streamlit.log
   
   # Check dependencies
   pip list
   
   # Test AWS connectivity
   aws bedrock list-foundation-models --region us-west-2
   ```

2. **Slow Performance**:
   - Check Neptune connectivity
   - Monitor CloudWatch metrics
   - Optimize graph queries
   - Enable caching

3. **WebSocket Issues**:
   - Check ALB configuration
   - Verify security groups
   - Test direct connection

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add to streamlit config
[logger]
level = "debug"
```

## Deployment Checklist

### Pre-Deployment

- [ ] AWS credentials configured
- [ ] All dependencies installed
- [ ] Configuration files updated
- [ ] Security groups configured
- [ ] IAM roles created

### Deployment

- [ ] Application deployed
- [ ] Health checks passing
- [ ] SSL certificate installed
- [ ] DNS records updated
- [ ] Monitoring configured

### Post-Deployment

- [ ] Functionality testing
- [ ] Performance testing
- [ ] Security scanning
- [ ] Backup verification
- [ ] Documentation updated

## Cost Optimization

### AWS Cost Factors

1. **EC2 Instances**: Use appropriate instance types
2. **Neptune**: Monitor query costs
3. **Bedrock**: Track API usage
4. **S3**: Implement lifecycle policies
5. **CloudFront**: Monitor data transfer

### Optimization Strategies

1. **Reserved Instances**: For predictable workloads
2. **Spot Instances**: For development environments
3. **Auto Scaling**: Scale based on demand
4. **Caching**: Reduce API calls
5. **Monitoring**: Track and optimize usage

## Future Improvements

### Planned Enhancements

1. **Container Deployment**:
   - Docker containerization
   - ECS/EKS deployment
   - Blue-green deployments

2. **CI/CD Pipeline**:
   - Automated testing
   - Deployment automation
   - Infrastructure as code

3. **Multi-Region**:
   - Global deployment
   - Disaster recovery
   - Performance optimization

4. **Advanced Monitoring**:
   - Application performance monitoring
   - User analytics
   - Cost optimization alerts