#!/bin/bash

# High-speed deployment script for FastAPI Fargate Stack
set -e

echo "🚀 Starting high-speed deployment..."

# Set environment variables
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

# Navigate to infra directory
cd infra

# Activate virtual environment
source .venv/bin/activate || {
    echo "Creating virtual environment..."
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip --no-cache-dir
    pip install -r requirements.txt --no-cache-dir
}

echo "⚡ Running optimized CDK deployment..."

# Deploy with optimization flags
cdk deploy FastapiFargateCdkStack \
    --require-approval never \
    --app "python3 app.py" \
    --hotswap \
    --progress events \
    --concurrency 10

echo "📡 Getting service IP address..."

# Get the ECS service ARN and extract task ARN
SERVICE_ARN=$(aws ecs list-services --cluster fastapi-cluster --query 'serviceArns[0]' --output text)
TASK_ARN=$(aws ecs list-tasks --cluster fastapi-cluster --service-name "$SERVICE_ARN" --query 'taskArns[0]' --output text)

# Get the public IP of the task
PUBLIC_IP=$(aws ecs describe-tasks --cluster fastapi-cluster --tasks "$TASK_ARN" --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[0].Association.PublicIp' --output text)

echo "✅ Deployment completed!"
echo "🌐 API endpoint: http://$PUBLIC_IP"
echo "🏥 Health check: http://$PUBLIC_IP/health"

# Test the endpoint
echo "🔍 Testing endpoint..."
sleep 30  # Wait for service to be ready
curl -f "http://$PUBLIC_IP/health" && echo "✅ Service is healthy!" || echo "⚠️ Service not ready yet, please wait a moment"
