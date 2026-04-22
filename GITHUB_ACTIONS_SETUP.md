# GitHub Actions 設定ガイド

このガイドでは、GitHub Actions を使用した自動テスト・デプロイパイプラインを設定します。

## 前提条件

- GitHub にリポジトリを作成済み
- AWS アカウントを持っている
- AWS CLI が設定済み

## ステップ 1: GitHub OIDC プロバイダーの設定

AWS から GitHub に信頼できるプロバイダーとして認識されるようにします。

```bash
# 1. GitHub OIDC プロバイダーを登録（初回のみ）
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --region ap-northeast-1
```

## ステップ 2: GitHub Actions 用 IAM ロールの作成

```bash
# setup-github-actions.sh を実行（.env ファイルが必要）
chmod +x setup-github-actions.sh
./setup-github-actions.sh
```

このスクリプトが以下を自動で実行します：

- GitHub Actions 用 IAM ロールを作成
- ECR へのプッシュ権限を付与
- ECS へのデプロイ権限を付与

## ステップ 3: GitHub リポジトリに Secrets を追加

GitHub リポジトリの `Settings > Secrets and variables > Actions` に以下を追加：

### Secrets（秘密にする値）

```
AWS_ACCOUNT_ID = 123456789012
```

### Repository Variables（公開して良い値）

```
AWS_REGION = ap-northeast-1
ECS_CLUSTER_NAME = langlog-cluster
ECS_SERVICE_NAME = langlog-api-service
ECS_TASK_FAMILY = langlog-api-task
```

### 設定方法

1. GitHub リポジトリにアクセス
2. `Settings` をクリック
3. 左側の `Secrets and variables` > `Actions` をクリック
4. `New repository secret` ボタンをクリック
5. Name と Value を入力して保存

## ステップ 4: setup-github-actions.sh の編集

生成された `github-actions-trust-policy.json` の以下の部分を編集：

```json
"StringLike": {
  "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USER/YOUR_REPO:*"
}
```

- `YOUR_GITHUB_USER`: GitHub ユーザー名またはオーガニゼーション名
- `YOUR_REPO`: リポジトリ名

例：`repo:yaman/langlog:*`

## ステップ 5: パイプラインのテスト

```bash
# コードを commit/push
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

GitHub の `Actions` タブでパイプラインの実行を確認できます。

## 利用可能なワークフロー

### 1. test.yml - テスト実行

- **トリガー**: Push と PR
- **内容**: ユニットテスト実行、カバレッジレポート生成

### 2. deploy.yml - 本番デプロイ

- **トリガー**: main への push、または手動実行
- **内容**: テスト → ビルド → ECR プッシュ → ECS デプロイ

### 3. lint.yml - コード品質チェック

- **トリガー**: Push と PR
- **内容**: Black、isort、flake8 でのチェック

## GitHub Actions での環境変数

ワークフローファイル（`.github/workflows/*.yml`）で参照可能：

```yaml
env:
  AWS_REGION: ${{ vars.AWS_REGION }}

jobs:
  deploy:
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-role
          aws-region: ${{ env.AWS_REGION }}
```

## トラブルシューティング

### IAM ロール認証エラー

**エラー**: `An error occurred (AccessDenied) when calling the AssumeRoleWithWebIdentity operation`

**解決策**:

1. GitHub OIDC プロバイダーが正しく登録されているか確認
2. trust policy の `repo:YOUR_GITHUB_USER/YOUR_REPO:*` が正しいか確認
3. IAM ロールが正しく作成されているか確認

```bash
# ロール確認
aws iam get-role --role-name github-actions-role

# trust policy を確認
aws iam get-role-policy --role-name github-actions-role --policy-name AssumeRolePolicy
```

### ECR イメージがプッシュできない

**チェック項目**:

1. IAM ポリシーに `ecr:GetAuthorizationToken` があるか
2. ECR リポジトリが存在するか
3. AWS クレデンシャルが正しいか

```bash
# ECR リポジトリを手動作成
aws ecr create-repository \
  --repository-name langlog-api \
  --region ap-northeast-1
```

### ワークフローが実行されない

1. ワークフローファイルの構文が正しいか確認
2. トリガー条件（branches など）が正しいか確認
3. GitHub Actions が有効になっているか確認（Settings > Actions）

## セキュリティベストプラクティス

1. **Secrets は Git で管理しない**
   - `.env` は `.gitignore` に追加済み
   - Secrets は GitHub Secrets を使用

2. **IAM ロールは最小権限の原則**
   - デプロイに必要な権限のみを付与
   - ワイルドカード `*` の使用を避ける

3. **デプロイ前にテストを実行**
   - 本番デプロイ前に自動テストが必須

4. **ログに機密情報を含めない**
   - GitHub Actions が自動にマスク

## 参考リンク

- [GitHub Actions ドキュメント](https://docs.github.com/en/actions)
- [AWS GitHub Actions](https://github.com/aws-actions)
- [OpenID Connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
