"""Configuration management for the sales proposal system."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # LLM Settings
    default_llm_provider: str = "anthropic"  # openai or anthropic
    default_model: str = "claude-3-5-haiku-20241022"
    temperature: float = 0.7
    max_tokens: int = 2000

    # Vector Store Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_store_path: str = "./data/vector_store"
    top_k_results: int = 5

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/proposals.db"

    # Document Storage
    upload_dir: str = "./data/uploads"
    output_dir: str = "./data/outputs"

    # Confidence Thresholds
    high_confidence_threshold: float = 0.9
    medium_confidence_threshold: float = 0.7

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
