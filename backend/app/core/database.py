"""
データベース接続設定
Railway PostgreSQL対応
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# データベースURL取得
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# 重要: RailwayのPostgreSQLはpostgres://で始まるが、
# SQLAlchemyはpostgresql://が必要
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"[Database] Using: {DATABASE_URL[:30] if DATABASE_URL else 'None'}...")

# エンジン作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # 接続の有効性を事前確認（502エラー対策）
)

# セッション
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()


def get_db():
    """データベースセッションの依存性"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """データベーステーブル作成"""
    Base.metadata.create_all(bind=engine)
