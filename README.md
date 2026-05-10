# LangLog API - FastAPI to ECS Deployment Guide

## 🚀 デプロイ後のアクセス方法

ECS Fargate はデプロイのたびに **パブリック IP が変わります**。
以下のコマンドで現在の IP を確認してください。

```bash
# 現在のパブリック IP を取得（WSL / Linux / Mac で実行）
TASK_ARN=$(aws ecs list-tasks \
  --cluster langlog-cluster \
  --service-name langlog-service \
  --region ap-northeast-1 \
  --query 'taskArns[0]' --output text)

ENI_ID=$(aws ecs describe-tasks \
  --cluster langlog-cluster \
  --tasks $TASK_ARN \
  --region ap-northeast-1 \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text)

PUBLIC_IP=$(aws ec2 describe-network-interfaces \
  --network-interface-ids $ENI_ID \
  --region ap-northeast-1 \
  --query 'NetworkInterfaces[0].Association.PublicIp' \
  --output text)

echo "🌐 アクセスURL: http://$PUBLIC_IP/"
echo "📖 API Docs:   http://$PUBLIC_IP/docs"
echo "❤️  Health:     http://$PUBLIC_IP/health"
```

| エンドポイント        | 内容                  |
| --------------------- | --------------------- |
| `http://<IP>/`        | React フロントエンド  |
| `http://<IP>/docs`    | Swagger UI（API仕様） |
| `http://<IP>/health`  | ヘルスチェック        |
| `http://<IP>/api/v1/` | FastAPI バックエンド  |

> **補足**: GitHub Actions のデプロイログ末尾にも URL が出力されます。

---

## プロジェクト構成

```
.
├── main.py                          # FastAPI アプリケーション
├── requirements.txt                 # Python 依存パッケージ
├── Dockerfile                       # Docker イメージ定義
├── docker-compose.yml              # ローカル開発用
├── .env.example                     # 環境変数テンプレート
├── ecs-task-definition.json        # ECS タスク定義
├── deploy.sh                        # 手動デプロイスクリプト
├── setup-github-actions.sh          # GitHub Actions 設定スクリプト
├── .github/
│   └── workflows/
│       ├── deploy.yml              # CI/CD デプロイパイプライン
│       └── test.yml                # テスト実行パイプライン
├── tests/
│   └── test_main.py                # ユニットテスト
└── README.md                        # このファイル
```

## ステップ 1: ローカル開発環境のセットアップ

### 前提条件

- Docker がインストールされていること
- Docker Compose がインストールされていること
- Python 3.11+ がインストールされていること

### 開発環境の起動

```bash
# Docker Compose でローカルで実行
docker-compose up

# または直接実行
python -m uvicorn main:app --reload
```

アクセス: http://localhost:8000
API ドキュメント: http://localhost:8000/docs

## ステップ 2: AWS 環境の準備

### 2.1 IAM ロールの作成

**ecsTaskExecutionRole** - タスク実行用（AWS側の操作）

```bash
aws iam create-role --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# ポリシーをアタッチ
aws iam attach-role-policy --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

**ecsTaskRole** - アプリケーション用（アプリが必要とするAWSリソースへのアクセス）

```bash
aws iam create-role --role-name ecsTaskRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'
```

### 2.2 ECR（Elastic Container Registry）のセットアップ

```bash
# ECR リポジトリを作成
aws ecr create-repository \
  --repository-name langlog-api \
  --region ap-northeast-1
```

### 2.3 ECS クラスターの作成

```bash
# Fargate クラスターを作成
aws ecs create-cluster \
  --cluster-name langlog-cluster \
  --region ap-northeast-1
```

### 2.4 CloudWatch Logs グループを作成

```bash
aws logs create-log-group \
  --log-group-name /ecs/langlog-api \
  --region ap-northeast-1
```

## ステップ 3: Docker イメージのビルドと ECR へのプッシュ

### 3.0 環境ファイルの作成

```bash
# テンプレートからコピー
cp .env.example .env

# .env を編集してAWSアカウントIDなどを設定
# AWS_ACCOUNT_ID=123456789012
# AWS_REGION=ap-northeast-1
# など
```

```bash
# Docker イメージをビルド
docker build -t langlog-api:latest .

# AWS ECR にログイン
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# イメージにタグを付与
docker tag langlog-api:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/langlog-api:latest

# ECR にプッシュ
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/langlog-api:latest
```

## ステップ 4: ECS タスク定義の登録

### タスク定義ファイルの準備

`ecs-task-definition.json` を編集します。`.env` ファイルから情報を取得して置き換えます：

```bash
# スクリプトで自動置換（推奨）
AWS_ACCOUNT_ID=$(grep AWS_ACCOUNT_ID .env | cut -d= -f2)
AWS_REGION=$(grep AWS_REGION .env | cut -d= -f2)

sed -i "s/\[AWS_ACCOUNT_ID\]/$AWS_ACCOUNT_ID/g" ecs-task-definition.json
sed -i "s/\[REGION\]/$AWS_REGION/g" ecs-task-definition.json
```

または手動で編集：

- `[AWS_ACCOUNT_ID]` → .env の AWS_ACCOUNT_ID 値
- `[REGION]` → .env の AWS_REGION 値

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json \
  --region ap-northeast-1
```

## ステップ 5: ECS サービスの作成と起動

### VPC とセキュリティグループの確認

