# LangLog AWS デプロイ完全ガイド

## 📋 目次

1. [前提条件](#前提条件)
2. [アーキテクチャ設計](#アーキテクチャ設計)
3. [AWS セットアップ手順](#awsセットアップ手順)
4. [デプロイ手順](#デプロイ手順)
5. [CI/CD パイプライン](#cicdパイプライン)
6. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必要なツール

- AWS アカウント（クレジットカード必須）
- AWS CLI v2
- Docker & Docker Compose
- Git

### インストール

```bash
# AWS CLI インストール
# Windows: https://awscli.amazonaws.com/AWSCLIV2.msi
# Mac: brew install awscli
# Linux: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

# AWS CLI 設定
aws configure
# 以下を入力：
# AWS Access Key ID: AKIA****
# AWS Secret Access Key: ****
# Default region: ap-northeast-1 (東京)
# Default output format: json
```

---

## アーキテクチャ設計

### 推奨構成（本番環境）

```
┌─────────────────────────────────────────────────────────┐
│                    Route 53 (DNS)                       │
│              langlog.example.com                        │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
   ┌────▼─────┐            ┌────────┴─┐
   │    S3    │            │   ALB    │
   │(Frontend)│            │ (Backend)│
   └──────────┘            └────┬─────┘
                                │
        ┌───────────────────────┘
        │
   ┌────▼──────────────┐
   │     ECS Tasks     │
   │ (FastAPI Container)
   │  - 2~3 instances  │
   └────┬──────────────┘
        │
    ┌───┴─────────┬─────────────┐
    │             │             │
┌───▼──┐    ┌────▼───┐    ┌───▼────┐
│ RDS  │    │ElastiCache  │ECR     │
│(DB)  │    │ (Redis)    │(Images)│
└──────┘    └────────┘    └────────┘
```

### 主要な AWS サービス

| サービス        | 用途               | 概要                |
| --------------- | ------------------ | ------------------- |
| **ECS**         | コンテナ実行       | FastAPI を実行      |
| **RDS**         | データベース       | PostgreSQL 管理     |
| **ElastiCache** | キャッシュ         | Redis インスタンス  |
| **ALB**         | ロードバランサー   | トラフィック分散    |
| **ECR**         | イメージレジストリ | Docker イメージ保存 |
| **S3**          | ファイル保存       | フロントエンド配信  |
| **CloudFront**  | CDN                | グローバル高速配信  |
| **CloudWatch**  | ログ・モニタリング | ログ保存・監視      |

---

## AWS セットアップ手順

### ステップ 1: IAM ユーザー作成

```bash
# AWS Management Console にログイン
# https://console.aws.amazon.com

# IAM → ユーザー → ユーザーを作成

# ユーザー名: github-actions-user
# アクセスタイプ: プログラムによるアクセス
# 権限: 以下のポリシーをアタッチ
  - AmazonECS_FullAccess
  - AmazonEC2ContainerRegistryFullAccess
  - AmazonRDSFullAccess
  - AWSCloudFormationFullAccess

# アクセスキーと シークレットキーを保存（重要！）
```

### ステップ 2: ECR リポジトリ作成

```bash
# AWS Management Console
# Elastic Container Registry → リポジトリ

# バックエンド用
リポジトリ名: langlog-api
イメージタグの可変性: 有効

# フロントエンド用
リポジトリ名: langlog-frontend
イメージタグの可変性: 有効
```

### ステップ 3: RDS インスタンス作成

```bash
# AWS Management Console
# RDS → データベース → データベースを作成

設定内容:
├─ エンジン: PostgreSQL 15.3
├─ テンプレート: 本番環境
├─ DBインスタンス識別子: langlog-db
├─ マスターユーザー: admin
├─ パスワード: (強力なパスワードを設定)
├─ DBインスタンスクラス: db.t3.micro（開発）or t3.small（本番）
├─ ストレージ: 20 GB（最小）
├─ マルチAZ: 有効（本番）
├─ パブリックアクセシビリティ: 無効
└─ バックアップ保持期間: 7 日

# セキュリティグループを設定
ルール: ポート 5432、ソース: ECS セキュリティグループ
```

### ステップ 4: ElastiCache クラスタ作成

```bash
# AWS Management Console
# ElastiCache → キャッシュクラスタ

設定内容:
├─ エンジン: Redis 7.0
├─ クラスタ名: langlog-redis
├─ ノードタイプ: cache.t3.micro
├─ ノード数: 1（開発）or 3（本番）
├─ ポート: 6379
├─ パラメータグループ: default
└─ セキュリティグループ: ポート 6379、ソース: ECS

# エンドポイントを記録（例：langlog-redis.xxxxx.ng.0001.apne1.cache.amazonaws.com）
```

### ステップ 5: ECS クラスタ作成

```bash
# AWS Management Console
# ECS → クラスタ → クラスタを作成

設定内容:
├─ クラスタ名: langlog-cluster
├─ VPC: デフォルト VPC
├─ サブネット: 2 個以上選択（異なるAZ）
└─ セキュリティグループ:
    ├─ ルール 1: ポート 8000（HTTP）、ソース: ALB SG
    └─ ルール 2: ポート 5432（自分自身）

# または AWS CloudFormation でテンプレートを使用（推奨）
```

### ステップ 6: ALB (Application Load Balancer) 作成

```bash
# AWS Management Console
# EC2 → ロードバランサー

設定内容:
├─ ロードバランサータイプ: Application Load Balancer
├─ 名前: langlog-alb
├─ VPC: クラスタと同じ
├─ リスナー: ポート 80 → ターゲットグループ
├─ ターゲットグループ名: langlog-api-tg
├─ プロトコル: HTTP
├─ ポート: 8000
└─ ヘルスチェック:
    ├─ パス: /api/v1/auth/me
    ├─ 間隔: 30 秒
    └─ タイムアウト: 5 秒

# エンドポイント URL を記録（例：langlog-alb-1234567890.ap-northeast-1.elb.amazonaws.com）
```

### ステップ 7: ECS タスク定義作成

```bash
# AWS Management Console
# ECS → タスク定義 → 新しいリビジョンを作成

# または CLI でテンプレートから作成
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json
```

**ecs-task-definition.json テンプレート**:

```json
{
  "family": "langlog-api-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "langlog-api",
      "image": "ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/langlog-api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://admin:PASSWORD@langlog-db.xxxxx.ap-northeast-1.rds.amazonaws.com:5432/langlog"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://langlog-redis.xxxxx.ng.0001.apne1.cache.amazonaws.com:6379"
        },
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/langlog-api",
          "awslogs-region": "ap-northeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### ステップ 8: ECS サービス作成

```bash
# AWS Management Console
# ECS → クラスタ → サービス → サービスを作成

設定内容:
├─ タスク定義: langlog-api-task
├─ サービス名: langlog-api-service
├─ レプリカ数: 2（最小）
├─ ロードバランサー: ALB
├─ ターゲットグループ: langlog-api-tg
└─ オートスケーリング:
    ├─ 最小タスク数: 2
    ├─ 最大タスク数: 4
    └─ CPU ターゲット: 70%
```

### ステップ 9: S3 + CloudFront（フロントエンド）

```bash
# S3 バケット作成
aws s3 mb s3://langlog-frontend-ACCOUNT_ID --region ap-northeast-1

# 静的ウェブサイトホスティング有効化
aws s3 website s3://langlog-frontend-ACCOUNT_ID/ \
  --index-document index.html \
  --error-document index.html

# CloudFront ディストリビューション作成
# AWS Management Console → CloudFront

設定内容:
├─ オリジンドメイン: S3 バケット
├─ S3 アクセス: OAI (Origin Access Identity)
├─ デフォルトルートオブジェクト: index.html
└─ ビューアーポリシー: HTTPS リダイレクト
```

---

## デプロイ手順

### ステップ 1: ECR にログイン

```bash
# AWS アカウントID を取得
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# ECR ログイン
aws ecr get-login-password --region ap-northeast-1 | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com
```

### ステップ 2: バックエンドイメージをビルド・プッシュ

```bash
cd english-diary

# イメージ情報を設定
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY=$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com
IMAGE_TAG=$(git rev-parse --short HEAD)

# ビルド
docker build -f Dockerfile.backend -t $ECR_REGISTRY/langlog-api:$IMAGE_TAG .
docker tag $ECR_REGISTRY/langlog-api:$IMAGE_TAG $ECR_REGISTRY/langlog-api:latest

# プッシュ
docker push $ECR_REGISTRY/langlog-api:$IMAGE_TAG
docker push $ECR_REGISTRY/langlog-api:latest

echo "Backend image pushed: $ECR_REGISTRY/langlog-api:$IMAGE_TAG"
```

### ステップ 3: フロントエンドイメージをビルド・プッシュ

```bash
cd english-diary/frontend

# ビルド
npm run build

# イメージ作成
docker build -f Dockerfile -t $ECR_REGISTRY/langlog-frontend:$IMAGE_TAG .
docker tag $ECR_REGISTRY/langlog-frontend:$IMAGE_TAG $ECR_REGISTRY/langlog-frontend:latest

# プッシュ
docker push $ECR_REGISTRY/langlog-frontend:$IMAGE_TAG
docker push $ECR_REGISTRY/langlog-frontend:latest
```

### ステップ 4: ECS タスクを更新

```bash
# タスク定義を登録
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json

# サービスを更新
aws ecs update-service \
  --cluster langlog-cluster \
  --service langlog-api-service \
  --task-definition langlog-api-task:REVISION \
  --force-new-deployment
```

### ステップ 5: フロントエンドをデプロイ

```bash
# S3 にアップロード
aws s3 sync dist/ s3://langlog-frontend-$ACCOUNT_ID/ --delete

# CloudFront キャッシュをクリア
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?Origins.Items[0].DomainName=='langlog-frontend-$ACCOUNT_ID.s3.amazonaws.com'].Id" \
  --output text)

aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"

echo "Frontend deployed!"
```

---

## CI/CD パイプライン

### GitHub Actions ワークフロー設定

**.github/workflows/deploy-aws.yml**:

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  AWS_REGION: ap-northeast-1

jobs:
  deploy:
    runs-on: ubuntu-latest

    permissions:
      contents: read
      id-token: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        run: |
          aws ecr get-login-password --region ${{ env.AWS_REGION }} | \
            docker login --username AWS --password-stdin ${{ steps.login-ecr.outputs.registry }}

      - name: Build and push backend image
        run: |
          docker build -f Dockerfile.backend -t ${{ steps.login-ecr.outputs.registry }}/langlog-api:${{ github.sha }} .
          docker push ${{ steps.login-ecr.outputs.registry }}/langlog-api:${{ github.sha }}

      - name: Build and push frontend image
        run: |
          docker build -f frontend/Dockerfile -t ${{ steps.login-ecr.outputs.registry }}/langlog-frontend:${{ github.sha }} frontend/
          docker push ${{ steps.login-ecr.outputs.registry }}/langlog-frontend:${{ github.sha }}

      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster langlog-cluster \
            --service langlog-api-service \
            --task-definition langlog-api-task \
            --force-new-deployment

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install dependencies
        run: cd english-diary/frontend && npm ci

      - name: Build
        run: cd english-diary/frontend && npm run build

      - name: Deploy to S3
        run: |
          aws s3 sync english-diary/frontend/dist/ s3://langlog-frontend-${{ secrets.AWS_ACCOUNT_ID }}/ --delete

      - name: Invalidate CloudFront
        run: |
          DISTRIBUTION_ID=${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }}
          aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

### GitHub Secrets を設定

AWS Management Console または CLI で：

```bash
# GitHub リポジトリ設定 → Secrets and variables → Actions

AWS_ACCESS_KEY_ID=AKIA****
AWS_SECRET_ACCESS_KEY=****
AWS_ACCOUNT_ID=123456789
CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC
```

---

## トラブルシューティング

### ECS タスクが起動しない

```bash
# ログを確認
aws logs tail /ecs/langlog-api --follow

# タスク詳細を確認
aws ecs describe-tasks \
  --cluster langlog-cluster \
  --tasks <TASK_ARN>
```

### データベース接続エラー

```bash
# セキュリティグループを確認
aws ec2 describe-security-groups \
  --group-ids sg-xxxxx

# RDS エンドポイントを確認
aws rds describe-db-instances \
  --db-instance-identifier langlog-db
```

### Redis 接続エラー

```bash
# ElastiCache ノードステータスを確認
aws elasticache describe-cache-clusters \
  --cache-cluster-id langlog-redis

# セキュリティグループを確認
aws elasticache describe-cache-security-groups
```

### CloudFront キャッシュ問題

```bash
# キャッシュをクリア
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"

# ディストリビューション詳細
aws cloudfront get-distribution --id E1234567890ABC
```

---

## コスト削減のコツ

### 開発環境

```
- ECS: t3.micro（無料枠内）
- RDS: t3.micro
- ElastiCache: t3.micro
- 月額目安: $20-50
```

### 本番環境

```
- ECS: t3.small ✕ 2-4 インスタンス
- RDS: t3.small with マルチAZ
- ElastiCache: t3.small ✕ 3 ノード
- ALB: 時間単価 $0.0225
- 月額目安: $200-500
```

### コスト最適化

1. **Auto Scaling を設定**

   ```bash
   CPU > 70% → スケールアップ
   CPU < 30% → スケールダウン
   ```

2. **リザーブドインスタンス購入**
   - 1 年契約で 30% 割引
   - 3 年契約で 50% 割引

3. **不使用リソースの削除**
   - 開発環境は使用時のみ起動
   - CloudWatch ログは 30 日保持

---

## 次のステップ

- [ ] AWS アカウント作成
- [ ] IAM ユーザー作成
- [ ] ECR リポジトリ作成
- [ ] RDS インスタンス作成
- [ ] ElastiCache クラスタ作成
- [ ] ECS クラスタ作成
- [ ] ALB 作成
- [ ] タスク定義作成
- [ ] サービス作成
- [ ] GitHub Secrets 設定
- [ ] CI/CD パイプライン設定
- [ ] デプロイ実行
- [ ] ドメイン設定（Route 53）

---

**質問や問題が発生した場合は、AWS サポートまたは AWS コミュニティフォーラムを利用してください。**
