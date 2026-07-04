from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Neurovest Core Engine"
    # Add other configuration settings here

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