```bash
# VPC と subnet を確認
aws ec2 describe-vpcs --region ap-northeast-1

# セキュリティグループを作成（ポート 8000 を許可）
aws ec2 create-security-group \
  --group-name langlog-sg \
  --description "Security group for LangLog API" \
  --region ap-northeast-1

# インバウンドルールを追加
aws ec2 authorize-security-group-ingress \
  --group-name langlog-sg \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0 \
  --region ap-northeast-1
```

### ECS サービスの作成

```bash
aws ecs create-service \
  --cluster langlog-cluster \
  --service-name langlog-api-service \
  --task-definition langlog-api-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --region ap-northeast-1
```

## ステップ 6: デプロイスクリプトの実行（初回以降）

```bash
# 1. .env ファイルを作成（初回のみ）
cp .env.example .env

# 2. .env を編集して AWS認証情報を設定
nano .env
# または
# AWS_ACCOUNT_ID=123456789012
# AWS_REGION=ap-northeast-1
# など

# 3. スクリプトに実行権限を付与
chmod +x deploy.sh

# 4. デプロイを実行（.env から自動で変数を読み込む）
./deploy.sh
```

デプロイスクリプトが .env ファイルから自動で環境変数を読み込むため、環境変数を手動で設定する必要はありません。

## 監視とログ確認

```bash
# ECS サービスの状態を確認
aws ecs describe-services \
  --cluster langlog-cluster \
  --services langlog-api-service \
  --region ap-northeast-1

# CloudWatch ログを確認
aws logs tail /ecs/langlog-api --follow --region ap-northeast-1
```

## API テスト

### ヘルスチェック

```bash
curl http://[ECS_PUBLIC_IP]:8000/health
```

### API ドキュメント

ECS のパブリック IP にアクセス：

```
http://[ECS_PUBLIC_IP]:8000/docs
```

## トラブルシューティング

### イメージが見つからない

```bash
# ECR にイメージが存在するか確認
aws ecr describe-images \
  --repository-name langlog-api \
  --region ap-northeast-1
```

### タスクが起動しない

```bash
# タスクの詳細を確認
aws ecs describe-tasks \
  --cluster langlog-cluster \
  --tasks [TASK_ARN] \
  --region ap-northeast-1
```

### ログを確認

```bash
aws logs get-log-events \
  --log-group-name /ecs/langlog-api \
  --log-stream-name [STREAM_NAME] \
  --region ap-northeast-1
```

## 本番環境への推奨設定

1. **Load Balancer の追加** - ALB（Application Load Balancer）を使用
2. **オートスケーリング** - タスク数を自動調整
3. **環境変数** - Secrets Manager または Systems Manager Parameter Store を使用
4. **ログ管理** - CloudWatch Logs への統合
5. **監視** - CloudWatch メトリクスとアラーム

## CI/CD パイプラインの設定（GitHub Actions）

### GitHub Actions の初期設定

1. **GitHub OIDC Provider をセットアップ**

```bash
# .env ファイルから環境変数を読み込む
source .env

# GitHub Actions用のIAMロールを設定
chmod +x setup-github-actions.sh
./setup-github-actions.sh
```

2. **GitHub リポジトリに環境情報を追加**

リポジトリの `Settings > Secrets and variables > Actions` で以下を設定：

| Secret 名      | 値                      |
| -------------- | ----------------------- |
| AWS_ACCOUNT_ID | あなたのAWSアカウントID |

3. **GitHub リポジトリに環境変数を追加**

リポジトリの `Settings > Variables > Repository variables` で以下を設定：

| Variable 名      | 値                  |
| ---------------- | ------------------- |
| AWS_REGION       | ap-northeast-1      |
| ECS_CLUSTER_NAME | langlog-cluster     |
| ECS_SERVICE_NAME | langlog-api-service |
| ECS_TASK_FAMILY  | langlog-api-task    |

### 自動パイプラインの動作

#### テストパイプライン (`test.yml`)

- **トリガー**: Push または PR が main/develop にマージされた時
- **実行内容**:
  1. Python 3.11 環境をセットアップ
  2. 依存パッケージをインストール
  3. `pytest` でユニットテストを実行
  4. カバレッジレポートを Codecov にアップロード

```bash
# ローカルでテストを実行
pytest tests/ -v --cov=. --cov-report=html
```

#### デプロイパイプライン (`deploy.yml`)

- **トリガー**: main ブランチへの Push または手動実行（`workflow_dispatch`）
- **実行内容**:
  1. テストを実行
  2. Dockerイメージをビルド
  3. ECR にプッシュ
  4. ECS タスク定義を更新
  5. ECS サービスを自動デプロイ

### パイプラインの監視

GitHub リポジトリの `Actions` タブで実行状況を確認できます。

デプロイの詳細ログ：

```bash
# 本番環境のサービス状態を確認
aws ecs describe-services \
  --cluster langlog-cluster \
  --services langlog-api-service \
  --region ap-northeast-1

# ログを確認
aws logs tail /ecs/langlog-api --follow --region ap-northeast-1
```

### GitHub Actions のトラブルシューティング

**IAM ロール認証エラー**

```bash
# GitHub OIDC プロバイダーが作成されているか確認
aws iam list-open-id-connect-providers --region ap-northeast-1

# trust policy を再度実行
./setup-github-actions.sh
```

**Secrets が見つからない**

```
Settings > Secrets and variables > Actions で設定を確認
```

## 参考リンク

- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
- [AWS ECS ドキュメント](https://docs.aws.amazon.com/ja_jp/ecs/)
- [Docker ドキュメント](https://docs.docker.com/)
