from pydantic_settings import BaseSettings
from typing import Optional
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
    
    # Twilio Settings (Optional)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Enable/Disable Twilio
    ENABLE_TWILIO: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()