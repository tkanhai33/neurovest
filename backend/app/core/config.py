import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Neurovest Core Engine"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Financial data calculation strict metrics
    CRYPTO_DECIMAL_PLACES: int = 8
    FIAT_DECIMAL_PLACES: int = 2
    
    class Config:
        case_sensitive = True

settings = Settings()
