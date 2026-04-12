# Railway Next.js + FastAPI + PostgreSQL テンプレート

Railway上でNext.js（フロントエンド）+ FastAPI（バックエンド）+ PostgreSQL（DB）の構成を素早く構築するためのテンプレートです。

## 特徴

- 502エラーを防ぐための設定済み
- CORS設定のベストプラクティス
- PostgreSQL接続の自動変換（postgres:// → postgresql://）
- ヘルスチェック設定済み
- 日本語フォント対応（PDF生成用）

## ファイル構成

```text
.
├── README.md                    # このファイル
├── docs/
│   ├── RAILWAY_SETUP_GUIDE.md   # Railway環境構築ガイド
│   ├── GEMINI_API_SETUP.md      # Gemini API セットアップ
│   ├── APPSTORE_REVIEW_GUIDE.md # App Store審査ノウハウ
│   ├── IAP_IMPLEMENTATION_GUIDE.md # IAP(課金)実装ガイド
│   └── EAS_BUILD_GUIDE.md       # EAS Build & Submitガイド
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

## ドキュメント一覧

| ドキュメント | 内容 |
|-------------|------|
| [Railway環境構築ガイド](docs/RAILWAY_SETUP_GUIDE.md) | Railway上でのプロジェクト作成、PostgreSQL設定、502エラー対策、CORS設定 |
| [Gemini API セットアップ](docs/GEMINI_API_SETUP.md) | Google Gemini APIの設定、SDK、トラブルシューティング |
| [App Store審査ノウハウ](docs/APPSTORE_REVIEW_GUIDE.md) | 審査リジェクト実体験、メタデータ注意点、サブスク必須要件、提出前チェックリスト |
| [IAP実装ガイド](docs/IAP_IMPLEMENTATION_GUIDE.md) | react-native-iap v14+、レシート検証、Sandbox テスト、エラーハンドリング |
| [EAS Build & Submitガイド](docs/EAS_BUILD_GUIDE.md) | EASビルド、ビルド番号管理、署名設定、デバッグコード除去 |

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

## Railway デプロイの注意点

- `railway redeploy` は**前回の成功デプロイを再実行**する（最新コミットではない）
- GitHub自動デプロイが動かない場合は新しいコミットをpushして強制トリガー
- DB migrationはビルド時ではなく `start.sh` で実行（Dockerビルド時はDB接続不可）

## ライセンス

MIT
