# File: backend/utils/config.py

"""
Configuration Management Module
Loads and validates environment variables
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "SynergyScope"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_PREFIX: str = "/api/v1"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    # AWS Services
    S3_BUCKET: str = "synergyscope-data"
    NEPTUNE_ENDPOINT: str = "localhost"
    NEPTUNE_PORT: int = 8182
    SAGEMAKER_ENDPOINT: str = "synergyscope-endpoint"
    BEDROCK_MODEL_ID: str = "anthropic.claude-v2"
    QUICKSIGHT_ACCOUNT_ID: str = ""
    
    # Riot API
    RIOT_API_KEY: str = ""
    RIOT_API_REGION: str = "na1"
    RIOT_API_BASE_URL: str = "https://americas.api.riotgames.com"
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()