import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://emailbotuser:Xa5EekvEr1cMEGUq@cluster0.wdvicn9.mongodb.net/emailbot?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "emailbot")
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # AWS Configuration (Legacy - can be removed after Gmail OAuth setup)
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_SES_SOURCE_EMAIL: str = os.getenv("AWS_SES_SOURCE_EMAIL", "patelkathan244@gmail.com")
    DEFAULT_SENDER_EMAIL: str = os.getenv("DEFAULT_SENDER_EMAIL", "sale.rrimp@gmail.com")
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "https://www.mailsflow.net/auth/callback")
    
    # Email Configuration (Legacy SMTP - can be removed after Gmail OAuth setup)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "sale.rrimp@gmail.com")
    SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "")
    
    # CORS Configuration - handle both string and list formats
    CORS_ORIGINS: List[str] = []
    
    # Stripe Configuration
    # Replace these with your actual Stripe keys from https://dashboard.stripe.com/apikeys
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_stripe_secret_key_here")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_your_stripe_publishable_key_here")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_your_webhook_secret_here")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Handle CORS_ORIGINS from environment variable
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001,https://www.mailsflow.net,https://mailsflow.net")
        if isinstance(cors_origins, str):
            self.CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]
        else:
            self.CORS_ORIGINS = cors_origins
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
