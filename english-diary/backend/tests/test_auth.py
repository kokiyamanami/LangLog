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
        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]
        assert "id" in data
    
    def test_register_duplicate_email(self, client, test_user_data):
        """重複メールアドレスでの登録失敗"""
        # 最初のユーザーを登録
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 同じメールで再登録
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
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
        assert data["token_type"] == "bearer"
    
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
