"""
Configuration module for KANZ System
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    groq_api_key: str
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    database_url: str
    
    # Application
    app_name: str = "KANZ"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # RAG Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    # LLM Settings
    llm_model: str = "mixtral-8x7b-32768"
    llm_temperature: float = 0.1
    max_tokens: int = 4096
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
