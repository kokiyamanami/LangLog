#!/bin/bash
set -e

BACKEND_PATH="/mnt/c/Users/yaman/OneDrive/デスクトップ/LangLog/LangLog/english-diary/backend"
FRONTEND_PATH="/mnt/c/Users/yaman/OneDrive/デスクトップ/LangLog/LangLog/english-diary/frontend"
ENV_FILE="${FRONTEND_PATH}/.env.production"
AWS_REGION="ap-northeast-1"
ECR_URI="389323710086.dkr.ecr.ap-northeast-1.amazonaws.com/langlog-backend:latest"

echo "=== Deploy Start ==="

echo "[1/4] Building Docker image..."
cd "$BACKEND_PATH"
docker build -t langlog-backend:latest -f Dockerfile.backend .

echo "[2/4] Pushing to ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "389323710086.dkr.ecr.${AWS_REGION}.amazonaws.com"
docker tag langlog-backend:latest "$ECR_URI"
docker push "$ECR_URI"

echo "[3/4] Updating ECS service..."
aws ecs update-service --cluster langlog-cluster --service langlog-service --force-new-deployment --region "$AWS_REGION" > /dev/null
echo "Waiting 90s for new task to start..."
sleep 90

echo "[4/4] Getting new task IP..."
TASK_ARN=$(aws ecs list-tasks --cluster langlog-cluster --region "$AWS_REGION" --query 'taskArns[0]' --output text)
echo "Task ARN: $TASK_ARN"

ENI_ID=$(aws ecs describe-tasks --cluster langlog-cluster --tasks "$TASK_ARN" --region "$AWS_REGION" --output json | python3 -c "
import sys, json
d = json.load(sys.stdin)
details = d['tasks'][0]['attachments'][0]['details']
eni = [x['value'] for x in details if x['name'] == 'networkInterfaceId'][0]
print(eni)
")
echo "ENI: $ENI_ID"

NEW_IP=$(aws ec2 describe-network-interfaces --network-interface-ids "$ENI_ID" --region "$AWS_REGION" --query 'NetworkInterfaces[0].Association.PublicIp' --output text)
echo "New IP: $NEW_IP"

echo "VITE_API_URL=http://${NEW_IP}:8000/api/v1" > "$ENV_FILE"
echo "Updated .env.production: VITE_API_URL=http://${NEW_IP}:8000/api/v1"

read -p "Deploy Frontend too? (y/n): " R
if [ "$R" = "y" ]; then
  echo "Building frontend..."
  cd "$FRONTEND_PATH"
  npm run build
  aws s3 sync dist s3://langlog-frontend-poc --region "$AWS_REGION" --delete
  echo "Frontend deployed!"
fi

echo ""
echo "=== Done! ==="
echo "API: http://${NEW_IP}:8000"
echo "Frontend: http://langlog-frontend-poc.s3-website.ap-northeast-1.amazonaws.com"
