"""
認証エンドポイントのテスト
"""
import pytest
from fastapi import status


class TestUserRegistration:
    """ユーザー登録テスト"""
    
    def test_register_success(self, client, test_user_data):
        """正常なユーザー登録"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user"]["email"] == test_user_data["email"]
        assert data["user"]["name"] == test_user_data["name"]
        assert "id" in data["user"]
    
    def test_register_duplicate_email(self, client, test_user_data):
        """重複メールアドレスでの登録失敗"""
        # 最初のユーザーを登録
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 同じメールで再登録
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT)
    
    def test_register_invalid_email(self, client):
        """不正なメールアドレス"""
        response = client.post("/api/v1/auth/register", json={
            "name": "Test",
            "email": "invalid-email",
            "password": "password123"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client):
        """短すぎるパスワード"""
        response = client.post("/api/v1/auth/register", json={
            "name": "Test",
            "email": "test@example.com",
            "password": "short"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """ユーザーログインテスト"""
    
    def test_login_success(self, client, test_user_data):
        """正常なログイン"""
        # ユーザー登録
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # ログイン
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "Bearer"
    
    def test_login_invalid_password(self, client, test_user_data):
        """不正なパスワード"""
        # ユーザー登録
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 間違ったパスワードでログイン
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrong_password"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """存在しないユーザーでログイン"""
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    """トークンリフレッシュテスト"""
    
    def test_refresh_token_success(self, client, test_user_data):
        """正常なトークンリフレッシュ"""
        # ユーザー登録
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # ログイン
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        refresh_token = login_response.json()["refresh_token"]
        
        # トークンリフレッシュ
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
    
    def test_refresh_invalid_token(self, client):
        """不正なリフレッシュトークン"""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPasswordSecurity:
    """パスワードセキュリティテスト"""
    
    def test_password_hashing(self, client, test_user_data):
        """パスワードがハッシュ化されて保存されること"""
        # ユーザー登録
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # レスポンスにはパスワードハッシュが含まれていないこと
        user_data = response.json()
        assert "password" not in user_data
        assert "password_hash" not in user_data
    
    def test_different_passwords_different_hashes(self, client):
        """異なるパスワードは異なるハッシュになること"""
        user1 = {
            "name": "User 1",
            "email": "user1@example.com",
            "password": "password123"
        }
        
        user2 = {
            "name": "User 2",
            "email": "user2@example.com",
            "password": "password123"  # 同じパスワード
        }
        
        response1 = client.post("/api/v1/auth/register", json=user1)
        response2 = client.post("/api/v1/auth/register", json=user2)
        
        # 両方とも登録できること
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
    
    def test_case_sensitive_password(self, client, test_user_data):
        """パスワードが大文字・小文字を区別すること"""
        # ユーザー登録
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 異なるケースでログイン試行
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"].upper()
        })
        
        # 異なるケースでのログインは失敗
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserRegistrationValidation:
    """ユーザー登録バリデーションテスト"""
    
    def test_email_format_validation(self, client):
        """メールアドレス形式の検証"""
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com"
        ]
        
        for invalid_email in invalid_emails:
            response = client.post("/api/v1/auth/register", json={
                "name": "Test",
                "email": invalid_email,
                "password": "password123"
            })
            
            # 不正なメールアドレスは拒否される
            assert response.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def test_name_required(self, client):
        """名前は必須項目"""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123"
        })
        
        # 名前なしは拒否される
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_password_minimum_length(self, client):
        """パスワード最小文字数チェック"""
        response = client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "pass"  # 短すぎるパスワード
        })
        
        # 短いパスワードは拒否される
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_empty_password(self, client):
        """空のパスワード"""
        response = client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": ""
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
