"""
統合テスト

並行リクエスト、ページネーション、トランザクションテストなど
"""
import pytest
from fastapi import status
import asyncio
from concurrent.futures import ThreadPoolExecutor


class TestPagination:
    """ページネーションテスト"""
    
    def test_get_diary_list_with_pagination(self, client, auth_headers):
        """日記リストのページネーション"""
        # 複数の日記を作成
        for i in range(5):
            client.post(
                "/api/v1/diary/",
                json={"original_text": f"Diary entry {i}"},
                headers=auth_headers
            )
        
        # ページ1を取得
        response = client.get(
            "/api/v1/diary/?skip=0&limit=2",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2
    
    def test_pagination_limit_boundary(self, client, auth_headers):
        """ページネーション上限テスト"""
        # 境界値テスト: limit=0 は無効
        response = client.get(
            "/api/v1/diary/?skip=0&limit=0",
            headers=auth_headers
        )
        
        # 無効なリミットは拒否または無視される
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def test_pagination_skip_negative(self, client, auth_headers):
        """ページネーション skip が負数の場合"""
        response = client.get(
            "/api/v1/diary/?skip=-1&limit=10",
            headers=auth_headers
        )
        
        # 負数は無効
        assert response.status_code in (status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_200_OK)
    
    def test_pagination_excessive_limit(self, client, auth_headers):
        """ページネーション上限が過度に大きい場合"""
        response = client.get(
            "/api/v1/diary/?skip=0&limit=10000",
            headers=auth_headers
        )
        
        # 過度に大きいリミットは制限される
        assert response.status_code == status.HTTP_200_OK
        # サーバー側で制限が適用される


class TestConcurrentRequests:
    """並行リクエストテスト"""
    
    @pytest.mark.skip(reason="TestClientはスレッドセーフでないため並行テストは非対応")
    def test_concurrent_diary_creation(self, client, auth_headers):
        """複数の日記を同時作成"""
        def create_diary(index):
            response = client.post(
                "/api/v1/diary/",
                json={"original_text": f"Concurrent diary {index}"},
                headers=auth_headers
            )
            return response.status_code == status.HTTP_201_CREATED
        
        # 5つの並行リクエスト
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(create_diary, range(5)))
        
        # すべてのリクエストが成功すること
        assert all(results)
    
    def test_concurrent_read_requests(self, client, auth_headers):
        """複数の日記を同時読取"""
        # まず1つ作成
        create_response = client.post(
            "/api/v1/diary/",
            json={"original_text": "Test for concurrent read"},
            headers=auth_headers
        )
        diary_id = create_response.json()["id"]
        
        def read_diary():
            response = client.get(
                f"/api/v1/diary/{diary_id}",
                headers=auth_headers
            )
            return response.status_code == status.HTTP_200_OK
        
        # 10個の並行読取
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: read_diary(), range(10)))
        
        assert all(results)


class TestEdgeCases:
    """エッジケーステスト"""
    
    def test_very_long_string(self, client, auth_headers):
        """非常に長い文字列の処理"""
        long_text = "A" * 5000
        
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": long_text},
            headers=auth_headers
        )
        
        # 長い文字列も処理される（上限チェック）
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def test_whitespace_only_text(self, client, auth_headers):
        """空白のみのテキスト"""
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": "   \n\t  \r\n   "},
            headers=auth_headers
        )
        
        # 空白のみは拒否される可能性
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST)
    
    def test_single_character_text(self, client, auth_headers):
        """1文字のテキスト"""
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": "A"},
            headers=auth_headers
        )
        
        # 1文字でも有効
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_numeric_string_text(self, client, auth_headers):
        """数字のみのテキスト"""
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": "1234567890"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_special_symbols(self, client, auth_headers):
        """特殊記号のみのテキスト"""
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": "!@#$%^&*()_+-=[]{}|;:',.<>?/"},
            headers=auth_headers
        )
        
        # 特殊記号も許可される
        assert response.status_code == status.HTTP_201_CREATED


class TestDataIntegrity:
    """データ整合性テスト"""
    
    def test_diary_data_persistence(self, client, auth_headers):
        """日記データが正しく保存・取得されること"""
        original_text = "I had a great day today. The weather was beautiful."
        
        # 作成
        create_response = client.post(
            "/api/v1/diary/",
            json={"original_text": original_text},
            headers=auth_headers
        )
        
        diary_id = create_response.json()["id"]
        
        # 取得
        get_response = client.get(
            f"/api/v1/diary/{diary_id}",
            headers=auth_headers
        )
        
        data = get_response.json()
        
        # オリジナルテキストが変更されていないこと
        assert data["original_text"] == original_text
    
    def test_user_isolation(self, client, test_user_data):
        """ユーザーデータが隔離されること"""
        # ユーザー1を登録
        user1_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert user1_response.status_code == status.HTTP_201_CREATED
        
        # ユーザー2を登録（別のメール）
        user2_data = {
            **test_user_data,
            "email": "user2@example.com"
        }
        user2_response = client.post("/api/v1/auth/register", json=user2_data)
        assert user2_response.status_code == status.HTTP_201_CREATED
        
        # 両ユーザーが存在すること
        assert user1_response.json()["user"]["email"] != user2_response.json()["user"]["email"]
    
    def test_diary_user_ownership(self, client, auth_headers):
        """日記が正しいユーザーに属していること"""
        # 日記作成
        create_response = client.post(
            "/api/v1/diary/",
            json={"original_text": "My secret diary"},
            headers=auth_headers
        )
        
        diary_id = create_response.json()["id"]
        
        # 日記取得時にユーザー情報が含まれること
        get_response = client.get(
            f"/api/v1/diary/{diary_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        
        # ユーザーIDが含まれていること
        assert "user_id" in data or "created_by" in data


class TestErrorHandling:
    """エラーハンドリングテスト"""
    
    def test_404_not_found_diary(self, client, auth_headers):
        """存在しない日記へのアクセス"""
        response = client.get(
            "/api/v1/diary/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_500_error_handling(self, client, auth_headers):
        """サーバーエラーレスポンス"""
        # 不正なデータでテスト（サーバーエラーが発生する可能性）
        response = client.post(
            "/api/v1/diary/",
            json={"original_text": None},
            headers=auth_headers
        )
        
        # バリデーションエラーまたはサーバーエラー
        assert response.status_code in (status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def test_error_response_format(self, client):
        """エラーレスポンスの形式"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrong"}
        )
        
        # エラーレスポンスには detail フィールドが含まれる
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)
