"""
日記エンドポイントのテスト
"""
import pytest
from fastapi import status


class TestDiaryCreate:
    """日記作成テスト"""
    
    def test_create_diary_success(self, client, auth_headers):
        """正常な日記作成"""
        diary_data = {
            "original_text": "Today I went to the park with my friends. It was a very good day."
        }
        
        response = client.post(
            "/api/v1/diary/",
            json=diary_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["original_text"] == diary_data["original_text"]
        assert "corrected_text" in data
        assert "corrections" in data
        assert "id" in data
    
    def test_create_diary_empty(self, client, auth_headers):
        """空の日記作成失敗"""
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": ""},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_diary_unauthorized(self, client):
        """認証なしの日記作成失敗"""
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": "Test diary"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDiaryRead:
    """日記取得テスト"""
    
    def test_get_diary_success(self, client, auth_headers):
        """日記詳細取得成功"""
        # 日記作成
        create_response = client.post(
            "/api/v1/diary/",
            json={"original_text": "Test diary content"},
            headers=auth_headers
        )
        diary_id = create_response.json()["id"]
        
        # 日記取得
        response = client.get(
            f"/api/v1/diary/{diary_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == diary_id
        assert data["original_text"] == "Test diary content"
    
    def test_get_diary_not_found(self, client, auth_headers):
        """存在しない日記取得失敗"""
        response = client.get(
            "/api/v1/diary/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_diary_unauthorized(self, client, auth_headers):
        """他のユーザーの日記取得失敗"""
        # ユーザーAが日記作成
        create_response = client.post(
            "/api/v1/diary/",
            json={"original_text": "User A diary"},
            headers=auth_headers
        )
        diary_id = create_response.json()["id"]
        
        # ユーザーBでログイン（別のユーザー）
        user_b_data = {
            "name": "User B",
            "email": "userb@example.com",
            "password": "password123"
        }
        client.post("/api/v1/auth/register", json=user_b_data)
        login_response = client.post("/api/v1/auth/login", json={
            "email": user_b_data["email"],
            "password": user_b_data["password"]
        })
        user_b_headers = {
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
        
        # ユーザーBがユーザーAの日記にアクセス
        response = client.get(
            f"/api/v1/diary/{diary_id}",
            headers=user_b_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDiaryList:
    """日記一覧テスト"""
    
    def test_list_diaries_success(self, client, auth_headers):
        """日記一覧取得成功"""
        # 複数の日記作成
        for i in range(3):
            client.post(
                "/api/v1/diary/",
                json={"original_text": f"Diary {i+1}"},
                headers=auth_headers
            )
        
        # 一覧取得
        response = client.get(
            "/api/v1/diary/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3
    
    def test_list_diaries_pagination(self, client, auth_headers):
        """日記一覧ページネーション"""
        # 複数の日記作成
        for i in range(5):
            client.post(
                "/api/v1/diary/",
                json={"original_text": f"Diary {i+1}"},
                headers=auth_headers
            )
        
        # ページネーション付き一覧取得
        response = client.get(
            "/api/v1/diary/?skip=0&limit=2",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2
    
    def test_list_diaries_empty(self, client, auth_headers):
        """日記なしの場合"""
        response = client.get(
            "/api/v1/diary/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_list_diaries_unauthorized(self, client):
        """認証なしの一覧取得失敗"""
        response = client.get("/api/v1/diary/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
