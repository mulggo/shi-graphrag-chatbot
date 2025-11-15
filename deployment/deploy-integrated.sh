#!/bin/bash

# Integrated ALB + CloudFront deployment script
# This script deploys both ALB and CloudFront in a single stack

set -e

# Configuration
STACK_NAME="streamlit-integrated"
TEMPLATE_FILE="alb-cloudfront-integrated.yaml"
REGION="us-west-2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS CLI is not configured or credentials are invalid"
        exit 1
    fi
    
    log_success "AWS CLI is configured"
}

# Get VPC and subnet information
get_vpc_info() {
    log_info "Getting VPC and subnet information..."
    
    # Get default VPC
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters "Name=is-default,Values=true" \
        --query 'Vpcs[0].VpcId' \
        --output text \
        --region $REGION)
    
    if [ "$VPC_ID" = "None" ] || [ -z "$VPC_ID" ]; then
        log_error "No default VPC found. Please specify VPC ID manually."
        exit 1
    fi
    
    # Get public subnets
    SUBNET_IDS=$(aws ec2 describe-subnets \
        --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=true" \
        --query 'Subnets[].SubnetId' \
        --output text \
        --region $REGION | tr '\t' ',')
    
    if [ -z "$SUBNET_IDS" ]; then
        log_error "No public subnets found in VPC $VPC_ID"
        exit 1
    fi
    
    log_success "Found VPC: $VPC_ID"
    log_success "Found subnets: $SUBNET_IDS"
}

# Get EC2 instance information
get_ec2_info() {
    log_info "Getting EC2 instance information..."
    
    # Look for running instances with Streamlit
    INSTANCE_ID=$(aws ec2 describe-instances \
        --filters "Name=instance-state-name,Values=running" \
        --query 'Reservations[].Instances[?Tags[?Key==`Name` && contains(Value, `streamlit`)]].[InstanceId]' \
        --output text \
        --region $REGION | head -1)
    
    if [ -z "$INSTANCE_ID" ] || [ "$INSTANCE_ID" = "None" ]; then
        # Fallback: get any running instance
        INSTANCE_ID=$(aws ec2 describe-instances \
            --filters "Name=instance-state-name,Values=running" \
            --query 'Reservations[0].Instances[0].InstanceId' \
            --output text \
            --region $REGION)
    fi
    
    if [ -z "$INSTANCE_ID" ] || [ "$INSTANCE_ID" = "None" ]; then
        log_error "No running EC2 instances found"
        exit 1
    fi
    
    log_success "Found EC2 instance: $INSTANCE_ID"
}

# Deploy CloudFormation stack
deploy_stack() {
    log_info "Deploying CloudFormation stack: $STACK_NAME"
    
    # Prepare parameters
    PARAMETERS="ParameterKey=VpcId,ParameterValue=$VPC_ID"
    PARAMETERS="$PARAMETERS ParameterKey=SubnetIds,ParameterValue=\"$SUBNET_IDS\""
    PARAMETERS="$PARAMETERS ParameterKey=EC2InstanceId,ParameterValue=$INSTANCE_ID"
    
    # Add certificate ARN if provided
    if [ ! -z "$CERTIFICATE_ARN" ]; then
        PARAMETERS="$PARAMETERS ParameterKey=CertificateArn,ParameterValue=$CERTIFICATE_ARN"
    fi
    
    # Add domain name if provided
    if [ ! -z "$DOMAIN_NAME" ]; then
        PARAMETERS="$PARAMETERS ParameterKey=DomainName,ParameterValue=$DOMAIN_NAME"
    fi
    
    # Deploy stack
    aws cloudformation deploy \
        --template-file $TEMPLATE_FILE \
        --stack-name $STACK_NAME \
        --parameter-overrides $PARAMETERS \
        --capabilities CAPABILITY_IAM \
        --region $REGION \
        --no-fail-on-empty-changeset
    
    if [ $? -eq 0 ]; then
        log_success "Stack deployed successfully"
    else
        log_error "Stack deployment failed"
        exit 1
    fi
}

# Get stack outputs
get_outputs() {
    log_info "Getting stack outputs..."
    
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text \
        --region $REGION)
    
    CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
        --output text \
        --region $REGION)
    
    APP_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
        --output text \
        --region $REGION)
    
    echo ""
    log_success "Deployment completed successfully!"
    echo ""
    echo "📊 Deployment Information:"
    echo "  Stack Name: $STACK_NAME"
    echo "  Region: $REGION"
    echo "  VPC ID: $VPC_ID"
    echo "  EC2 Instance: $INSTANCE_ID"
    echo ""
    echo "🌐 Access URLs:"
    echo "  ALB Direct: http://$ALB_DNS"
    echo "  CloudFront: $APP_URL"
    
    if [ ! -z "$DOMAIN_NAME" ]; then
        echo "  Custom Domain: https://$DOMAIN_NAME"
    fi
    
    echo ""
    echo "⚠️  Note: CloudFront deployment may take 15-20 minutes to fully propagate"
    echo "   Use ALB URL for immediate access, CloudFront URL for global CDN"
}

# Main execution
main() {
    echo "🚀 Starting integrated ALB + CloudFront deployment"
    echo ""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --certificate-arn)
                CERTIFICATE_ARN="$2"
                shift 2
                ;;
            --domain-name)
                DOMAIN_NAME="$2"
                shift 2
                ;;
            --stack-name)
                STACK_NAME="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --certificate-arn ARN    ACM certificate ARN for HTTPS"
                echo "  --domain-name DOMAIN     Custom domain name"
                echo "  --stack-name NAME        CloudFormation stack name (default: streamlit-integrated)"
                echo "  --region REGION          AWS region (default: us-west-2)"
                echo "  --help                   Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0"
                echo "  $0 --certificate-arn arn:aws:acm:us-west-2:123456789012:certificate/12345678-1234-1234-1234-123456789012"
                echo "  $0 --domain-name myapp.example.com --certificate-arn arn:aws:acm:us-west-2:123456789012:certificate/12345678-1234-1234-1234-123456789012"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Execute deployment steps
    check_aws_cli
    get_vpc_info
    get_ec2_info
    deploy_stack
    get_outputs
    
    echo ""
    log_success "Deployment script completed successfully!"
}

# Run main function
main "$@"