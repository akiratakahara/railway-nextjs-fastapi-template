# Gemini API セットアップガイド

Google Gemini APIを使用してPDF/画像からテキスト抽出を行うための設定手順です。

## 1. APIキーの取得

**重要: Google AI Studio から取得すること**

| 取得元 | 無料枠 | 結果 |
|--------|--------|------|
| Google AI Studio | あり（1日1500リクエスト） | 動作する |
| Google Cloud Console | なし（課金設定必要） | `limit: 0` エラー |

### 手順

1. https://aistudio.google.com/apikey にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. APIキーをコピー

## 2. 利用可能なモデルの確認

APIキー取得後、以下のコマンドで利用可能なモデルを確認できます：

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```

### 推奨モデル（2025年1月時点）

| モデル名 | 説明 | 無料枠 |
|----------|------|--------|
| `gemini-2.5-flash` | 高速・マルチモーダル対応 | あり |
| `gemini-2.5-pro` | 高性能版 | あり |

**注意:** `gemini-2.0-flash`, `gemini-1.5-flash` などの旧モデルは `limit: 0` エラーになる場合があります。

## 3. Python SDK

### インストール

```bash
pip install google-genai pdf2image Pillow
```

**重要:** `google-generativeai` ではなく `google-genai` を使用すること

### requirements.txt

```
google-genai>=1.0.0
pdf2image>=1.17.0
Pillow>=10.2.0
```

## 4. 環境変数

```bash
# 推奨（google-genai SDKのデフォルト）
GEMINI_API_KEY=your_api_key_here

# または（互換性のため）
GOOGLE_API_KEY=your_api_key_here
```

## 5. Dockerでの設定（PDF変換用）

`pdf2image` を使用する場合、`poppler-utils` が必要です：

```dockerfile
FROM python:3.11-slim

# PDF変換用の依存関係
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
```

## 6. 実装例

```python
import os
import base64
from google import genai

# クライアント作成
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
)

# 画像を送信してテキスト抽出
response = client.models.generate_content(
    model="gemini-2.5-flash",  # 必ず利用可能なモデルを指定
    contents=[
        {
            "inline_data": {
                "mime_type": "image/png",
                "data": base64.standard_b64encode(image_bytes).decode("utf-8")
            }
        },
        {"text": "この画像から情報を抽出してください"}
    ]
)

print(response.text)
```

## 7. Railway環境変数設定

1. Railwayダッシュボードを開く
2. バックエンドサービスを選択
3. Variables タブを開く
4. `GEMINI_API_KEY` を追加

## トラブルシューティング

### エラー: 429 RESOURCE_EXHAUSTED (limit: 0)

**原因と解決策:**

| 原因 | 解決策 |
|------|--------|
| Google Cloud ConsoleからAPIキーを取得した | Google AI Studioから再取得 |
| 古いモデル名を使用している | `gemini-2.5-flash` を使用 |
| APIが有効化されていない | ListModels APIで確認 |

### エラー: poppler not installed

**解決策:** Dockerfileに `poppler-utils` を追加

```dockerfile
RUN apt-get update && apt-get install -y poppler-utils
```

### エラー: ModuleNotFoundError: google.genai

**解決策:** 正しいパッケージをインストール

```bash
# 間違い
pip install google-generativeai

# 正しい
pip install google-genai
```

## まとめ

1. **APIキー**: Google AI Studio から取得
2. **SDK**: `google-genai` を使用
3. **モデル**: `gemini-2.5-flash` を使用
4. **環境変数**: `GEMINI_API_KEY`
5. **Docker**: `poppler-utils` を追加（PDF変換時）
