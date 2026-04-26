# テスト実行ガイド

バックエンドテストはコンテナ内で実行され、GitHub Actions で自動実行されます。

## 📋 ローカルでのテスト実行

### 1. Docker Compose でテスト実行（推奨）

```bash
cd english-diary

# テスト用Docker Composeで実行
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# コンテナを削除
docker-compose -f docker-compose.test.yml down
```

### 2. 直接 pytest を実行（開発環境）

```bash
cd english-diary/backend

# 全テスト実行
python -m pytest tests/ -v

# カバレッジ付きで実行
python -m pytest tests/ -v --cov=app --cov-report=html

# 特定のテストファイルを実行
python -m pytest tests/test_auth.py -v

# 特定のテストクラスを実行
python -m pytest tests/test_auth.py::TestUserRegistration -v

# 特定のテスト関数を実行
python -m pytest tests/test_auth.py::TestUserRegistration::test_register_success -v
```

### 3. スクリプト実行

```bash
cd english-diary

# テスト実行スクリプトを実行
chmod +x run-tests.sh
./run-tests.sh
```

## 🔄 CI/CD パイプライン

### GitHub Actions ワークフロー

リポジトリに push または PR を作成すると、自動的に以下が実行されます：

1. **コード取得**: リポジトリをチェックアウト
2. **Python セットアップ**: Python 3.11 をセットアップ
3. **依存関係インストール**: requirements.txt からパッケージをインストール
4. **サービス起動**:
   - PostgreSQL 15
   - Redis 7
5. **テスト実行**: pytest で全テストを実行
6. **カバレッジレポート**: Codecov にアップロード

### ワークフロー詳細

**ファイル**: `.github/workflows/backend-test.yml`

**トリガー条件**:

- main/develop ブランチへの push
- main/develop ブランチへの PR
- `english-diary/backend/**` ファイルの変更

**実行時間**: 約 2-3 分

## 📊 カバレッジレポート

### HTML レポート生成

```bash
cd english-diary/backend

python -m pytest tests/ --cov=app --cov-report=html

# htmlcov/index.html をブラウザで開く
```

### Codecov へのアップロード

GitHub Actions で自動的にアップロードされます。

**Codecov ダッシュボード**: https://codecov.io/gh/kokiyamanami/LangLog

## 🚀 テストの品質基準

### カバレッジ目標

- 🟢 **80% 以上**: 優秀（緑色バッジ）
- 🟠 **60-80%**: 要改善（オレンジ色バッジ）
- 🔴 **60% 未満**: 不足（赤色バッジ）

### GitHub PR チェック

- ✅ テストが全て成功すること
- ✅ カバレッジが低下しないこと
- ✅ コード品質がチェックされること

## 🐛 トラブルシューティング

### テストがローカルで失敗する場合

```bash
# デバッグ情報を表示
pytest -vv --tb=long -s

# 環境変数を確認
env | grep DATABASE_URL
env | grep TEST_DATABASE_URL
```

### データベース接続エラー

```bash
# PostgreSQL が起動しているか確認
docker ps | grep postgres

# Redis が起動しているか確認
docker ps | grep redis
```

### キャッシュの問題

```bash
# pip キャッシュをクリア
pip cache purge

# Docker イメージを再構築
docker-compose -f docker-compose.test.yml build --no-cache
```

## 📝 テスト追加時のチェックリスト

- [ ] テストファイルを `tests/` ディレクトリに配置
- [ ] テストクラス名を `Test*` で始める
- [ ] テスト関数名を `test_*` で始める
- [ ] フィクスチャを活用（重複を避ける）
- [ ] 例外テースを含める（エラーケース）
- [ ] ローカルで全テスト実行確認
- [ ] カバレッジ 80% 以上を目指す

## 🔗 参考リンク

- [pytest 公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [GitHub Actions ドキュメント](https://docs.github.com/actions)
- [Codecov](https://codecov.io/)
