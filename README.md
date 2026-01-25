# Railway Next.js + FastAPI + PostgreSQL テンプレート

Railway上でNext.js（フロントエンド）+ FastAPI（バックエンド）+ PostgreSQL（DB）の構成を素早く構築するためのテンプレートです。

## 特徴

- 502エラーを防ぐための設定済み
- CORS設定のベストプラクティス
- PostgreSQL接続の自動変換（postgres:// → postgresql://）
- ヘルスチェック設定済み
- 日本語フォント対応（PDF生成用）

## ファイル構成

```
.
├── README.md                    # このファイル
├── docs/
│   └── RAILWAY_SETUP_GUIDE.md   # 詳細な環境構築ガイド
├── backend/
│   ├── Dockerfile               # バックエンド用Dockerfile
│   ├── requirements.txt         # Python依存関係（例）
│   ├── .env.example             # 環境変数サンプル
│   └── app/
│       ├── main.py              # FastAPIアプリ（例）
│       └── core/
│           └── database.py      # DB接続（例）
└── frontend/
    ├── next.config.js           # Next.js設定
    └── .env.example             # 環境変数サンプル
```

## クイックスタート

### 1. このテンプレートをコピー

```bash
# 新しいプロジェクトにコピー
cp -r railway-nextjs-fastapi-template/* your-new-project/
```

### 2. Railwayでプロジェクト作成

1. [Railway](https://railway.app) にログイン
2. 「New Project」→「Empty Project」
3. PostgreSQLを追加: 「Add」→「Database」→「PostgreSQL」
4. バックエンドを追加: 「Add」→「GitHub Repo」
5. フロントエンドを追加: 「Add」→「GitHub Repo」

### 3. 環境変数を設定

詳細は [docs/RAILWAY_SETUP_GUIDE.md](docs/RAILWAY_SETUP_GUIDE.md) を参照

## 502エラー対策チェックリスト

- [ ] Dockerfileに `HEALTHCHECK` がある
- [ ] `/health` エンドポイントがある
- [ ] `postgres://` → `postgresql://` 変換処理がある
- [ ] `output: 'standalone'` が設定されている（Next.js）
- [ ] 環境変数がすべて設定されている

## ライセンス

MIT
