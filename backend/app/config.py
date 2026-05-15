"""Application configuration management."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

# 设置 Hugging Face 模型本地目录
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
os.environ['HF_HOME'] = str(MODELS_DIR)
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "RAG Knowledge Base"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database (SQLite for local dev, PostgreSQL for production)
    DATABASE_URL: str = "sqlite+aiosqlite:///" + str(Path(__file__).parent.parent / "data" / "ragapp.db")
    DATABASE_ECHO: bool = False

    # Redis (optional, not required for local dev)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Milvus (Milvus Lite file mode for local dev, server mode for production)
    MILVUS_URI: str = str(Path(__file__).parent.parent / "data" / "milvus.db")
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_DB: str = "default"

    # File Upload
    UPLOAD_DIR: str = str(Path(__file__).parent.parent / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "csv", "txt", "md", "docx", "doc"]

    # Embedding Model
    DEFAULT_EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DEVICE: str = "cpu"  # cpu / cuda
    EMBEDDING_BATCH_SIZE: int = 32
    
    # Local Model Path (optional - place models here to use offline)
    LOCAL_MODEL_DIR: str = str(Path(__file__).parent.parent / "models")

    # Reranker Model
    DEFAULT_RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"

    # Retrieval
    RETRIEVAL_TOP_K: int = 20  # Hybrid search candidates
    RERANK_TOP_N: int = 5      # After reranking
    CONFIDENCE_THRESHOLD: float = 0.3

    # Chunking
    DEFAULT_CHUNK_SIZE: int = 512
    DEFAULT_CHUNK_OVERLAP: int = 64
    PARENT_CHUNK_SIZE: int = 1536

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Security
    SECRET_KEY: str = "change-this-to-a-secure-random-string"
    API_KEY_ENCRYPTION_KEY: Optional[str] = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


settings = Settings()
