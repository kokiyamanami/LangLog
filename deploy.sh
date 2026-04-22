#!/bin/bash
set -e

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
else
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file by copying .env.example:"
    echo "  cp .env.example .env"
    echo "Then update the values with your AWS credentials."
    exit 1
fi

# Validate required variables
required_vars=("AWS_ACCOUNT_ID" "AWS_REGION" "ECS_CLUSTER_NAME" "ECR_REPO_NAME")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set in .env file"
        exit 1
    fi
done

echo "🚀 FastAPI to ECS Deployment Script"
echo "===================================="
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "Repository: $ECR_REPO_NAME"
echo ""

# 1. Build Docker image
echo "📦 Building Docker image..."
docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# 2. Login to ECR
echo "🔐 Logging in to AWS ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# 3. Create ECR repository if it doesn't exist
echo "📝 Ensuring ECR repository exists..."
aws ecr create-repository \
  --repository-name ${ECR_REPO_NAME} \
  --region ${AWS_REGION} || echo "Repository already exists"

# 4. Tag the image for ECR
echo "🏷️  Tagging image for ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}

# 5. Push to ECR
echo "📤 Pushing image to ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}

# 6. Update ECS task definition
echo "📋 Updating ECS task definition..."
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json \
  --region ${AWS_REGION}

# 7. Update ECS service
echo "🔄 Updating ECS service..."
aws ecs update-service \
  --cluster ${ECS_CLUSTER_NAME} \
  --service ${ECS_SERVICE_NAME} \
  --task-definition ${ECS_TASK_FAMILY}:1 \
  --force-new-deployment \
  --region ${AWS_REGION}

echo "✅ Deployment complete!"
echo "Monitor the service: aws ecs describe-services --cluster ${ECS_CLUSTER_NAME} --services ${ECS_SERVICE_NAME} --region ${AWS_REGION}"
