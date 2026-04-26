# LangLog PoC デプロイメント完全ガイド

## 📋 目次

1. [PoC について](#poc-について)
2. [アーキテクチャ](#アーキテクチャ)
3. [前提条件](#前提条件)
4. [AWS セットアップ](#aws-セットアップ)
5. [ローカルセットアップ](#ローカルセットアップ)
6. [デプロイ手順](#デプロイ手順)
7. [トラブルシューティング](#トラブルシューティング)
8. [本番移行ロードマップ](#本番移行ロードマップ)

---

## PoC について

### 🎯 PoC（Proof of Concept）とは

```
「概念実証」
→ 実現可能性を確認するための初期段階
→ サービス名も仕様も固まってない
→ 小規模ユーザーでテスト
```

### 📊 PoC vs MVP vs 本番

| フェーズ | 目的         | ユーザー   | 月額      | 要件       |
| -------- | ------------ | ---------- | --------- | ---------- |
| **PoC**  | 概念実証     | 開発チーム | $35       | 動けば OK  |
| **MVP**  | 最小限の提供 | 100-1K     | $50-100   | 安定性・UX |
| **本番** | 提供開始     | 1K+        | $100-500+ | 高可用性   |

### ✅ LangLog PoC の特徴

```
✅ ECS 1 タスク（複数コンテナ）
✅ RDS db.t3.micro
✅ Fargate で自動管理
✅ GitHub Actions 自動デプロイ
✅ 月額 $32-35/月
✅ ALB・ドメイン不要
✅ ECS タスク IP で直接アクセス
```

---

## アーキテクチャ

### 📐 PoC 構成図

```
┌────────────────────────────────────────┐
│ ECS タスク 1 個（Fargate）              │
│ IP: 172.31.10.50                       │
│                                        │
│ ┌──────────────────────────────────┐  │
│ │ FastAPI コンテナ                 │  │
│ │ ポート: 8000                     │  │
│ │ - uvicorn                        │  │
│ │ - Python 3.11                    │  │
│ │ - requirements.txt               │  │
│ └──────────────────────────────────┘  │
│                                        │
│ ┌──────────────────────────────────┐  │
│ │ Nginx コンテナ                   │  │
│ │ ポート: 80                       │  │
│ │ - React（dist/）                 │  │
│ │ - FastAPI プロキシ設定           │  │
│ └──────────────────────────────────┘  │
│                                        │
│ 内部通信:                              │
│ Nginx → fastapi:8000                   │
└────────────────────────────────────────┘
         ↓
    [RDS PostgreSQL]
    db.t3.micro

ユーザーアクセス:
http://172.31.10.50/           ← フロントエンド（Nginx）
http://172.31.10.50/api/v1/    ← API（FastAPI）
http://172.31.10.50/docs       ← FastAPI ドキュメント
```

### 🔄 デプロイフロー

```
① Git push to main
   ↓
② GitHub Actions 実行
   ├─ バックエンドテスト
   ├─ FastAPI イメージビルド → ECR プッシュ
   ├─ フロントエンドビルド
   ├─ Nginx イメージビルド → ECR プッシュ
   └─ ECS タスク更新
   ↓
③ ECS が新イメージ実行
   ├─ FastAPI コンテナ起動
   └─ Nginx コンテナ起動
   ↓
④ ユーザーアクセス可能
   http://172.31.10.50/
```

---

## 前提条件

### 必要なアカウント・ツール

```
✅ AWS アカウント（クレジットカード必須）
✅ GitHub アカウント
✅ Docker デスクトップ
✅ AWS CLI v2
✅ Node.js 18+
✅ Python 3.11+
```

### インストール確認

```bash
# Docker
docker --version
# Docker version 20.10+

# AWS CLI
aws --version
# aws-cli/2.x.x

# Node.js
node --version
# v18.x.x

# Python
python --version
# Python 3.11+
```

---

## AWS セットアップ

### ステップ 1: AWS IAM ユーザー作成

```bash
# AWS Management Console
# https://console.aws.amazon.com/iam/

1. ユーザーを作成
   名前: github-actions-deploy

2. アクセスキーを生成
   → CSV ダウンロード・保存

3. 以下の権限をアタッチ:
   ✅ AmazonECS_FullAccess
   ✅ AmazonEC2ContainerRegistryFullAccess
   ✅ AmazonRDSFullAccess
```

### ステップ 2: ECR リポジトリ作成

```bash
# AWS Management Console → ECR

# バックエンド用
aws ecr create-repository --repository-name langlog-api --region ap-northeast-1

# フロントエンド用
aws ecr create-repository --repository-name langlog-frontend --region ap-northeast-1

# 確認
aws ecr describe-repositories --region ap-northeast-1
```

### ステップ 3: RDS インスタンス作成

```bash
# AWS Management Console → RDS → データベース

設定:
├─ エンジン: PostgreSQL 15
├─ テンプレート: 無料利用枠
├─ DB インスタンス識別子: langlog-db
├─ マスターユーザー: admin
├─ パスワード: (強力なパスワード)
├─ DB インスタンスクラス: db.t3.micro
├─ ストレージ: 20GB
├─ パブリックアクセシビリティ: 無効
└─ バックアップ保持期間: 7 日
```

### ステップ 4: ECS クラスタ作成

```bash
# AWS Management Console → ECS → クラスタ

aws ecs create-cluster \
  --cluster-name langlog-cluster \
  --region ap-northeast-1

# 確認
aws ecs describe-clusters \
  --clusters langlog-cluster \
  --region ap-northeast-1
```

### ステップ 5: CloudWatch ロググループ作成

```bash
aws logs create-log-group \
  --log-group-name /ecs/langlog-api \
  --region ap-northeast-1

aws logs create-log-group \
  --log-group-name /ecs/langlog-frontend \
  --region ap-northeast-1
```

---

## ローカルセットアップ

### ステップ 1: AWS CLI 設定

```bash
aws configure

# 入力:
AWS Access Key ID: AKIA****
AWS Secret Access Key: ****
Default region: ap-northeast-1
Default output format: json
```

### ステップ 2: ECR ログイン

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ecr get-login-password --region ap-northeast-1 | \
  docker login --username AWS --password-stdin \
  $ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com
```

### ステップ 3: GitHub Secrets 設定

```bash
# リポジトリ Settings → Secrets and variables → Actions

gh secret set AWS_ACCOUNT_ID --body "$ACCOUNT_ID"
gh secret set AWS_ACCESS_KEY_ID --body "AKIA****"
gh secret set AWS_SECRET_ACCESS_KEY --body "****"

# 確認
gh secret list
```

---

## デプロイ手順

### 方法 1: 自動デプロイ（GitHub Actions）

#### ステップ 1: ファイル配置確認

```
english-diary/
├─ backend/
│  ├─ Dockerfile.backend ← 必須
│  ├─ main.py
│  └─ requirements.txt
├─ frontend/
│  ├─ Dockerfile.frontend ← 必須
│  └─ src/
├─ nginx.conf ← 必須
├─ ecs-task-definition.json ← 必須
└─ .github/workflows/
   └─ deploy-mvp.yml ← 必須
```

#### ステップ 2: Main ブランチに push

```bash
cd english-diary

git add -A
git commit -m "feat: PoC deployment setup (multi-container)"
git push origin main

# GitHub Actions が自動実行開始
```

#### ステップ 3: Actions 実行確認

```bash
# GitHub Actions タブ → Deploy MVP Workflow

状態確認:
✅ Test ジョブ: 5 分
✅ Build Backend: 3 分
✅ Build Frontend: 3 分
✅ Update ECS: 2 分
───────────────────────
合計: 13 分程度

完了したら:
http://172.31.10.50/
```

### 方法 2: 手動デプロイ（ローカル）

#### ステップ 1: バックエンドイメージビルド

```bash
cd english-diary

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY=$ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com

docker build -f backend/Dockerfile.backend \
  -t $ECR_REGISTRY/langlog-api:latest \
  backend/

docker push $ECR_REGISTRY/langlog-api:latest
```

#### ステップ 2: フロントエンドイメージビルド

```bash
docker build -f frontend/Dockerfile.frontend \
  -t $ECR_REGISTRY/langlog-frontend:latest \
  frontend/

docker push $ECR_REGISTRY/langlog-frontend:latest
```

#### ステップ 3: ECS タスク定義更新

```bash
# JSON ファイルで ACCOUNT_ID を置き換え
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" ecs-task-definition.json

aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json

# サービス作成（初回のみ）
aws ecs create-service \
  --cluster langlog-cluster \
  --service-name langlog-poc-service \
  --task-definition langlog-poc-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-public-xxxxx],securityGroups=[sg-ecs-xxxxx],assignPublicIp=ENABLED}"

# サービス更新（2 回目以降）
aws ecs update-service \
  --cluster langlog-cluster \
  --service langlog-poc-service \
  --task-definition langlog-poc-task \
  --force-new-deployment
```

#### ステップ 4: タスク IP 確認

```bash
TASK_ARN=$(aws ecs list-tasks \
  --cluster langlog-cluster \
  --service-name langlog-poc-service \
  --query 'taskArns[0]' --output text)

aws ecs describe-tasks \
  --cluster langlog-cluster \
  --tasks $TASK_ARN \
  --query 'tasks[0].attachments[?type==`ElasticNetworkInterface`].details[?name==`publicIpv4Address`].value' \
  --output text

# 例: 54.123.45.67
# アクセス: http://54.123.45.67/
```

---

## ローカルテスト（docker-compose）

### docker-compose.yml

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: langlog
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./english-diary/backend
      dockerfile: Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://admin:devpassword@postgres:5432/langlog
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./english-diary/backend:/app

  frontend:
    build:
      context: ./english-diary/frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

### ローカルテスト実行

```bash
# イメージビルド・サービス起動
docker-compose up --build

# 確認
curl http://localhost/               # フロントエンド
curl http://localhost/api/v1/auth/me # API

# ログ確認
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止
docker-compose down
```

---

## トラブルシューティング

### ECS タスクが起動しない

```bash
# ログ確認
aws logs tail /ecs/langlog-api --follow

# タスク詳細
aws ecs describe-tasks \
  --cluster langlog-cluster \
  --tasks <TASK_ARN>

# よくある原因:
❌ Docker イメージが見つからない
   → ECR に正しくプッシュされているか確認

❌ RDS 接続失敗
   → DATABASE_URL が正しいか確認
   → セキュリティグループ設定確認

❌ メモリ不足
   → ECS タスク定義の CPU/メモリ増加
```

### Nginx が FastAPI に接続できない

```
原因: nginx.conf の `upstream fastapi` 設定

修正:
upstream fastapi {
    server fastapi:8000;  ← コンテナ名が重要
}

ECS タスク定義で links 設定:
"links": ["fastapi:fastapi"]  ← コンテナ名を指定
```

### API エラーが返される

```bash
# FastAPI ドキュメント確認
http://172.31.10.50/docs

# ログで詳細確認
docker-compose logs backend

# よくある原因:
❌ DB マイグレーション未実行
❌ 環境変数未設定
❌ 認証トークン期限切れ
```

---

## 本番移行ロードマップ

### Phase 1: PoC（今ここ）

```
月額: $35/月
構成: ECS 1 タスク + RDS micro
方針: 動作確認・ユーザーテスト
```

### Phase 2: MVP（ユーザー 100+ 時）

```
月額: $60-100/月
構成変更:
  ✅ ECS 2 タスク（冗長性）
  ✅ RDS t3.small（性能向上）
  ✅ ALB 追加（負荷分散）
  ✅ CloudWatch アラート

やること:
  - セキュリティ強化
  - ロギング監視
  - 自動スケール設定
```

### Phase 3: 本番（ユーザー 1K+ 時）

```
月額: $150-300/月
構成変更:
  ✅ ECS 3-4 タスク（高可用性）
  ✅ RDS t3.medium + マルチAZ
  ✅ ElastiCache 追加
  ✅ CloudFront CDN
  ✅ Route 53 ドメイン
  ✅ WAF セキュリティ

やること:
  - SLA 設定
  - 災害対策
  - 本格的な監視
```

---

## チェックリスト

### デプロイ前確認

```
□ AWS IAM ユーザー作成
□ ECR リポジトリ作成（langlog-api, langlog-frontend）
□ RDS インスタンス起動
□ ECS クラスタ作成
□ CloudWatch ロググループ作成
□ AWS CLI ログイン
□ GitHub Secrets 設定
□ docker-compose でローカルテスト成功
```

### デプロイ後確認

```
□ GitHub Actions 実行完了
□ ECS タスク起動確認
□ http://タスクIP/ でアクセス可能
□ フロントエンド表示確認
□ /api/v1/auth/me で API レスポンス確認
□ /docs で FastAPI ドキュメント表示確認
□ CloudWatch ログに出力確認
```

---

## 次のステップ

1. **AWS セットアップ**: 上記「AWS セットアップ」セクション実行
2. **ローカル設定**: AWS CLI, GitHub Secrets 設定
3. **ローカルテスト**: docker-compose で動作確認
4. **デプロイ**: GitHub Actions で自動デプロイ実行
5. **アクセス確認**: タスク IP で確認
6. **本番化検討**: ユーザーテスト結果に基づいて段階的アップグレード

---

## 参考資料

- [AWS ECS on Fargate](https://docs.aws.amazon.com/ecs/latest/developerguide/what-is-fargate.html)
- [AWS RDS PostgreSQL](https://docs.aws.amazon.com/rds/latest/userguide/USER_PostgreSQL.html)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Compose](https://docs.docker.com/compose/)

---

**質問や問題が発生した場合は、AWS ドキュメントまたはコミュニティを参照してください。**
