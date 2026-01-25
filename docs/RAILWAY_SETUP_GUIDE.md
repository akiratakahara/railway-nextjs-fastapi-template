# Railway環境構築ガイド

このドキュメントでは、Railway上でNext.js（フロントエンド）+ FastAPI（バックエンド）+ PostgreSQL（DB）の構成を構築する方法と、502エラーを防ぐための設定を説明します。

---

## 目次

1. [アーキテクチャ概要](#アーキテクチャ概要)
2. [プロジェクト作成](#プロジェクト作成)
3. [PostgreSQL設定](#postgresql設定)
4. [バックエンド設定（FastAPI）](#バックエンド設定fastapi)
5. [フロントエンド設定（Next.js）](#フロントエンド設定nextjs)
6. [環境変数一覧](#環境変数一覧)
7. [502エラー対策](#502エラー対策)
8. [CORS設定](#cors設定)
9. [トラブルシューティング](#トラブルシューティング)

---

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                        Railway                               │
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │   Frontend       │    │   Backend        │              │
│  │   (Next.js)      │───▶│   (FastAPI)      │              │
│  │   Port: 3000     │    │   Port: 8000     │              │
│  └──────────────────┘    └────────┬─────────┘              │
│                                   │                         │
│                          ┌────────▼─────────┐              │
│                          │   PostgreSQL     │              │
│                          │   (Railway DB)   │              │
│                          └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

**URL構成例:**
- フロントエンド: `https://myapp-production.up.railway.app`
- バックエンド: `https://myapp-backend-production.up.railway.app`
- DB: Railway内部接続（`${{Postgres.DATABASE_URL}}`）

---

## プロジェクト作成

### 1. Railwayプロジェクト作成

1. [Railway](https://railway.app) にログイン
2. 「New Project」→「Empty Project」を選択
3. プロジェクト名を設定

### 2. サービス追加

1つのプロジェクトに3つのサービスを追加:

1. **PostgreSQL**: 「Add」→「Database」→「PostgreSQL」
2. **Backend**: 「Add」→「GitHub Repo」→ バックエンドのリポジトリを選択
3. **Frontend**: 「Add」→「GitHub Repo」→ フロントエンドのリポジトリを選択

---

## PostgreSQL設定

### 自動設定される環境変数

Railwayが自動で以下の変数を提供:

| 変数名 | 説明 |
|--------|------|
| `DATABASE_URL` | 完全な接続URL |
| `PGHOST` | ホスト名 |
| `PGPORT` | ポート |
| `PGUSER` | ユーザー名 |
| `PGPASSWORD` | パスワード |
| `PGDATABASE` | データベース名 |

### バックエンドからの参照方法

バックエンドの環境変数で参照:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### 重要: postgres:// → postgresql:// の変換

RailwayのPostgreSQLは `postgres://` で始まるURLを提供しますが、SQLAlchemyは `postgresql://` が必要です。

```python
# backend/app/core/database.py
DATABASE_URL = os.getenv("DATABASE_URL")

# 変換処理（必須）
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
```

---

## バックエンド設定（FastAPI）

### Dockerfile（推奨）

```dockerfile
FROM python:3.11-slim

# 環境変数
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# システム依存関係（日本語フォント含む）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        fonts-ipafont-gothic \
        fonts-ipafont-mincho \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーション
COPY . .

# 非rootユーザー（セキュリティ）
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# ヘルスチェック（502エラー対策で重要）
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 起動コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### ヘルスチェックエンドポイント（必須）

```python
# backend/app/main.py
@app.get("/health")
async def health_check():
    """ヘルスチェック - Railwayが定期的に確認"""
    return {"status": "healthy"}
```

### Railway設定

バックエンドサービスの Settings タブ:

| 設定項目 | 値 |
|----------|-----|
| Root Directory | `/backend` （モノレポの場合） |
| Build Command | （Dockerfileがあれば不要） |
| Start Command | （Dockerfileがあれば不要） |

---

## フロントエンド設定（Next.js）

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // standalone出力（Railway推奨）
  output: 'standalone',

  // 環境変数
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // APIプロキシ（オプション）
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### 重要: output: 'standalone'

この設定により、Next.jsは最小限のファイルだけを出力し、Railwayでの起動が高速化されます。

### Railway設定

フロントエンドサービスの Settings タブ:

| 設定項目 | 値 |
|----------|-----|
| Root Directory | `/frontend` （モノレポの場合） |
| Build Command | `npm run build` |
| Start Command | `npm start` |

---

## 環境変数一覧

### バックエンド（Backend）

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `DATABASE_URL` | ✅ | PostgreSQL接続URL | `${{Postgres.DATABASE_URL}}` |
| `SECRET_KEY` | ✅ | JWT署名用の秘密鍵 | ランダムな文字列（32文字以上） |
| `ALLOWED_ORIGINS` | ✅ | CORS許可オリジン | `https://myapp-production.up.railway.app` |
| `FRONTEND_URL` | ✅ | フロントエンドURL | `https://myapp-production.up.railway.app` |
| `PORT` | - | ポート番号 | `8000` |
| `CLOUDINARY_CLOUD_NAME` | - | Cloudinary設定 | `xxxxx` |
| `CLOUDINARY_API_KEY` | - | Cloudinary設定 | `123456789` |
| `CLOUDINARY_API_SECRET` | - | Cloudinary設定 | `xxxxx` |

### フロントエンド（Frontend）

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `NEXT_PUBLIC_API_URL` | ✅ | バックエンドのURL | `https://myapp-backend-production.up.railway.app` |

---

## 502エラー対策

### 502エラーの主な原因と対策

#### 1. 起動時間が長すぎる

**原因:** アプリケーションの起動に時間がかかり、Railwayがタイムアウト

**対策:**
- Dockerfileに `HEALTHCHECK` の `--start-period` を設定（30秒以上）
- 起動時の重い処理を遅延実行

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

#### 2. ヘルスチェックの失敗

**原因:** `/health` エンドポイントがない、または応答しない

**対策:**
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### 3. ポートの不一致

**原因:** アプリが待機するポートとRailwayの期待するポートが異なる

**対策:**
- バックエンド: `--port 8000` を明示
- フロントエンド: Next.jsはデフォルトで3000番

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4. メモリ不足

**原因:** 無料プランのメモリ制限（512MB）を超過

**対策:**
- 重い依存関係を削減
- Hobbyプラン以上にアップグレード
- 起動時の初期化処理を軽量化

#### 5. データベース接続エラー

**原因:** DB接続に失敗してアプリがクラッシュ

**対策:**
- 接続リトライ処理を追加
- 接続プールの設定を調整

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # 接続の有効性を事前確認
)
```

---

## CORS設定

### バックエンドでの設定

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

# 環境変数から取得
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ワイルドカード(*)は避ける
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 重要: ワイルドカードを避ける

```python
# ❌ NG: セキュリティリスク
allow_origins=["*"]

# ✅ OK: 明示的に指定
allow_origins=["https://myapp-production.up.railway.app"]
```

### CORS設定のデバッグ

起動時にログ出力:
```python
@app.on_event("startup")
async def startup_event():
    print(f"[CORS] ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
```

---

## トラブルシューティング

### デプロイが失敗する

1. **Logs タブを確認** - エラーメッセージを特定
2. **Build Logs を確認** - 依存関係のインストールエラー
3. **環境変数を確認** - 必須変数が設定されているか

### 502 Bad Gateway

1. ヘルスチェックエンドポイントの確認
2. ポート設定の確認
3. 起動ログでエラーを確認
4. メモリ使用量を確認（Metrics タブ）

### CORS エラー

1. `ALLOWED_ORIGINS` にフロントエンドURLが含まれているか確認
2. プロトコル（http/https）が一致しているか確認
3. 末尾のスラッシュを含めない（`https://example.com` ✅ / `https://example.com/` ❌）

### データベース接続エラー

1. `DATABASE_URL` が正しく設定されているか確認
2. `postgres://` → `postgresql://` の変換処理があるか確認
3. PostgreSQLサービスが「Online」状態か確認

---

## チェックリスト

デプロイ前に確認:

### バックエンド
- [ ] Dockerfile に HEALTHCHECK がある
- [ ] `/health` エンドポイントがある
- [ ] `postgres://` → `postgresql://` 変換がある
- [ ] CORS設定で明示的にオリジンを指定している
- [ ] 環境変数 `SECRET_KEY` を設定した
- [ ] 環境変数 `DATABASE_URL` を設定した
- [ ] 環境変数 `ALLOWED_ORIGINS` を設定した

### フロントエンド
- [ ] `next.config.js` に `output: 'standalone'` がある
- [ ] 環境変数 `NEXT_PUBLIC_API_URL` を設定した

### Railway
- [ ] PostgreSQLサービスが追加されている
- [ ] 各サービスの Root Directory が正しい
- [ ] 環境変数がすべて設定されている

---

## 参考リンク

- [Railway Docs](https://docs.railway.app/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Standalone Output](https://nextjs.org/docs/pages/api-reference/next-config-js/output)
