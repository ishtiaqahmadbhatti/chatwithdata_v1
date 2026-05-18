from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    app_name: str = "SmartConverter FastAPI"
    app_version: str = "1.0.0"
    debug: bool = False
    database_active: bool = True
    dynamodb_active: bool = False
    
    # AWS Region for DynamoDB
    aws_region: str = os.environ.get("AWS_REGION", "us-east-1")
    dynamodb_table_prefix: str = os.environ.get("DYNAMODB_TABLE_PREFIX", "SmartConverter")
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    
    # Directories — Lambda sets UPLOADS_DIR/OUTPUTS_DIR to /tmp/* via Dockerfile ENV
    upload_dir: str = os.environ.get("UPLOADS_DIR", "uploads")
    output_dir: str = os.environ.get("OUTPUTS_DIR", "outputs")
    
    # Stripe Settings (Load from environment variables)
    stripe_api_key: str = ""  # Set in .env file
    stripe_webhook_secret: str = ""  # Set in .env file
    stripe_price_monthly: str = ""  # Monthly Plan Price ID
    stripe_price_yearly: str = ""  # Yearly Plan Price ID
    
    # max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_file_size: int = 0  # 0 means unlimited
    
    # Retention period for files (in minutes) - files older than this will be deleted
    file_retention_minutes: int = 60  # Default 1 hour
    # file_retention_minutes: int = 120  # Reduced to 1 minute for testing
    
    # S3 Settings — for large file uploads (bypasses API Gateway 10MB limit)
    s3_bucket: str = os.environ.get("S3_BUCKET", "")
    s3_region: str = os.environ.get("S3_REGION", "us-east-1")
    s3_presigned_expiry: int = 3600  # seconds — presigned URL validity

    # OCR Settings
    tesseract_path: Optional[str] = None
    
    # Database Settings (Load from environment variables)
    database_url: Optional[str] = None
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "SmartConverterDB"
    db_user: str = "postgres"
    db_password: str = ""  # Set in .env file
    
    # JWT Settings
    secret_key: str = "your-secret-key-change-this-in-production"  # Change in .env
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Redis Settings (optional)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # OAuth Providers
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    facebook_client_id: Optional[str] = None
    facebook_client_secret: Optional[str] = None
    
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
    
    @property
    def get_database_url(self) -> str:
        """Get the database URL, either from environment or constructed from settings."""
        if self.database_url:
            return self.database_url
        # URL encode the password to handle special characters
        from urllib.parse import quote_plus
        encoded_password = quote_plus(self.db_password)
        return f"postgresql://{self.db_user}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Email Settings (Load from environment variables)
    MAIL_USERNAME: str = ""  # Set in .env file
    MAIL_PASSWORD: str = ""  # Set in .env file
    MAIL_FROM: str = ""  # Set in .env file
    MAIL_FROM_NAME: str = "SmartConverter Helpdesk"
    HELPDESK_EMAIL: str = "techmindsforge@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist (safe on Lambda — /tmp/ is writable, /var/task/ is read-only)
try:
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
except OSError:
    pass  # Lambda: dirs may be read-only; actual /tmp/* dirs created in Dockerfile
