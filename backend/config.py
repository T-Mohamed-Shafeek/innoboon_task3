from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ecommerce_db"
    SECRET_KEY: str = "9f82bfcaf183c7a8fd66f9e476e0db3b6cc9d99325c6a30c61a4e8d65b3b1c75"  # In production, this should be set via environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: str = "http://localhost:8501"
    API_URL: str = "http://localhost:8000" 
    
    @property
    def origins(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow" 
    )

settings = Settings() 