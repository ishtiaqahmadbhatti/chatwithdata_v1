from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    app_name: str = "ChatWithData FastAPI"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    
    # Directories
    upload_dir: str = os.environ.get("UPLOADS_DIR", "uploads")
    output_dir: str = os.environ.get("OUTPUTS_DIR", "outputs")
    
    # File Limits and Retention
    max_file_size: int = 0  # 0 means unlimited
    file_retention_minutes: int = 60  # Default 1 hour
    
    # S3 Settings — for large file uploads/downloads caching
    s3_bucket: str = os.environ.get("S3_BUCKET", "")
    s3_region: str = os.environ.get("S3_REGION", "us-east-1")
    s3_presigned_expiry: int = 3600  # seconds
    
    # YouTube Data API v3 (for comment extraction)
    youtube_api_key: Optional[str] = None

    # Ollama / RAG Settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "gemma4:latest"
    ollama_embed_model: str = "qwen3-embedding:latest"
    faiss_persist_dir: str = "faiss_db"
    protocol_buffers_python_implementation: Optional[str] = None

    # LangSmith / LangChain Tracing
    langchain_tracing_v2: Optional[str] = None
    langchain_endpoint: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langchain_project: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()

# Ensure directories exist
try:
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
except OSError:
    pass
