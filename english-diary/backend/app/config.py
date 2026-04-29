"""アプリケーション設定ファイル

このモジュールは環境変数から設定を読み込み、アプリケーション全体で使用する
設定値を管理します。開発環境では .env ファイルから、本番環境では環境変数から
読み込まれます。
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定クラス
    
    すべての環境変数と設定値をこのクラスで管理します。
    Pydantic の BaseSettings を使用することで、環境変数の自動バリデーションが可能です。
    """
    
    # ===== データベース設定 =====
    # PostgreSQL への接続文字列
    # 形式: postgresql://ユーザー名:パスワード@ホスト/データベース名
    # TEST_DATABASE_URL が設定されている場合はそちらを優先（テスト環境用）
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost/english_diary")
    )
    
    # ===== JWT (JSON Web Token) 認証設定 =====
    # トークン署名用の秘密鍵（本番環境では強力なランダム値を使用すること）
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "your-secret-key-change-in-production"
    )
    # トークン署名アルゴリズム（HS256 = HMAC with SHA-256）
    JWT_ALGORITHM: str = "HS256"
    # アクセストークンの有効期限（時間単位）
    JWT_EXPIRATION_HOURS: int = 24
    # リフレッシュトークンの有効期限（日数単位）
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    
    # ===== API 設定 =====
    # API のベースパス（すべてのエンドポイントはこれを接頭辞として使用）
    API_V1_STR: str = "/api/v1"
    # プロジェクト名（ドキュメント表示用）
    PROJECT_NAME: str = "LangLog API"
    
    # ===== CORS (Cross-Origin Resource Sharing) 設定 =====
    CORS_ORIGINS: list = [
        "*"  # Production では環境変数から設定すること
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
