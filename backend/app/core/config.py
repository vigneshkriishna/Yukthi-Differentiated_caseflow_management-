"""
Application configuration settings
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "DCM System with BNS Assist"
    APP_VERSION: str = "1.0.0"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    PORT: int = 8001

    # MongoDB Database
    MONGODB_URL: str = ""
    MONGODB_DATABASE: str = "dcm_system"
    MONGODB_USERNAME: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_CLUSTER: str = ""
    DATABASE_URL: str = "sqlite:///./dcm_system.db"
    DATABASE_ECHO: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BCRYPT_ROUNDS: int = 12

    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # Demo Data
    CREATE_DEMO_DATA: bool = True
    DEMO_USERS_COUNT: int = 4
    DEMO_CASES_COUNT: int = 10

    # Email Settings
    EMAIL_ENABLED: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # NLP Models (Phase 1)
    NLP_MODEL_PATH: str = "./models"
    BNS_MAPPING_FILE: str = "./data/bns_mapping.json"

    # Scheduler
    DAILY_HEARING_SLOTS: int = 50
    SLACK_PERCENTAGE: float = 0.15  # 15% slack

    # Reports
    REPORTS_DIR: str = "./reports"

    # =============================================================================
    # API INTEGRATIONS
    # =============================================================================

    # Email Service
    SENDGRID_API_KEY: str = ""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = "DCM System"
    FROM_EMAIL: str = ""

    # SMS Service
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # AWS Services
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-west-2"
    S3_BUCKET_NAME: str = ""

    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_BUCKET: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # Enhanced ML APIs
    OPENAI_API_KEY: str = ""
    GOOGLE_CLOUD_AI_KEY: str = ""
    AZURE_COGNITIVE_KEY: str = ""
    AZURE_COGNITIVE_ENDPOINT: str = ""

    # Payment Gateway
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # Monitoring
    DATADOG_API_KEY: str = ""
    GOOGLE_ANALYTICS_ID: str = ""

    # SSL/TLS
    SSL_CERT_PATH: str = ""
    SSL_KEY_PATH: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
