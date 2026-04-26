# バックエンド テスト実行ガイド

## 概要

このプロジェクトは pytest を使用した包括的なバックエンドテストスイートを提供しています。

## テストスイート構成

```
tests/
├── conftest.py          # 共有フィクスチャとセットアップ
├── test_auth.py         # 認証エンドポイントテスト
├── test_diary.py        # 日記CRUDテスト
└── test_users.py        # ユーザー操作テスト
```

## 必要なパッケージ

```bash
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
```

（`requirements.txt` に既に含まれています）

## テスト実行

### 1. すべてのテストを実行

```bash
cd backend
pytest
```

### 2. 特定のテストファイルを実行

```bash
# 認証テスト
pytest tests/test_auth.py

# 日記テスト
pytest tests/test_diary.py

# ユーザーテスト
pytest tests/test_users.py
```

### 3. 特定のテストクラスを実行

```bash
# ユーザー登録テストのみ
pytest tests/test_auth.py::TestUserRegistration

# 日記作成テストのみ
pytest tests/test_diary.py::TestDiaryCreate
```

### 4. 特定のテスト関数を実行

```bash
# ログイン成功テストのみ
pytest tests/test_auth.py::TestUserLogin::test_login_success
```

### 5. 詳細な出力

```bash
# 詳細なパス情報を表示
pytest -v

# スタックトレースの詳細を表示
pytest -vv

# 実行時間を表示
pytest -v --durations=10
```

### 6. カバレッジレポート生成

```bash
# HTML形式のカバレッジレポート生成
pytest --cov=app --cov-report=html

# ターミナルに出力
pytest --cov=app --cov-report=term-missing
```

## テストカバレッジ

現在のカバレッジ対象：

- ✅ **認証（auth.py）**
  - ユーザー登録（バリデーション含む）
  - ユーザーログイン
  - トークンリフレッシュ

- ✅ **日記（diary.py）**
  - 日記作成
  - 日記取得（詳細・一覧）
  - ページネーション
  - アクセス権限チェック

- ✅ **ユーザー（users.py）**
  - プロフィール取得・更新
  - パスワード変更
  - 認証チェック

## テスト用フィクスチャ

### `db_session`

テスト用のデータベースセッション（トランザクション分離）

### `client`

FastAPI TestClient インスタンス

### `test_user_data`

テスト用ユーザー情報

```python
{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test_password_123"
}
```

### `test_user`

DB に保存されたテストユーザー

### `auth_token`

認証テスト用のアクセストークン

### `auth_headers`

認証ヘッダー

```python
{"Authorization": f"Bearer {access_token}"}
```

## テスト例

```python
def test_create_diary_success(self, client, auth_headers):
    """正常な日記作成"""
    diary_data = {
        "original_text": "Test diary content"
    }

    response = client.post(
        "/api/v1/diary/",
        json=diary_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["original_text"] == diary_data["original_text"]
```

## CI/CD 統合

GitHub Actions での実行例：

```yaml
- name: Run tests
  run: |
    cd backend
    pytest --cov=app --cov-report=xml
```

## よくある問題

### 1. テストが失敗する場合

```bash
# デバッグ情報を表示
pytest -vv --tb=long

# ログを表示
pytest -s
```

### 2. テストが遅い場合

```bash
# 実行時間が長いテストを特定
pytest --durations=10
```

### 3. 特定のテストをスキップ

```python
@pytest.mark.skip(reason="WIP")
def test_something():
    pass
```

## テスト追加時のガイドライン

1. **テストクラスでグループ化**: 関連するテストを `Test*` クラスにまとめる
2. **説明的な関数名**: `test_<feature>_<scenario>` の形式を使用
3. **フィクスチャを活用**: 重複を避け、セットアップを一元化
4. **例外テストを含む**: 失敗ケース、バリデーション、権限チェック

## 推奨される実行タイミング

- ✅ コミット前：`pytest`
- ✅ PR作成前：`pytest --cov`
- ✅ デプロイ前：フルテスト + カバレッジ確認

---

詳細は pytest 公式ドキュメント参照：https://docs.pytest.org/
