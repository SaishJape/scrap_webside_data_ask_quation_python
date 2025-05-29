from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = "AIzaSyB2d52clfGjeXoqrEpBi1zAibjhQTU_NcM"
    
    # Database settings
    qdrant_url: str = "http://localhost:6333"
    qdrant_timeout: float = 10.0
    qdrant_prefer_grpc: bool = False
    
    # Model settings
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    gemini_model: str = "gemini-2.0-flash"
    vector_size: int = 384
    
    # Text processing settings
    chunk_size: int = 500
    search_limit: int = 3
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()