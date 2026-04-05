import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./firstfintech_qa.db"

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # OpenAI / LLM
    OPENAI_API_KEY: str = ""
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_RETRY_COUNT: int = 3
    FALLBACK_ENABLED: bool = True
    RULE_ENGINE_VERSION: str = "v1.0"
    ENABLE_ADVANCED_RULES: bool = True
    TEST_DATA_GENERATION_ENABLED: bool = True
    OLLAMA_MODEL: str = "dolphin-llama3:latest"
    FRONTEND_URL: str = "http://localhost:5500"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
