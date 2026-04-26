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


class TestDiaryUpdate:
    """日記更新テスト"""
    
    def test_update_diary_success(self, client, auth_headers):
        """日記更新成功"""
        # 日記作成
        create_response = client.post(
            "/api/v1/diary/",
            json={"original_text": "Initial diary"},
            headers=auth_headers
        )
        diary_id = create_response.json()["id"]
        
        # 日記更新
        update_response = client.put(
            f"/api/v1/diary/{diary_id}",
            json={"original_text": "Updated diary"},
            headers=auth_headers
        )
        
        assert update_response.status_code == status.HTTP_200_OK
        data = update_response.json()
        assert data["original_text"] == "Updated diary"
    
    def test_update_nonexistent_diary(self, client, auth_headers):
        """存在しない日記の更新失敗"""
        response = client.put(
            "/api/v1/diary/00000000-0000-0000-0000-000000000000",
            json={"original_text": "Updated"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_diary_unauthorized(self, client):
        """認証なしの日記更新失敗"""
        response = client.put(
            "/api/v1/diary/00000000-0000-0000-0000-000000000000",
            json={"original_text": "Updated"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDiaryDelete:
    """日記削除テスト"""
    
    def test_delete_diary_success(self, client, auth_headers):
        """日記削除成功"""
        # 日記作成
        create_response = client.post(
            "/api/v1/diary/",
            json={"original_text": "To be deleted"},
            headers=auth_headers
        )
        diary_id = create_response.json()["id"]
        
        # 日記削除
        delete_response = client.delete(
            f"/api/v1/diary/{diary_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)
        
        # 削除後は取得できないこと
        get_response = client.get(
            f"/api/v1/diary/{diary_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_diary(self, client, auth_headers):
        """存在しない日記の削除"""
        response = client.delete(
            "/api/v1/diary/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDiaryContentValidation:
    """日記内容バリデーションテスト"""
    
    def test_diary_with_newlines(self, client, auth_headers):
        """改行を含む日記"""
        diary_data = {
            "original_text": "First line\nSecond line\nThird line"
        }
        
        response = client.post(
            "/api/v1/diary/",
            json=diary_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "\n" in data["original_text"]
    
    def test_diary_with_tabs(self, client, auth_headers):
        """タブを含む日記"""
        diary_data = {
            "original_text": "Line1\tTabbed\tContent"
        }
        
        response = client.post(
            "/api/v1/diary/",
            json=diary_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_diary_with_mixed_punctuation(self, client, auth_headers):
        """複雑な句読点を含む日記"""
        diary_data = {
            "original_text": "Hello! How are you? I'm fine, thanks. Really! (Yes, really.) [1]"
        }
        
        response = client.post(
            "/api/v1/diary/",
            json=diary_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_diary_with_urls(self, client, auth_headers):
        """URL を含む日記"""
        diary_data = {
            "original_text": "I visited https://www.example.com today. Check it out: http://example.co.jp/path?param=value"
        }
        
        response = client.post(
            "/api/v1/diary/",
            json=diary_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_diary_response_contains_corrections(self, client, auth_headers):
        """日記レスポンスに修正情報が含まれること"""
        diary_data = {
            "original_text": "I goed to the park yesterday"
        }
        
        response = client.post(
            "/api/v1/diary/",
            json=diary_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # レスポンスに corrections フィールドが含まれる
        assert "corrections" in data
        assert isinstance(data["corrections"], (list, dict))
