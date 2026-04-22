# LangLog 開発ルール

このドキュメントは LangLog リポジトリでコード開発する際のルールを定義しています。  
このプロジェクトは **学習用途が主目的** のため、コメント・ドキュメントを充実させることを優先します。

## 1. コメント記述ルール

### 1.1 ファイルヘッダーコメント

すべてのコードファイルの先頭に、そのファイルの目的を説明するコメントを付与する。

**Python の例:**

```python
"""ユーザー認証サービスモジュール

このモジュールはユーザーの登録、ログイン、トークン管理などの認証関連の
ビジネスロジックを提供します。パスワードのハッシュ化・検証、JWT トークンの
生成・検証などの機能を含みます。
"""
```

**JavaScript / React の例:**

```javascript
/**
 * 認証コンテキストモジュール
 *
 * このモジュールはアプリケーション全体での認証状態を管理します。
 * ログインユーザー情報、トークン、認証関数などを Context API を通じて
 * すべてのコンポーネントに提供します。
 */
```

### 1.2 クラス・関数のコメント

クラスと関数には、その役割・目的・パラメータ・戻り値を詳しく説明するコメントを付与する。

**Python の例:**

```python
class UserService:
    """ユーザー管理サービスクラス

    ユーザーの作成、検索、更新、削除などの操作を担当します。
    データベースとの連携を隠蔽し、ビジネスロジックを提供します。
    """

    def create_user(self, email: str, password: str, name: str) -> User:
        """ユーザーを作成します

        指定されたメールアドレスとパスワードで新規ユーザーを登録します。
        パスワードは bcrypt でハッシュ化して保存されます。

        Args:
            email (str): ユーザーのメールアドレス
            password (str): ユーザーのパスワード（最大72文字）
            name (str): ユーザー名

        Returns:
            User: 作成されたユーザーオブジェクト

        Raises:
            ValueError: メールアドレスが既に登録されている場合
        """
```

### 1.3 複雑なロジックへのコメント

5行以上の複雑な処理には、各ステップを説明するコメントを付与する。

```python
def hash_password(password: str) -> str:
    """パスワードを bcrypt でハッシュ化する"""
    # pwd_context は passlib で定義された CryptContext インスタンス
    # hash() メソッドでパスワードをハッシュ化
    # bcrypt は毎回異なるハッシュ値を生成（Salt を含む）
    return pwd_context.hash(password)
```

### 1.4 変数・定義の説明コメント

複数の関連する定義や設定値には、各項目の意味を説明するコメントを付与する。

```python
class Settings(BaseSettings):
    # ===== データベース設定 =====
    # PostgreSQL への接続文字列
    DATABASE_URL: str = os.getenv(...)

    # ===== JWT 認証設定 =====
    # トークン署名用の秘密鍵
    JWT_SECRET_KEY: str = os.getenv(...)

    # トークン署名アルゴリズム（HS256 = HMAC with SHA-256）
    JWT_ALGORITHM: str = "HS256"
```

## 2. ドキュメント記述ルール

### 2.1 README

各モジュール・コンポーネントディレクトリに、その役割を説明する README を作成する（今後）。

```markdown
# Authentication Module

## 概要

ユーザー認証関連の機能を提供します。

## 構成ファイル

- `models/user.py` - ユーザーデータモデル
- `schemas/user.py` - リクエスト/レスポンススキーマ
- `services/auth_service.py` - 認証ビジネスロジック
- `routers/auth.py` - API エンドポイント

## 使用方法

...
```

### 2.2 設計ドキュメント

API 設計や重要なアルゴリズムには、別途設計ドキュメント（DESIGN.md など）を作成する。

## 3. 名前付けルール

### 3.1 変数名

- **意図が明確な名前を使用**: `user` ✅ vs `u` ❌
- **ブール値は is/has プレフィックス**: `is_active`, `has_permission` ✅
- **集合は複数形**: `users`, `items` ✅

### 3.2 関数名

- **動作を示す動詞を含む**: `create_user()`, `fetch_users()` ✅
- **実装の詳細を含めない**: `get_users_from_db()` ❌ → `get_users()` ✅
- **戻り値がブール値の場合**: `is_valid()`, `has_permission()` ✅

### 3.3 クラス名

- **CapitalCase を使用**: `UserService`, `AuthForm` ✅
- **単数形を使用**: `User` ✅ vs `Users` ❌

## 4. コード整理ルール

### 4.1 インポート順序

```python
# 1. 標準ライブラリ
import os
from datetime import datetime

# 2. サードパーティライブラリ
from sqlalchemy import Column, String
from pydantic import BaseModel

# 3. ローカルモジュール
from app.database import Base
from app.config import settings
```

### 4.2 ファイル構成

```
module/
├── README.md           # モジュール説明
├── __init__.py         # エクスポート定義
├── models.py           # ORM モデル（または models/）
├── schemas.py          # Pydantic スキーマ（または schemas/）
├── services.py         # ビジネスロジック（または services/）
└── routers.py          # API ロジック（または routers/）
```

## 5. コード品質基準

### 5.1 責務単一性

- 1 つの関数は 1 つの責務のみ持つ
- 関数の長さは 30 行以下を目安とする
- 複雑な処理は関数に抽出する

### 5.2 エラーハンドリング

すべての可能性のあるエラーを処理し、適切なエラーメッセージを返す。

```python
def get_user(user_id: str) -> User:
    """ユーザーを ID で取得"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # ユーザーが見つからない場合は明確なエラーメッセージ
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    return user
```

## 6. 新機能追加時のチェックリスト

- [ ] ファイルヘッダーコメント を記述
- [ ] 関数/クラスのドキュメント を記述
- [ ] 複雑なロジックにコメント を記述
- [ ] 関数のテスト を作成
- [ ] エラーハンドリング を実装
- [ ] 型ヒント を記述
- [ ] 不要なコメント (実装の詳細など) を削除
- [ ] README/設計ドキュメント を更新

## 7. デバッグ用コメント

デバッグ中のコメントは、コミット前に削除する。必要な場合は TODO コメントを使用。

```python
# ❌ 削除すべき
# print(user)  # テスト用

# ✅ 推奨
# TODO: パフォーマンス最適化が必要（N+1 クエリ問題）
```

---

**目標: コメント量が多すぎるくらいが丁度いい。  
このリポジトリは学習教材として機能させることが優先。**
