# GitHub Secrets 設定ガイド

## 📋 目次

1. [GitHub Secrets とは](#github-secrets-とは)
2. [必要な Secrets 一覧](#必要な-secrets-一覧)
3. [AWS 認証情報の取得](#aws-認証情報の取得)
4. [Secrets の登録方法](#secrets-の登録方法)
5. [トラブルシューティング](#トラブルシューティング)

---

## GitHub Secrets とは

### 🔐 何か

GitHub Actions ワークフロー内で使用する **秘密情報を安全に保存** するサービス

```
Git push
  ↓
GitHub Actions 実行
  ↓
Secrets から取得（暗号化）
  ↓
AWS 認証情報でログイン
  ↓
ECR・ECS・S3 へアクセス
```

### ⚠️ 重要

- **絶対に Git にコミットしない！**（AWS キーが流出）
- GitHub 上で暗号化保存
- ワークフロー実行時のみ復号化
- ログには表示されない（`***` でマスク）

---

## 必要な Secrets 一覧

MVP デプロイ自動化に必要:

| Secrets 名                                 | 値                   | 例                                         |
| ------------------------------------------ | -------------------- | ------------------------------------------ |
| `AWS_ACCOUNT_ID`                           | AWS アカウント ID    | `123456789012`                             |
| `AWS_ACCESS_KEY_ID`                        | IAM アクセスキー     | `AKIAIOSFODNN7EXAMPLE`                     |
| `AWS_SECRET_ACCESS_KEY`                    | IAM シークレットキー | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `SLACK_WEBHOOK`（オプション）              | Slack 通知 URL       | `https://hooks.slack.com/...`              |
| `CLOUDFRONT_DISTRIBUTION_ID`（オプション） | CloudFront ID        | `E1234ABCD5678`                            |

---

## AWS 認証情報の取得

### ステップ 1: AWS Management Console にログイン

```
https://console.aws.amazon.com
```

### ステップ 2: AWS Account ID を確認

```
① AWS Management Console 右上の アカウント名 をクリック
② 「アカウント」を選択
③ Account ID を表示（例：123456789012）
④ コピーして保存
```

### ステップ 3: IAM ユーザー作成（推奨）

**セキュリティベストプラクティス**: Root アカウントキーは使用禁止

```
① IAM → ユーザー → ユーザーを作成
② ユーザー名: github-actions-deploy
③ アクセスタイプ: プログラムによるアクセス
④ 次へ
```

### ステップ 4: IAM ユーザーに権限を付与

```
① 権限の設定 → ポリシーをアタッチ
② 以下をチェック:
   ✅ AmazonECS_FullAccess
   ✅ AmazonEC2ContainerRegistryFullAccess
   ✅ AmazonS3FullAccess
   ✅ AmazonRDSFullAccess
   ✅ CloudFrontFullAccess
③ 次へ → ユーザーを作成
```

### ステップ 5: アクセスキーを取得

```
① IAM → ユーザー → github-actions-deploy をクリック
② セキュリティ認証情報 タブ
③ アクセスキー → アクセスキーを作成
④ ユースケース: その他
⑤ 次へ → アクセスキーを作成
⑥ 表示される:
   - アクセスキー ID
   - シークレットアクセスキー
⑦ CSV ダウンロードして保存（重要！）
```

**⚠️ 注意**:

- シークレットアクセスキーは **この時だけ表示**
- 後で表示されない
- 必ずコピーして保存
- 流出したら即削除

---

## Secrets の登録方法

### 🎯 方法 1: GitHub Web UI（簡単）

#### ステップ 1: リポジトリ設定画面を開く

```
① GitHub で LangLog リポジトリを開く
② 上部メニュー → Settings
③ 左サイドバー → Secrets and variables → Actions
```

#### ステップ 2: AWS_ACCOUNT_ID を登録

```
① New repository secret をクリック
② Name: AWS_ACCOUNT_ID
③ Secret: 123456789012 をペースト
④ Add secret をクリック
```

**画面例**:

```
┌─────────────────────────────────────┐
│ New secret                           │
├─────────────────────────────────────┤
│ Name: AWS_ACCOUNT_ID                │
│ Secret: [123456789012         ]     │
│                                     │
│        [Add secret] [Cancel]        │
└─────────────────────────────────────┘
```

#### ステップ 3: AWS_ACCESS_KEY_ID を登録

```
① New repository secret をクリック
② Name: AWS_ACCESS_KEY_ID
③ Secret: AKIA******* をペースト
④ Add secret をクリック
```

#### ステップ 4: AWS_SECRET_ACCESS_KEY を登録

```
① New repository secret をクリック
② Name: AWS_SECRET_ACCESS_KEY
③ Secret: wJalrXUtnFEMI/K7MDENG/**** をペースト
④ Add secret をクリック
```

#### ステップ 5: 確認

```
リポジトリ Secrets 一覧:
✅ AWS_ACCOUNT_ID
✅ AWS_ACCESS_KEY_ID
✅ AWS_SECRET_ACCESS_KEY

各 Secret の右に ★ マークがあれば登録完了
```

---

### 🎯 方法 2: GitHub CLI（コマンドライン）

#### セットアップ

```bash
# GitHub CLI インストール
# Windows: https://cli.github.com/
# Mac: brew install gh
# Linux: https://github.com/cli/cli/releases

# GitHub にログイン
gh auth login
# → GitHub.com を選択 → SSH を選択 → 指示に従う
```

#### Secrets 登録

```bash
# リポジトリフォルダに移動
cd c:\Users\yaman\OneDrive\デスクトップ\LangLog\LangLog

# AWS_ACCOUNT_ID を登録
gh secret set AWS_ACCOUNT_ID --body "123456789012"

# AWS_ACCESS_KEY_ID を登録
gh secret set AWS_ACCESS_KEY_ID --body "AKIA*******"

# AWS_SECRET_ACCESS_KEY を登録
gh secret set AWS_SECRET_ACCESS_KEY --body "wJalrXUtnFEMI/K7MDENG/****"

# 登録確認
gh secret list
```

**出力例**:

```
AWS_ACCOUNT_ID              Updated 2026-04-25
AWS_ACCESS_KEY_ID           Updated 2026-04-25
AWS_SECRET_ACCESS_KEY       Updated 2026-04-25
```

---

### 🎯 方法 3: ファイルから一括登録（最速）

#### `secrets.json` を作成

```json
{
  "AWS_ACCOUNT_ID": "123456789012",
  "AWS_ACCESS_KEY_ID": "AKIA*******",
  "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/****"
}
```

#### スクリプトで一括登録

**register-secrets.sh**（Mac/Linux）:

```bash
#!/bin/bash

SECRETS_FILE="secrets.json"

while IFS="=" read -r key value; do
  value=$(echo $value | sed 's/"//g')
  gh secret set $key --body "$value"
  echo "✅ $key registered"
done < <(jq -r 'to_entries | .[] | "\(.key)=\(.value)"' $SECRETS_FILE)

echo "✨ All secrets registered!"
```

**register-secrets.ps1**（Windows PowerShell）:

```powershell
# secrets.json から読み込み
$secrets = Get-Content secrets.json | ConvertFrom-Json

foreach ($key in $secrets.PSObject.Properties.Name) {
    $value = $secrets.$key
    gh secret set $key --body $value
    Write-Host "✅ $key registered"
}

Write-Host "✨ All secrets registered!"
```

#### 実行

```bash
# Mac/Linux
chmod +x register-secrets.sh
./register-secrets.sh

# Windows PowerShell
./register-secrets.ps1
```

---

## Secrets 使用例（ワークフロー内）

### YAML での参照

```yaml
name: Deploy MVP to AWS

env:
  AWS_REGION: ap-northeast-1
  ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
```

### ⚠️ ログには表示されない

```
デプロイログ:
Configuring AWS credentials
Using AWS region: ap-northeast-1
AWS Access Key ID: ****** (マスク済み)
AWS Secret Access Key: *** (マスク済み)
✅ AWS credentials configured
```

実際のキーが漏れることはない！

---

## トラブルシューティング

### ❌ エラー: Secret not found

```
Error: Unable to find secret AWS_ACCESS_KEY_ID
```

**解決方法**:

```
① Secret 名を確認（大文字・小文字区別）
② Secret が登録されているか確認
③ ワークフロー YAML の参照名が正しいか確認

正しい参照: ${{ secrets.AWS_ACCESS_KEY_ID }}
間違い: ${{ secrets.aws_access_key_id }}
```

### ❌ エラー: Access Denied（AWS）

```
Error: An error occurred (AccessDenied) when calling the DescribeTaskDefinition operation
```

**解決方法**:

```
① AWS_ACCESS_KEY_ID が正しいか確認
② AWS_SECRET_ACCESS_KEY が正しいか確認
③ IAM ユーザーに権限があるか確認
④ キーの有効期限切れ確認
```

### ❌ エラー: 401 Unauthorized

```
Error: AWS authentication failed
```

**解決方法**:

```
① Key ID とシークレットキーが一致しているか確認
② IAM ユーザーが存在するか確認
③ Key が無効化されていないか確認
④ 新しい Key を再発行
```

### 🔄 Secret を更新したい

```
① GitHub Settings → Secrets
② 更新したい Secret をクリック
③ Update をクリック
④ 新しい値をペースト
⑤ Update secret をクリック
```

**注意**: 既に実行中のワークフローは古い値を使用

### 🗑️ Secret を削除したい

```
① GitHub Settings → Secrets
② 削除する Secret をクリック
③ Delete をクリック
④ 確認画面で Delete を再度クリック
```

---

## ✅ セットアップ完了チェックリスト

```
□ AWS Account ID を取得
  位置: https://console.aws.amazon.com/

□ IAM ユーザー github-actions-deploy を作成
  権限: ECS, ECR, S3, RDS, CloudFront

□ アクセスキーを生成
  CSV をダウンロード・保存

□ GitHub Secrets に登録
  AWS_ACCOUNT_ID
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY

□ ワークフロー YAML に追加
  .github/workflows/deploy-mvp.yml

□ Main ブランチに push してテスト
  → Actions タブで Deploy MVP が実行
  → 成功確認
```

---

## 🎯 次のステップ

1. **Secrets を登録** ← 今ここ
2. **deploy-mvp.yml を追加**
3. **GitHub Actions で自動デプロイ実行**
4. **Slack 通知を設定**（オプション）

---

## 📝 参考資料

- [GitHub Secrets 公式ドキュメント](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AWS IAM ユーザー作成](https://docs.aws.amazon.com/iam/latest/userguide/id_users_create.html)
- [GitHub CLI](https://cli.github.com/)

---

## 💡 セキュリティのベストプラクティス

```
✅ すること:
  - リポジトリごとに異なる Secrets を使用
  - 定期的に Key をローテーション（90 日ごと）
  - 不要な権限は付与しない（最小権限の原則）
  - Secret を Git にコミットしない
  - Secret ファイル（secrets.json）は .gitignore に追加

❌ しないこと:
  - Root AWS キーを使用
  - Secret をログ出力
  - Secret をチャットで共有
  - 無期限の Key を使用
  - 複数リポジトリで同じ Key を再利用
```

---

## 🔐 GitHub Secrets セキュリティ三原則

```
1. 暗号化: GitHub サーバーで暗号化保存
   → ハッカーが GitHub を侵攻しても読めない

2. マスク: ログに表示されない
   → CI/CD ログに秘密情報が漏れない

3. アクセス制御: リポジトリ管理者のみ編集可
   → 誤ってコミットされるリスク低い
```
