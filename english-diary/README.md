# LangLog - ローカル実装ガイド

## 📋 プロジェクト構成

```
langlog/
├─ backend/                # FastAPI バックエンド
│  ├─ app/
│  │  ├─ models/          # SQLAlchemy モデル
│  │  ├─ schemas/         # Pydantic スキーマ
│  │  ├─ routers/         # API ルーター
│  │  ├─ services/        # ビジネスロジック
│  │  ├─ config.py        # 設定
│  │  └─ database.py      # DB接続
│  ├─ main.py             # FastAPI メインファイル
│  └─ requirements.txt    # Python 依存関係
├─ frontend/              # React フロントエンド
│  ├─ src/
│  │  ├─ pages/          # ページコンポーネント
│  │  ├─ components/     # 再利用可能なコンポーネント
│  │  ├─ services/       # API クライアント
│  │  ├─ App.tsx         # ルートコンポーネント
│  │  └─ index.tsx       # エントリーポイント
│  ├─ public/            # 静的ファイル
│  └─ package.json       # npm 依存関係
├─ docker-compose.yml    # Docker Compose 設定
├─ Dockerfile.backend    # バックエンド用 Dockerfile
├─ Dockerfile.frontend   # フロントエンド用 Dockerfile
├─ .env                  # 環境変数（開発用）
└─ .env.example         # 環境変数テンプレート
```

---

## 🚀 ローカル実行方法

### 前提条件

- Docker & Docker Compose がインストール済み
- Node.js 18+ (オプション: ローカル実行時)
- Python 3.11+ (オプション: ローカル実行時)

### 方法 1: Docker Compose で実行（推奨）

```bash
# プロジェクトディレクトリに移動
cd langlog

# コンテナを起動
docker-compose up

# ログを確認
# - Backend: http://localhost:8000
# - Frontend: http://localhost:3000
# - Postgres: localhost:5432
# - Redis: localhost:6379
```

### 方法 2: ローカルで実行

**Backend:**

```bash
cd backend

# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# PostgreSQL を起動（別ターミナル）
# または docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16-alpine

# 環境変数設定
export DATABASE_URL=postgresql://postgres:postgres@localhost/english_diary

# サーバー起動
uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend

# 依存関係インストール
npm install

# 開発サーバー起動
npm start
```

---

## 🔐 ログインテスト

### テストアカウント作成

**登録画面で作成:**

1. http://localhost:3000 を開く
2. 「登録する」をクリック
3. 以下を入力:
   - ユーザー名: `Test User`
   - メール: `test@example.com`
   - パスワード: `password123` (8文字以上)
4. 「登録」をクリック

**ログイン:**

1. ログイン画面で以下を入力
   - メール: `test@example.com`
   - パスワード: `password123`
2. 「ログイン」をクリック
3. ダッシュボードに遷移することを確認

---

## 🔌 API エンドポイント

### 認証関連

```bash
# ユーザー登録
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'

# ログイン
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# ログインユーザー情報取得
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"

# トークンリフレッシュ
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "{refresh_token}"
  }'
```

---

## 🧪 テスト実行

### バックエンド テスト（Docker推奨）

```bash
cd english-diary

# Docker Compose でテスト実行
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# または直接pytest実行
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html
```

### テストカバレッジ確認

```bash
# HTML レポート生成
cd backend
pytest --cov=app --cov-report=html

# ブラウザで htmlcov/index.html を開く
```

### 特定のテストを実行

```bash
cd backend

# 認証テストのみ
pytest tests/test_auth.py -v

# 日記テストのみ
pytest tests/test_diary.py -v

# 特定のテストクラス
pytest tests/test_auth.py::TestUserRegistration -v

# 特定のテスト関数
pytest tests/test_auth.py::TestUserRegistration::test_register_success -v
```

### CI/CD パイプライン

GitHub Actions で以下が自動実行されます：

- ✅ pytest でテスト実行
- ✅ カバレッジレポート生成
- ✅ Codecov へのアップロード

**詳細**: [CI_TESTING_GUIDE.md](../CI_TESTING_GUIDE.md) を参照

---

## 🔧 トラブルシューティング

### ポート競合

```bash
# 既存の接続を確認
lsof -i :8000    # Backend
lsof -i :3000    # Frontend
lsof -i :5432    # Postgres

# 強制終了（必要に応じて）
kill -9 <PID>
```

### DB 接続エラー

```bash
# 手動で Postgres 起動
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine

# DB 作成
docker exec postgres createdb -U postgres english_diary
```

### React ビルドエラー

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 📊 次のステップ

1. **日記 CRUD API 実装**
   - モデル: Diary
   - ルーター: routers/diaries.py
   - サービス: services/diary_service.py

2. **カレンダー UI 実装**
   - コンポーネント: pages/CalendarPage.tsx
   - API 連携: services/api.ts

3. **AI 分析 API 統合**
   - OpenAI API 設定
   - ルーター: routers/ai.py
   - 非同期タスク（Celery）

---

## 📚 参考

- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
- [React ドキュメント](https://react.dev/)
- [SQLAlchemy ドキュメント](https://docs.sqlalchemy.org/)
- [設計書](./ENGLISH_DIARY_DESIGN_V2.md)

---

**実装スタート！** 🚀
