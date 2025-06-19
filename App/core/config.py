from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Settings
    GROQ_API_KEY: str
    GROQ_API_URL: str = "https://api.groq.com/v1/chat/completions"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    # App Settings
    APP_NAME: str = "Medical Triage Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()