"""
Application configuration settings
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "DCM System with BNS Assist"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./dcm_system.db"
    DATABASE_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # NLP Models (Phase 1)
    NLP_MODEL_PATH: str = "./models"
    BNS_MAPPING_FILE: str = "./data/bns_mapping.json"
    
    # Scheduler
    DAILY_HEARING_SLOTS: int = 50
    SLACK_PERCENTAGE: float = 0.15  # 15% slack
    
    # Reports
    REPORTS_DIR: str = "./reports"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
