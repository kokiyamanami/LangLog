"""
共有テストフィクスチャとユーティリティ
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.diary import Diary
from app.routers.auth import get_password_hash


# テスト用データベース設定
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

@pytest.fixture(scope="session")
def db_engine():
    """テスト用データベースエンジン"""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """各テスト用のデータベースセッション"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    def override_get_db():
        yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient"""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """テスト用ユーザーデータ"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "test_password_123"
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """テスト用ユーザー（DB保存）"""
    user = User(
        name=test_user_data["name"],
        email=test_user_data["email"],
        password_hash=get_password_hash(test_user_data["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user_data):
    """テスト用認証トークン"""
    # ユーザー作成
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # ログイン
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """認証ヘッダー"""
    return {"Authorization": f"Bearer {auth_token}"}
