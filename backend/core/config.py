from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_ENV: str = "local"
    DATABASE_URL: str = "sqlite:///./zerotrust.db"
    CORS_ORIGINS: str = "http://127.0.0.1:8000,http://localhost:8000,null"
    API_PREFIX: str = "/api/v1"
    ADMIN_API_KEY: str = "change-me-before-production"
    TRUST_TICK_SECONDS: int = 10
    
    JWT_SECRET_KEY: str = "replace-with-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-me-before-production"
    
    WEBHOOK_SECRET: str = "change-me-before-production"

    @property
    def cors_origins_list(self) -> List[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        if self.APP_ENV == "production" and "*" in origins:
            raise ValueError("Wildcard CORS '*' is not allowed in production APP_ENV.")
        return origins

    class Config:
        env_file = ".env"

settings = Settings()
