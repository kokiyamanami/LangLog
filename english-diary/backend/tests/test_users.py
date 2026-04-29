"""
ユーザーエンドポイントのテスト
"""
import pytest
from fastapi import status


class TestGetCurrentUser:
    """現在のユーザー取得テスト"""
    
    def test_get_current_user_success(self, client, auth_headers, test_user_data):
        """現在のユーザー情報取得成功"""
        response = client.get(
            "/api/v1/users/profile",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]
    
    def test_get_current_user_unauthorized(self, client):
        """認証なしのユーザー情報取得失敗"""
        response = client.get("/api/v1/users/profile")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserProfile:
    """ユーザープロフィール取得テスト"""
    
    def test_get_user_profile_success(self, client, auth_headers, test_user_data):
        """ユーザープロフィール取得成功"""
        response = client.get(
            "/api/v1/users/profile",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]
    
    def test_get_user_profile_not_found(self, client):
        """認証なしのプロフィール取得失敗"""
        response = client.get("/api/v1/users/profile")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateProfile:
    """プロフィール更新テスト"""
    
    def test_update_profile_success(self, client, auth_headers):
        """プロフィール更新成功"""
        update_data = {
            "name": "Updated Name",
            "gender": "male",
            "birth_date": "1990-01-01"
        }
        
        response = client.put(
            "/api/v1/users/profile",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
    
    def test_update_profile_unauthorized(self, client):
        """認証なしのプロフィール更新失敗"""
        response = client.put(
            "/api/v1/users/profile",
            json={"name": "New Name"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestChangePassword:
    """パスワード変更テスト"""
    
    def test_change_password_success(self, client, auth_headers, test_user_data):
        """パスワード変更成功"""
        response = client.post(
            "/api/v1/users/change-password",
            json={
                "current_password": test_user_data["password"],
                "new_password": "new_password_123",
                "confirm_password": "new_password_123"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_old(self, client, auth_headers):
        """古いパスワード間違い"""
        response = client.post(
            "/api/v1/users/change-password",
            json={
                "current_password": "wrong_password_long",
                "new_password": "new_password_123",
                "confirm_password": "new_password_123"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_change_password_unauthorized(self, client):
        """認証なしのパスワード変更失敗"""
        response = client.post(
            "/api/v1/users/change-password",
            json={
                "old_password": "password",
                "new_password": "new_password"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
