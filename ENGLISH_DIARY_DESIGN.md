# 英語日記アプリ 詳細設計書（v2）

**バージョン**: 2.0  
**作成日**: 2026-04-21  
**ステータス**: 実装準備完了

---

## 📋 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [技術スタック](#2-技術スタック)
3. [機能一覧](#3-機能一覧)
4. [画面構成](#4-画面構成)
5. [API設計](#5-api設計)
6. [データベース設計](#6-データベース設計)
7. [ER図](#7-er図)
8. [システムアーキテクチャ](#8-システムアーキテクチャ)
9. [処理フロー](#9-処理フロー)
10. [設計のポイント](#10-設計のポイント)
11. [拡張戦略](#11-拡張戦略)
12. [開発ロードマップ](#12-開発ロードマップ)

---

## 1. プロジェクト概要

### 🎯 ビジョン

英語学習者が日々の日記を通じて、AIからの添削フィードバックを受け、継続的に英語スキルを向上させることができるアプリケーション。

### 📌 MVP（最小限の実行可能製品）

- ✅ ユーザー認証（登録・ログイン）
- ✅ 日記の作成・編集・削除
- ✅ AI による英文添削
- ✅ カレンダー表示

### 🚀 将来の拡張

- 📱 スピーキング機能（音声シャドーイング）
- 🎯 スコアリング・学習履歴
- 📊 学習分析ダッシュボード
- 🏆 TOEIC対策モード

---

## 2. 技術スタック

### フロントエンド

| 項目           | 技術                |
| -------------- | ------------------- |
| フレームワーク | React 18            |
| 言語           | TypeScript          |
| 状態管理       | Redux / Context API |
| スタイリング   | Tailwind CSS        |
| HTTP Client    | axios               |
| カレンダー     | react-big-calendar  |

### バックエンド

| 項目           | 技術            |
| -------------- | --------------- |
| フレームワーク | FastAPI 0.104.1 |
| 言語           | Python 3.11     |
| ORM            | SQLAlchemy 2.0  |
| Database       | PostgreSQL 16   |
| 認証           | JWT + bcrypt    |
| API Doc        | OpenAPI/Swagger |
| Async Task     | Celery + Redis  |

### インフラ

| 項目         | 技術                 |
| ------------ | -------------------- |
| コンテナ     | Docker               |
| コンテナ実行 | AWS ECS Fargate      |
| データベース | AWS RDS (PostgreSQL) |
| キャッシュ   | Redis (ElastiCache)  |
| ストレージ   | S3（将来）           |
| CI/CD        | GitHub Actions       |

### AI・External Services

| 項目   | 技術                |
| ------ | ------------------- |
| AI添削 | OpenAI API (GPT-4)  |
| メール | SES または SendGrid |

---

## 3. 機能一覧

### 3.1 認証機能

```
✅ ユーザー登録（Email + Password）
✅ ログイン
✅ ログアウト
✅ ログインユーザー情報取得
✅ パスワード変更（将来）
✅ メール認証（将来）
```

### 3.2 日記機能（MVP）

```
✅ 日記作成（title + content）
✅ 日記一覧取得（日付でフィルター可能）
✅ 日記詳細取得
✅ 日記編集
✅ 日記削除
```

### 3.3 AI添削機能

```
✅ 英文添削リクエスト
✅ 添削結果取得（修正点 + 説明）
✅ 添削履歴管理
```

### 3.4 カレンダー機能

```
✅ 月単位の日記表示
✅ 日付クリックで日記詳細 or 新規作成へ遷移
✅ 日付ごとに添削完了状態を表示
```

### 3.5 ユーザープロフィール

```
✅ プロフィール表示
✅ プロフィール編集（名前、メール など）
✅ 統計情報表示（総日記数、今月の数 など）
```

---

## 4. 画面構成

### 4.1 認証関連

#### ログイン画面

```
┌─────────────────────────────┐
│      LangLog                │
│       ログイン画面           │
├─────────────────────────────┤
│ メールアドレス               │
│ [________________]           │
│                             │
│ パスワード                  │
│ [________________]           │
│                             │
│ [  ログイン  ]  [新規登録]  │
└─────────────────────────────┘
```

#### 登録画面

```
┌─────────────────────────────┐
│      新規ユーザー登録        │
├─────────────────────────────┤
│ 名前                        │
│ [________________]           │
│                             │
│ メールアドレス               │
│ [________________]           │
│                             │
│ パスワード                  │
│ [________________]           │
│                             │
│ [  登録  ]                  │
└─────────────────────────────┘
```

### 4.2 メイン画面

#### カレンダー画面

```
┌─────────────────────────────────────┐
│  2026年4月                   [+新規]  │
├──────────┬──────────┬────────────────┤
│ Sun | Mon| Tue | Wed| Thu | Fri | Sat│
├──────────┼──────────┼────────────────┤
│    |  1  │  2  │  3  │  4  │  5  │  6  │
│ 7  │ 8●  │  9  │ 10  │ 11  │ 12  │ 13  │  ● = 日記あり
│ 14 │ 15● │ 16  │ 17● │ 18  │ 19  │ 20  │
│ 21 │ 22  │ 23  │ 24  │ 25  │ 26  │ 27  │
│ 28 │ 29  │ 30  │     │     │     │     │
└─────────────────────────────────────┘
```

#### 日記入力・編集画面

```
┌──────────────────────────────────────┐
│  日記作成・編集                  [✓保存]│
├──────────────────────────────────────┤
│ 日付: 2026-04-21                     │
│ タイトル:                            │
│ [________________]                   │
│                                      │
│ 本文:                               │
│ ┌──────────────────────────────────┐│
│ │ Today I went to school. I...      ││
│ │                                   ││
│ │                                   ││
│ └──────────────────────────────────┘│
│                                      │
│ [  AI添削 ]                          │
│                                      │
│ ---- 添削結果 ----                   │
│ ✏️ 修正点:                          │
│  • "went" の使い方は正しい          │
│  • より自然な表現...                │
│                                      │
│ [削除]                              │
└──────────────────────────────────────┘
```

#### マイページ

```
┌──────────────────────────────┐
│  マイページ                  │
├──────────────────────────────┤
│ 👤 ユーザー情報              │
│  名前: Taro Yamada           │
│  メール: taro@example.com    │
│  登録日: 2026-01-15          │
│                             │
│ [編集]                      │
│                             │
│ 📊 統計情報                 │
│  総日記数: 25               │
│  今月: 8                   │
│  今週: 3                   │
│  平均文字数: 350文字        │
│                             │
│ [ログアウト]                │
└──────────────────────────────┘
```

---

## 5. API設計

### 5.1 認証系 API

#### 1. ユーザー登録

```
POST /api/v1/auth/register

Request:
{
  "name": "Taro Yamada",
  "email": "taro@example.com",
  "password": "SecurePassword123!"
}

Response (201):
{
  "id": "uuid-001",
  "name": "Taro Yamada",
  "email": "taro@example.com",
  "created_at": "2026-04-21T10:30:00Z"
}

Error (400):
{
  "error": "Email already exists"
}
```

#### 2. ログイン

```
POST /api/v1/auth/login

Request:
{
  "email": "taro@example.com",
  "password": "SecurePassword123!"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "user": {
    "id": "uuid-001",
    "name": "Taro Yamada",
    "email": "taro@example.com"
  }
}

Error (401):
{
  "error": "Invalid credentials"
}
```

#### 3. ログアウト

```
POST /api/v1/auth/logout

Headers:
Authorization: Bearer {access_token}

Response (200):
{
  "message": "Logged out successfully"
}
```

#### 4. ログインユーザー取得

```
GET /api/v1/auth/me

Headers:
Authorization: Bearer {access_token}

Response (200):
{
  "id": "uuid-001",
  "name": "Taro Yamada",
  "email": "taro@example.com",
  "created_at": "2026-04-21T10:30:00Z"
}
```

#### 5. トークンリフレッシュ

```
POST /api/v1/auth/refresh

Request:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer"
}

Error (401):
{
  "error": "invalid_token",
  "message": "Invalid or expired refresh token"
}
```

---

### 5.2 ユーザー API

#### 1. ユーザー情報取得

```
GET /api/v1/users/me

Headers:
Authorization: Bearer {access_token}

Response (200):
{
  "id": "uuid-001",
  "name": "Taro Yamada",
  "email": "taro@example.com",
  "gender": "male",
  "birth_date": "1990-01-15",
  "created_at": "2026-04-21T10:30:00Z"
}
```

#### 2. ユーザー情報更新

```
PUT /api/v1/users/me

Headers:
Authorization: Bearer {access_token}

Request:
{
  "name": "Taro Yamada Updated",
  "gender": "male",
  "birth_date": "1990-01-15"
}

Response (200):
{
  "id": "uuid-001",
  "name": "Taro Yamada Updated",
  "email": "taro@example.com",
  "updated_at": "2026-04-21T15:30:00Z"
}
```

---

### 5.3 日記 API

#### 1. 日記一覧取得（ページネーション対応）

```
GET /api/v1/diaries?date=2026-04-21&limit=10&offset=0

Headers:
Authorization: Bearer {access_token}

Query Parameters:
- date: 対象日付（YYYY-MM-DD形式）
- limit: 1ページあたりのアイテム数（デフォルト: 10、最大: 100）
- offset: スキップするアイテム数（デフォルト: 0）

Response (200):
{
  "items": [
    {
      "id": "uuid-d001",
      "user_id": "uuid-001",
      "date": "2026-04-21",
      "title": "My First Day in Tokyo",
      "content": "Today I arrived in Tokyo. The city is very busy...",
      "corrected_content": null,
      "has_feedback": false,
      "created_at": "2026-04-21T10:30:00Z",
      "updated_at": "2026-04-21T10:30:00Z"
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0,
  "has_next": true
}
```

#### 月単位での取得（カレンダー用）

```
GET /api/v1/diaries?month=2026-04

Response (200):
{
  "month": "2026-04",
  "diary_dates": [
    "2026-04-01",
    "2026-04-08",
    "2026-04-15",
    "2026-04-21"
  ]
}
```

#### 2. 日記詳細取得

```
GET /api/v1/diaries/uuid-d001

Headers:
Authorization: Bearer {access_token}

Response (200):
{
  "id": "uuid-d001",
  "user_id": "uuid-001",
  "date": "2026-04-21",
  "title": "My First Day in Tokyo",
  "content": "Today I arrived in Tokyo. The city is very busy...",
  "corrected_content": "Today I arrived in Tokyo. The city is extremely busy...",
  "correction_points": [
    {
      "original": "very busy",
      "corrected": "extremely busy",
      "reason": "より自然で表現力豊かな表現"
    }
  ],
  "has_feedback": true,
  "feedback_created_at": "2026-04-21T11:00:00Z",
  "created_at": "2026-04-21T10:30:00Z",
  "updated_at": "2026-04-21T10:30:00Z"
}
```

#### 3. 日記作成

```
POST /api/v1/diaries

Headers:
Authorization: Bearer {access_token}

Request:
{
  "date": "2026-04-21",
  "title": "My First Day in Tokyo",
  "content": "Today I arrived in Tokyo. The city is very busy..."
}

Response (201):
{
  "id": "uuid-d001",
  "user_id": "uuid-001",
  "date": "2026-04-21",
  "title": "My First Day in Tokyo",
  "content": "Today I arrived in Tokyo. The city is very busy...",
  "created_at": "2026-04-21T10:30:00Z"
}
```

#### 4. 日記編集

```
PUT /api/v1/diaries/uuid-d001

Headers:
Authorization: Bearer {access_token}

Request:
{
  "title": "My First Day in Tokyo (Updated)",
  "content": "Today I arrived in Tokyo. The city is extremely busy..."
}

Response (200):
{
  "id": "uuid-d001",
  "title": "My First Day in Tokyo (Updated)",
  "content": "Today I arrived in Tokyo. The city is extremely busy...",
  "updated_at": "2026-04-21T15:30:00Z"
}
```

#### 5. 日記削除

```
DELETE /api/v1/diaries/uuid-d001

Headers:
Authorization: Bearer {access_token}

Response (204): No Content
```

---

### 5.4 AI添削 API（汎用設計）

#### 1. AI分析リクエスト（非同期処理、ステータス追跡）

```
POST /api/v1/ai/analyze

Headers:
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "type": "writing",        # ← typeで機能を分岐
  "content": "I goed to school yesterday.",
  "diary_id": "uuid-d001"   # ← optional
}

Response (202 Accepted - 非同期処理開始):
{
  "analysis_id": "uuid-a001",
  "type": "writing",
  "status": "processing",
  "message": "Analysis in progress. Check /ai/analyze/{analysis_id} for results."
}
```

#### 分析結果の確認（GET）

```
GET /api/v1/ai/analyze/uuid-a001

Headers:
Authorization: Bearer {access_token}

# 処理完了時
Response (200):
{
  "analysis_id": "uuid-a001",
  "type": "writing",
  "status": "completed",
  "original": "I goed to school yesterday.",
  "corrected": "I went to school yesterday.",
  "correction_points": [
    {
      "original": "goed",
      "corrected": "went",
      "reason": "不規則動詞の過去形。'go'の過去形は'went'です。"
    }
  ],
  "feedback_level": "basic",
  "processing_time_ms": 2340,
  "created_at": "2026-04-21T10:30:00Z",
  "completed_at": "2026-04-21T10:30:02Z"
}

# 処理中の場合
Response (202):
{
  "analysis_id": "uuid-a001",
  "status": "processing",
  "message": "Still processing. Please retry in a few seconds."
}

# 処理失敗の場合
Response (200):
{
  "analysis_id": "uuid-a001",
  "status": "failed",
  "error": "ai_service_unavailable",
  "message": "AI service unavailable. Please try again later."
}
```

#### 将来の拡張（同じエンドポイントで対応可能）

```
# スピーキング機能の場合
POST /api/v1/ai/analyze
{
  "type": "speaking",
  "audio_url": "s3://bucket/audio.wav",
  "diary_id": "uuid-d001"
}

Response (202):
{ "analysis_id": "uuid-a002", "status": "processing" }

# 完了確認
GET /api/v1/ai/analyze/uuid-a002
Response (200):
{
  "type": "speaking",
  "status": "completed",
  "pronunciation_score": 8.5,
  "fluency_score": 7.8,
  "feedback": "発音は良いですが、イントネーションを改善できます"
}

# シャドーイングの場合
POST /api/v1/ai/analyze
{
  "type": "shadowing",
  "reference_text": "...",
  "user_text": "..."
}

Response (202):
{ "analysis_id": "uuid-a003", "status": "processing" }

# 完了確認
GET /api/v1/ai/analyze/uuid-a003
Response (200):
{
  "type": "shadowing",
  "status": "completed",
  "accuracy": 0.92,
  "issues": [...]
}
```

---

### 5.5 エラーレスポンス仕様

全エンドポイント共通で以下のエラーレスポンスが返却されます。

#### HTTP Status Codes

| Code | 説明                  | 例                                     |
| ---- | --------------------- | -------------------------------------- |
| 400  | Bad Request           | バリデーションエラー（無効な形式など） |
| 401  | Unauthorized          | トークンが無効 or 期限切れ             |
| 403  | Forbidden             | リソースへのアクセス権がない           |
| 404  | Not Found             | リソースが見つからない                 |
| 409  | Conflict              | 既存リソースと競合（メール重複など）   |
| 429  | Too Many Requests     | レート制限超過                         |
| 500  | Internal Server Error | サーバーエラー                         |

#### エラーレスポンス形式

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field": "error description"
  },
  "timestamp": "2026-04-21T10:30:00Z",
  "request_id": "uuid-req-001"
}
```

#### 具体例

**バリデーションエラー（400）**

```json
{
  "error": "validation_error",
  "message": "Validation failed",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  }
}
```

**トークン無効（401）**

```json
{
  "error": "invalid_token",
  "message": "Access token is invalid or expired. Please refresh.",
  "details": {
    "hint": "Use POST /auth/refresh with your refresh_token"
  }
}
```

**権限なし（403）**

```json
{
  "error": "forbidden",
  "message": "You do not have permission to access this diary"
}
```

**リソース未検出（404）**

```json
{
  "error": "not_found",
  "message": "Diary with id 'uuid-d001' not found"
}
```

**メール重複（409）**

```json
{
  "error": "conflict",
  "message": "Email already registered",
  "details": {
    "email": "taro@example.com already exists"
  }
}
```

**レート制限超過（429）**

```json
{
  "error": "rate_limit_exceeded",
  "message": "Daily AI analysis limit reached",
  "details": {
    "limit": 5,
    "used": 5,
    "reset_at": "2026-04-22T00:00:00Z"
  },
  "headers": {
    "X-RateLimit-Limit": "5",
    "X-RateLimit-Remaining": "0",
    "X-RateLimit-Reset": "2026-04-22T00:00:00Z"
  }
}
```

---

---

## 6. データベース設計

### 6.1 USERS テーブル（ユーザー管理）

| カラム名      | 型           | 制約             | 説明                 |
| ------------- | ------------ | ---------------- | -------------------- |
| id            | UUID         | PRIMARY KEY      | ユーザーID           |
| name          | VARCHAR(100) | NOT NULL         | ユーザー名           |
| email         | VARCHAR(255) | NOT NULL, UNIQUE | メールアドレス       |
| password_hash | VARCHAR(255) | NOT NULL         | パスワードハッシュ   |
| gender        | VARCHAR(20)  |                  | 性別                 |
| birth_date    | DATE         |                  | 生年月日             |
| created_at    | TIMESTAMP    | DEFAULT NOW()    | 作成日時             |
| updated_at    | TIMESTAMP    | DEFAULT NOW()    | 更新日時             |
| deleted_at    | TIMESTAMP    | NULL             | 削除日時（論理削除） |

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  gender VARCHAR(20),
  birth_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

---

### 6.2 DIARIES テーブル（日記管理）

| カラム名          | 型           | 制約          | 説明                 |
| ----------------- | ------------ | ------------- | -------------------- |
| id                | UUID         | PRIMARY KEY   | 日記ID               |
| user_id           | UUID         | FOREIGN KEY   | ユーザーID           |
| date              | DATE         | NOT NULL      | 日記の日付           |
| title             | VARCHAR(255) | NOT NULL      | タイトル             |
| content           | TEXT         | NOT NULL      | 原文                 |
| corrected_content | TEXT         |               | 添削後のテキスト     |
| correction_points | JSONB        |               | 修正点の詳細         |
| has_feedback      | BOOLEAN      | DEFAULT FALSE | 添削済みフラグ       |
| created_at        | TIMESTAMP    | DEFAULT NOW() | 作成日時             |
| updated_at        | TIMESTAMP    | DEFAULT NOW() | 更新日時             |
| deleted_at        | TIMESTAMP    | NULL          | 削除日時（論理削除） |

```sql
CREATE TABLE diaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  corrected_content TEXT,
  correction_points JSONB,
  has_feedback BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
);

CREATE INDEX idx_diaries_user_date ON diaries(user_id, date);
CREATE INDEX idx_diaries_user_created ON diaries(user_id, created_at DESC);
CREATE INDEX idx_diaries_date ON diaries(date);
```

---

### 6.3 LEARNING_CONTENTS テーブル（将来の拡張用）

| カラム名   | 型           | 制約          | 説明                           |
| ---------- | ------------ | ------------- | ------------------------------ |
| id         | UUID         | PRIMARY KEY   | コンテンツID                   |
| user_id    | UUID         | FOREIGN KEY   | ユーザーID                     |
| type       | VARCHAR(50)  | NOT NULL      | writing / speaking / shadowing |
| content    | TEXT         |               | 入力内容                       |
| result     | JSONB        |               | 分析結果（汎用）               |
| score      | DECIMAL(3,1) |               | スコア                         |
| created_at | TIMESTAMP    | DEFAULT NOW() | 作成日時                       |

```sql
CREATE TABLE learning_contents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  content TEXT,
  result JSONB,
  score DECIMAL(3,1),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_learning_contents_user_type ON learning_contents(user_id, type);
CREATE INDEX idx_learning_contents_created ON learning_contents(created_at DESC);
```

---

### 6.4 ANALYSIS_HISTORY テーブル（AI分析履歴・将来用）

| カラム名        | 型          | 制約                   | 説明                    |
| --------------- | ----------- | ---------------------- | ----------------------- |
| id              | UUID        | PRIMARY KEY            | 分析ID                  |
| diary_id        | UUID        | FOREIGN KEY (optional) | 日記ID                  |
| user_id         | UUID        | FOREIGN KEY            | ユーザーID              |
| type            | VARCHAR(50) | NOT NULL               | writing / speaking など |
| input_text      | TEXT        |                        | 入力テキスト            |
| analysis_result | JSONB       | NOT NULL               | 分析結果                |
| created_at      | TIMESTAMP   | DEFAULT NOW()          | 作成日時                |

```sql
CREATE TABLE analysis_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  diary_id UUID REFERENCES diaries(id) ON DELETE SET NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  input_text TEXT,
  analysis_result JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analysis_history_diary ON analysis_history(diary_id);
CREATE INDEX idx_analysis_history_user ON analysis_history(user_id, created_at DESC);
```

---

## 7. ER図

### MVP フェーズ（Phase 1）

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ id (PK) [UUID]  │
│ name            │
│ email (UNIQUE)  │
│ password_hash   │
│ gender          │
│ birth_date      │
│ created_at      │
│ updated_at      │
│ deleted_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────┐
│     DIARIES         │
├─────────────────────┤
│ id (PK) [UUID]      │
│ user_id (FK)        │
│ date                │
│ title               │
│ content             │
│ corrected_content   │
│ correction_points   │
│ has_feedback        │
│ created_at          │
│ updated_at          │
│ deleted_at          │
└─────────────────────┘
```

### 将来の拡張フェーズ（Phase 3）

```
                    ┌─────────────────┐
                    │     USERS       │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              1:N   │                 │ 1:N
         ┌──────────▼──────────┐ ┌────▼──────────────────┐
         │     DIARIES         │ │ LEARNING_CONTENTS     │
         │ (writing特化UI)     │ │ (拡張の中核)          │
         └─────────────────────┘ ├──────────────────────┤
                                 │ id (PK) [UUID]       │
                                 │ user_id (FK)         │
                                 │ type (writing/...    │
                                 │       speaking/...   │
                                 │       shadowing)     │
                                 │ content              │
                                 │ result (JSON)        │
                                 │ score                │
                                 │ created_at           │
                                 └──────────────────────┘

         ┌─────────────────────────┐
         │ ANALYSIS_HISTORY        │
         ├─────────────────────────┤
         │ id (PK) [UUID]          │
         │ diary_id (FK, optional) │
         │ user_id (FK)            │
         │ type                    │
         │ input_text              │
         │ analysis_result (JSON)  │
         │ created_at              │
         └─────────────────────────┘
```

### ER図の設計意図

#### ① DIARIESは「writing特化」

- **目的**: MVPはここだけでサービス成立
- **特徴**: UIとカレンダーに直結
- **実装**: Phase 1 で完成

#### ② LEARNING_CONTENTSが拡張のカギ

- **目的**: 将来の speaking / shadowing に対応
- **設計**: type フィールドで機能を分岐
- **メリット**: カラム増加がない

| type      | 説明           | result 例                                           |
| --------- | -------------- | --------------------------------------------------- |
| writing   | 日記添削       | `{ "corrections": [...], "score": 8.2 }`            |
| speaking  | 発音認識       | `{ "pronunciation_score": 8.5, "feedback": "..." }` |
| shadowing | シャドーイング | `{ "accuracy": 0.92, "issues": [...] }`             |

#### ③ なぜテーブルを分けたか

**❌ DIARIESだけでやる場合**

```
content: 日記テキスト
audio_url: 音声ファイル（話す場合）
video_url: ビデオファイル（動画の場合）
→ カラムがどんどん増える
→ NULLだらけになる
→ クエリが複雑化
```

**✅ テーブル分離**

```
DIARIES: 日記テキストのみ
LEARNING_CONTENTS: 全ての学習コンテンツ
→ 綺麗に拡張可能
→ NULLなし
→ クエリシンプル
→ 新機能追加が楽
```

#### ④ 現実的な開発順序

**MVP（Phase 1）: 最小限**

```
USERS テーブル
DIARIES テーブル
↓
ユーザー管理 + 日記管理 + カレンダーUI
```

**拡張フェーズ（Phase 2-3）**

```
LEARNING_CONTENTS 追加
ANALYSIS_HISTORY 追加
↓
AI 機能の強化
スピーキング・シャドーイング対応
```

---

## 8. システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React SPA)                         │
│                    ├─ Login / Register                          │
│                    ├─ Calendar                                  │
│                    ├─ Diary Editor                              │
│                    ├─ My Page                                   │
│                    └─ AI Feedback Display                       │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTPS
┌────────────────────▼────────────────────────────────────────────┐
│                  FastAPI Backend (ECS Fargate)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Routers                                                  │  │
│  │ ├─ /auth      (login, register, logout)                │  │
│  │ ├─ /users     (profile, update)                         │  │
│  │ ├─ /diaries   (CRUD operations)                         │  │
│  │ └─ /ai        (analyze - writing/speaking/shadowing)   │  │
│  └──────┬───────────────────────────────────────────────────┘  │
│         │                                                       │
│  ┌──────▼───────────────────────────────────────────────────┐  │
│  │ Services                                                 │  │
│  │ ├─ AuthService                                          │  │
│  │ ├─ UserService                                          │  │
│  │ ├─ DiaryService                                         │  │
│  │ ├─ AIService (OpenAI integration)                       │  │
│  │ └─ AnalysisService                                      │  │
│  └──────┬───────────────────────────────────────────────────┘  │
│         │                                                       │
│  ┌──────▼───────────────────────────────────────────────────┐  │
│  │ Repositories (SQLAlchemy ORM)                            │  │
│  │ ├─ UserRepository                                       │  │
│  │ ├─ DiaryRepository                                      │  │
│  │ ├─ AnalysisRepository                                   │  │
│  │ └─ ...                                                  │  │
│  └──────┬───────────────────────────────────────────────────┘  │
│         │                                                       │
└─────────┼───────────────────────────────────────────────────────┘
          │
    ┌─────┴─────────────┬──────────────────┬──────────────┐
    │                   │                  │              │
┌───▼────┐  ┌──────────▼──┐  ┌───────────▼──┐  ┌─────────▼────┐
│PostgreSQL │  │   Redis    │  │  OpenAI API  │  │  SendGrid    │
│  (RDS)    │  │(ElastiCache)│  │   (Chat GPT) │  │   (Email)    │
│  (Users)  │  │  (Sessions)│  │              │  │              │
│  (Diaries)│  │  (Cache)   │  │              │  │              │
└───────────┘  └────────────┘  └──────────────┘  └──────────────┘
```

---

## 9. 処理フロー

### 9.1 日記作成フロー

```
1. ユーザー入力
   ┌─────────────────────────────┐
   │ Frontend: 日記入力画面       │
   │ - タイトル入力              │
   │ - 本文入力                  │
   └────────────┬────────────────┘

2. リクエスト送信
   ┌────────────▼────────────────┐
   │ POST /api/v1/diaries        │
   │ {                           │
   │   "date": "2026-04-21",     │
   │   "title": "...",           │
   │   "content": "..."          │
   │ }                           │
   └────────────┬────────────────┘

3. バックエンド処理
   ┌────────────▼────────────────┐
   │ DiaryService.create()       │
   │ - バリデーション            │
   │ - DB保存                    │
   │ - レスポンス返却            │
   └────────────┬────────────────┘

4. DB保存
   ┌────────────▼────────────────┐
   │ DIARIES テーブル            │
   │ ✓ 保存完了                  │
   └─────────────────────────────┘
```

### 9.2 AI 添削フロー（非同期処理）

```
1. ユーザーが「AI添削」ボタンをクリック
   ┌──────────────────────────────────┐
   │ Frontend                         │
   │ ボタンクリック → API送信          │
   └──────────────┬───────────────────┘

2. リクエスト送信
   ┌──────────────▼───────────────────┐
   │ POST /api/v1/ai/analyze          │
   │ {                                │
   │   "type": "writing",             │
   │   "content": "I goed to...",     │
   │   "diary_id": "uuid-d001"        │
   │ }                                │
   └──────────────┬───────────────────┘

3. バックエンド: 非同期タスク登録
   ┌──────────────▼───────────────────┐
   │ AIService.analyze()              │
   │ - Celery タスク登録              │
   │ - 即座にレスポンス返却            │
   │   status: "processing"           │
   └──────────────┬───────────────────┘

4. バックグラウンド処理
   ┌──────────────▼───────────────────┐
   │ Celery Task                      │
   │ - OpenAI API 呼び出し             │
   │ - 添削結果取得                    │
   │ - DIARIES テーブル更新            │
   └──────────────┬───────────────────┘

5. OpenAI API 処理
   ┌──────────────▼───────────────────┐
   │ OpenAI: GPT-4                    │
   │ - 添削内容生成                    │
   │ - JSON形式で返却                  │
   └──────────────┬───────────────────┘

6. DB更新
   ┌──────────────▼───────────────────┐
   │ DIARIES テーブル                 │
   │ - corrected_content 更新          │
   │ - correction_points 更新          │
   │ - has_feedback = true 設定        │
   └──────────────────────────────────┘

7. フロント: ポーリング or WebSocket
   ┌──────────────────────────────────┐
   │ Frontend: 結果表示                │
   │ GET /api/v1/diaries/uuid-d001    │
   │ → 添削結果を画面に表示             │
   └──────────────────────────────────┘
```

---

## 10. 設計のポイント

### 10.1 AI API の抽象化

```python
# AIService は type で機能を分岐する設計

@router.post("/ai/analyze")
def analyze(request: AnalyzeRequest):
    """
    request.type に応じて処理を分岐
    """
    if request.type == "writing":
        return ai_service.analyze_writing(request.content)
    elif request.type == "speaking":
        return ai_service.analyze_speaking(request.audio_url)
    elif request.type == "shadowing":
        return ai_service.analyze_shadowing(request.text)
```

**メリット:**

- ✅ エンドポイント増加なし
- ✅ 新機能追加が簡単
- ✅ クライアント側の変更最小限

### 10.2 カレンダー最適化

```python
# date カラムでシンプルに管理

# 月別の日記一覧を高速に取得
SELECT DISTINCT date FROM diaries
WHERE user_id = ? AND EXTRACT(YEAR FROM date) = 2026
AND EXTRACT(MONTH FROM date) = 4
ORDER BY date;

# インデックス活用で高速化
CREATE INDEX idx_diaries_user_date ON diaries(user_id, date);
```

### 10.3 拡張性

```sql
-- writing → speaking へ拡張する際
-- LEARNING_CONTENTS テーブルで吸収可能

-- writing は DIARIES で UI特化
-- speaking は LEARNING_CONTENTS で汎用対応

INSERT INTO learning_contents (user_id, type, content, result)
VALUES (?, 'speaking', ?, ?);
```

### 10.4 Rate Limiting 戦略

AI API は OpenAI の API コストが発生するため、ユーザーごとにレート制限を実装します。

**制限内容:**

```
・日次制限: 1ユーザーあたり最大 5回/日 の AI 分析
・時間制限: 1時間あたり最大 2回 の AI 分析
・バースト制限: 連続リクエストは 5秒間隔を空ける必要あり
```

**実装方法:**

```python
# Redis を使用したレート制限
key = f"ai_analysis_limit:{user_id}:{date}"
count = redis.incr(key)
if count > DAILY_LIMIT:
    raise RateLimitError()
redis.expire(key, 86400)  # 24時間でリセット
```

**レスポンスヘッダー:**

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 2
X-RateLimit-Reset: 2026-04-22T00:00:00Z
```

**制限超過時のレスポンス（429）:**

```json
{
  "error": "rate_limit_exceeded",
  "message": "Daily AI analysis limit reached",
  "details": {
    "limit": 5,
    "used": 5,
    "reset_at": "2026-04-22T00:00:00Z"
  }
}
```

**将来の拡張:**

- 有料プランでレート制限を緩和
- ユーザーレベルごとに異なる制限
- AI 使用量のモニタリング・アラート

---

## 11. 拡張戦略

### Phase 1: MVP（4週間）

```
✅ Users + Diaries テーブル
✅ Auth API
✅ Diary CRUD API
✅ AI Analyze API (writing only)
✅ Frontend: Login + Calendar + Editor
```

### Phase 2: AI 機能強化（2週間）

```
🔄 分析履歴管理
🔄 スコアリング機能
🔄 OpenAI API の最適化
```

### Phase 3: スピーキング対応（4週間）

```
🔄 LEARNING_CONTENTS テーブル追加
🔄 音声入力対応
🔄 Analyze API 拡張（speaking/shadowing）
🔄 Frontend: 音声アップロード UI
```

### Phase 4: ダッシュボード・分析（3週間）

```
🔄 ANALYSIS_HISTORY テーブル追加
🔄 学習統計ダッシュボード
🔄 成績表示機能
```

---

## 12. 開発ロードマップ

### タイムライン

```
Week 1-2: DB設計 + Backend基盤
├─ PostgreSQL セットアップ
├─ SQLAlchemy モデル定義
├─ Repository パターン実装
└─ JWT認証実装

Week 3-4: Core API
├─ Auth API 実装
├─ Diary CRUD 実装
├─ AI Analyze (writing) 実装
└─ テスト作成

Week 5: Frontend基盤
├─ React セットアップ
├─ 認証フロー実装
├─ 日記エディタ実装
└─ カレンダーUI実装

Week 6: 統合テスト + デプロイ
├─ E2E テスト
├─ Docker化
├─ ECS デプロイ
└─ 本番運用開始
```

---

## 📝 まとめ

### この設計の強み

✅ **シンプル**: MVP はテーブル 2 つだけ  
✅ **拡張性**: type 分岐で新機能追加可能  
✅ **クリア**: ER図で全体像が一目瞭然  
✅ **実装準備**: これだけあれば実装に入れる

### 次に必要なもの

1. **FastAPI ディレクトリ構成**

   ```
   english_diary/
   ├─ app/
   │  ├─ main.py
   │  ├─ routers/
   │  │  ├─ auth.py
   │  │  ├─ users.py
   │  │  ├─ diaries.py
   │  │  └─ ai.py
   │  ├─ services/
   │  │  ├─ auth_service.py
   │  │  ├─ diary_service.py
   │  │  └─ ai_service.py
   │  ├─ repositories/
   │  ├─ models/
   │  ├─ schemas/
   │  └─ config.py
   ├─ tests/
   ├─ docker-compose.yml
   └─ requirements.txt
   ```

2. **SQLAlchemy モデル定義**
3. **Pydantic Schema 定義**
4. **テスト スイート**

---

**設計書 v2.0 完成** ✅
