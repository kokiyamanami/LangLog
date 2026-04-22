#!/bin/bash
set -e

# AWS CI/CD Setup Script
# This script sets up the necessary IAM role for GitHub Actions to deploy to ECS

AWS_ACCOUNT_ID=$(grep AWS_ACCOUNT_ID .env | cut -d= -f2)
AWS_REGION=$(grep AWS_REGION .env | cut -d= -f2)

echo "🔐 Setting up GitHub Actions IAM Role"
echo "====================================="
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo ""

# Create trust policy for GitHub Actions
cat > github-actions-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::$AWS_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USER/YOUR_REPO:*"
        }
      }
    }
  ]
}
EOF

# Create IAM role for GitHub Actions
echo "📋 Creating IAM role for GitHub Actions..."
aws iam create-role \
  --role-name github-actions-role \
  --assume-role-policy-document file://github-actions-trust-policy.json \
  --region $AWS_REGION || echo "Role already exists"

# Create inline policy for ECR and ECS
cat > github-actions-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "arn:aws:ecr:$AWS_REGION:$AWS_ACCOUNT_ID:repository/langlog-api"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:DescribeTask",
        "ecs:RegisterTaskDefinition"
      ],
      "Resource": [
        "arn:aws:ecs:$AWS_REGION:$AWS_ACCOUNT_ID:service/langlog-cluster/langlog-api-service",
        "arn:aws:ecs:$AWS_REGION:$AWS_ACCOUNT_ID:task-definition/langlog-api-task:*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": [
        "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
        "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskRole"
      ]
    }
  ]
}
EOF

echo "📝 Attaching policies to role..."
aws iam put-role-policy \
  --role-name github-actions-role \
  --policy-name github-actions-policy \
  --policy-document file://github-actions-policy.json \
  --region $AWS_REGION

echo "✅ GitHub Actions IAM role setup complete!"
echo ""
echo "Next steps:"
echo "1. Update github-actions-trust-policy.json with your GitHub repository:"
echo "   - YOUR_GITHUB_USER: your GitHub username or organization"
echo "   - YOUR_REPO: your repository name"
echo ""
echo "2. Add the following secrets to your GitHub repository:"
echo "   - AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"
echo ""
echo "3. Go to https://github.com/YOUR_USER/YOUR_REPO/settings/secrets/actions"
echo "   and add the secret."
echo ""
echo "Cleanup:"
rm -f github-actions-trust-policy.json github-actions-policy.json
