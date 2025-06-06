from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your-secret-key-here"  # In production, this should be set via environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: str = "http://localhost:8501"
    API_URL: str = "http://localhost:8000"  # Add this field
    
    @property
    def origins(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"  # Allow extra fields
    )

settings = Settings() 