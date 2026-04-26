"""
レート制限およびパフォーマンステスト

レート制限、タイムアウト、リソース制限などのテスト
"""
import pytest
from fastapi import status
import time


class TestRateLimiting:
    """レート制限テスト"""
    
    def test_rapid_registration_attempts(self, client):
        """急速なユーザー登録試行"""
        base_email = "test{}.example.com"
        
        for i in range(10):
            response = client.post("/api/v1/auth/register", json={
                "name": f"Test User {i}",
                "email": f"test{i}@example.com",
                "password": "password123"
            })
            
            # すべてのリクエストが処理される（レート制限なし or 制限なし）
            assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_rapid_login_attempts(self, client):
        """急速なログイン試行"""
        for i in range(5):
            response = client.post("/api/v1/auth/login", json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            })
            
            # ブルートフォース対策がある場合は 429
            assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_429_TOO_MANY_REQUESTS)


class TestTimeoutHandling:
    """タイムアウトハンドリングテスト"""
    
    def test_request_completes_in_reasonable_time(self, client, auth_headers):
        """リクエストが妥当な時間で完了すること"""
        start_time = time.time()
        
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        elapsed_time = time.time() - start_time
        
        # リクエストは 5 秒以内に完了すること
        assert elapsed_time < 5.0
        assert response.status_code == status.HTTP_200_OK


class TestResourceLimits:
    """リソース制限テスト"""
    
    def test_response_time_get_user_list(self, client, auth_headers):
        """ユーザーリスト取得のレスポンスタイム"""
        start_time = time.time()
        
        response = client.get(
            "/api/v1/users/",
            headers=auth_headers
        )
        
        elapsed_time = time.time() - start_time
        
        # 応答時間が妥当範囲内
        if response.status_code == status.HTTP_200_OK:
            assert elapsed_time < 2.0
    
    def test_response_time_get_diary_list(self, client, auth_headers):
        """日記リスト取得のレスポンスタイム"""
        # 複数の日記を作成
        for i in range(5):
            client.post(
                "/api/v1/diary/",
                json={"original_text": f"Diary {i}"},
                headers=auth_headers
            )
        
        start_time = time.time()
        
        response = client.get(
            "/api/v1/diary/",
            headers=auth_headers
        )
        
        elapsed_time = time.time() - start_time
        
        # 複数アイテムの取得でも 1 秒以内
        assert elapsed_time < 1.0
        assert response.status_code == status.HTTP_200_OK


class TestMemoryAndConnectionPool:
    """メモリとコネクションプールテスト"""
    
    def test_multiple_sequential_requests(self, client, auth_headers):
        """複数の逐次リクエスト"""
        for i in range(20):
            response = client.get(
                "/api/v1/auth/me",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
        
        # メモリリークなくすべてのリクエストが成功
    
    def test_connection_persistence(self, client, auth_headers):
        """コネクション永続化テスト"""
        responses = []
        
        for i in range(5):
            response = client.get(
                "/api/v1/auth/me",
                headers=auth_headers
            )
            responses.append(response.status_code)
        
        # すべてが 200 であること
        assert all(status_code == status.HTTP_200_OK for status_code in responses)
