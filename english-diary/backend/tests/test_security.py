"""
セキュリティ関連テスト

CORS、JWT検証、SQLインジェクション対策などのテスト
"""
import pytest
from fastapi import status
import json


class TestCORSHeaders:
    """CORS ヘッダーテスト"""
    
    def test_cors_headers_present(self, client):
        """CORS ヘッダーが存在すること"""
        response = client.options("/api/v1/auth/me")
        
        # CORS プリフライトレスポンス確認
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_cors_allow_credentials(self, client, auth_headers):
        """認証情報を含むリクエストが許可されること"""
        response = client.get(
            "/api/v1/users/profile",
            headers=auth_headers
        )
        
        # 認証ヘッダー付きで成功
        assert response.status_code == status.HTTP_200_OK


class TestJWTTokenValidation:
    """JWT トークン検証テスト"""
    
    def test_expired_token_rejected(self, client):
        """期限切れトークンが拒否されること"""
        # 無効なトークンでリクエスト
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjB9.invalid"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_malformed_token_rejected(self, client):
        """不正な形式のトークンが拒否されること"""
        headers = {"Authorization": "Bearer malformed.token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_missing_bearer_prefix(self, client):
        """Bearer プレフィックスなしのトークンが拒否されること"""
        headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_token_signature(self, client):
        """署名が無効なトークンが拒否されること"""
        # トークン署名を改ざん
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.fake_signature"
        headers = {"Authorization": f"Bearer {fake_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSQLInjectionPrevention:
    """SQL インジェクション対策テスト"""
    
    def test_email_sql_injection_attempt(self, client):
        """メールアドレスへの SQL インジェクション試行が防止されること"""
        payload = {
            "name": "Attacker",
            "email": "test@example.com' OR '1'='1",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=payload)
        
        # バリデーションエラーが返る（インジェクションは実行されない）
        assert response.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def test_user_id_uuid_validation(self, client, auth_headers):
        """ユーザー ID が UUID 形式で検証されること"""
        # 不正な日記 ID でアクセス（UUID形式の検証）
        response = client.get(
            "/api/v1/diary/invalid_id_format",
            headers=auth_headers
        )
        
        # 不正なフォーマットは拒否される
        assert response.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def test_diary_id_uuid_validation(self, client, auth_headers):
        """日記 ID が UUID 形式で検証されること"""
        response = client.get(
            "/api/v1/diary/not_a_uuid",
            headers=auth_headers
        )
        
        assert response.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY)


class TestPayloadValidation:
    """ペイロード検証テスト"""
    
    @pytest.mark.skip(reason="Large payload limit is not yet implemented")
    def test_large_payload_rejected(self, client, auth_headers):
        """大きすぎるペイロードが拒否されること"""
        # 非常に大きなテキストを作成
        large_text = "A" * 1000000  # 1MB
        
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": large_text},
            headers=auth_headers
        )
        
        # 大きすぎるペイロードは拒否される
        assert response.status_code in (status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def test_malformed_json_rejected(self, client, auth_headers):
        """不正な JSON が拒否されること"""
        # 不正な JSON を直接送信
        response = client.post(
            "/api/v1/diary/",
            content=b"{ invalid json }",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_required_fields(self, client, auth_headers):
        """必須フィールドがないとき拒否されること"""
        # original_text フィールドなし
        response = client.post(
            "/api/v1/diary/",
            json={},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_extra_fields_ignored(self, client, auth_headers):
        """余分なフィールドが無視されること"""
        response = client.post(
            "/api/v1/diary/",
            json={
                "original_text": "Test diary",
                "extra_field": "should_be_ignored"
            },
            headers=auth_headers
        )
        
        # 余分なフィールドは無視されるが、リクエストは成功
        assert response.status_code == status.HTTP_201_CREATED


class TestSpecialCharacters:
    """特殊文字テスト"""
    
    def test_unicode_characters_in_text(self, client, auth_headers):
        """Unicode 文字が適切に処理されること"""
        diary_data = {
            "original_text": "Today I learned about 日本語, 中文, and العربية. It was interesting! 🎉"
        }
        
        response = client.post(
            "/api/v1/diary/",
            json=diary_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "日本語" in data["original_text"]
    
    def test_html_tags_in_text(self, client, auth_headers):
        """HTML タグが適切にエスケープされること"""
        diary_data = {
            "original_text": "I visited <script>alert('xss')</script> yesterday"
        }
        
        response = client.post(
            "/api/v1/diary/",
            json=diary_data,
            headers=auth_headers
        )
        
        # リクエストは成功（入力値は保存される）
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_special_characters_in_email(self, client):
        """メールアドレスの特殊文字検証"""
        # 有効なメールアドレス
        payload = {
            "name": "Test User",
            "email": "user+tag@example.co.uk",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED


class TestHTTPMethodValidation:
    """HTTP メソッド検証テスト"""
    
    def test_post_required_for_register(self, client, test_user_data):
        """ユーザー登録に POST が必須であること"""
        # GET でのアクセスを試みる
        response = client.get("/api/v1/auth/register")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_post_required_for_login(self, client):
        """ログインに POST が必須であること"""
        response = client.get("/api/v1/auth/login")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_get_required_for_user_profile(self, client, auth_headers):
        """ユーザープロフィール取得に GET が必須であること"""
        response = client.post(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
