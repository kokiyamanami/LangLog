"""LangLog バックエンドメインアプリケーション

このモジュールはFastAPIアプリケーションを初期化し、
ルーティング、CORS設定、データベース初期化を行います。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers import auth, users, diary

# SQLAlchemy ORM モデルに基づいてデータベーステーブルを作成
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass  # テスト環境ではDBが起動していない場合があるため無視

# FastAPI アプリケーションインスタンスを作成
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add CORS middleware - MUST be added before including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(diary.router)


# キャッチオール OPTIONS ハンドラー（CORS プリフライト対応）
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """OPTIONS リクエストを全エンドポイントで許可"""
    return {}


@app.get("/")
def read_root():
    return {"message": "LangLog API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
