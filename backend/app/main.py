"""
FastAPI アプリケーション テンプレート
Railway環境での502エラー対策済み
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="My API",
    description="Railway deployment template",
    version="1.0.0",
)

# CORS設定
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "API is running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    Railwayが定期的に確認するため必須
    """
    return {"status": "healthy"}


# 起動時の処理
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    print(f"[CORS] ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
    print("[App] Application started")
