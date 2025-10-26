import os
from pathlib import Path 
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from functools import lru_cache

# --- Define the Settings Class --- 
class Settings(BaseSettings):
    """
        Settings class for the application.
    """
    # ---- LLM Providers ---
    groq_api_key: str = Field(
        ...,
        description="Groq API key for Kimi , Qwen and OpenAI OSS Models"
    )
    gemini_api_key: str = Field(
        ...,
        description="Google Gemini API key for aggregator model"
    )
    # ---- Tools & Services --- 
    firecrawl_api_key: str = Field(
        ...,
        description="Firecrawl API key for Web Scraping Jobs"
    )
    landing_ai_api_key: str | None = None
    # ---- Observability --- 
    langsmith_api_key: Optional[str] = Field(
        None,
        description="LangSmith API key for tracing and debugging"
    )
    
    langsmith_project: str = Field(
        "cold-email-generator",
        description="LangSmith project name"
    )
    
    langsmith_endpoint: str = Field(
        "https://api.smith.langchain.com",
        description="LangSmith API endpoint"
    )
    
    langsmith_tracing: bool = Field(
        False,
        description="Enable/disable LangSmith tracing"
    )
    # --- APP Config --- 
    environments: str = Field(
        "development",
        description="Application environment (development/production)"
    )
    debug: bool = Field(
        False,
        description="Enable/disable debug mode"
    )
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed origins for CORS"
    )
    # --- File Upload --- 
    max_upload_size_mb: int = Field(
        5,
        description="Maximum file upload in MB",
        ge=1,
        le=10
    )
    # --- API Timeout ---
    llm_timeout: int = Field(
        30,
        description="Timeout for LLM API Calls in seconds",
        ge=10,
        le=120 
    )
    # --- FireCrawl Timeout ---
    firecrawl_timeout: int = Field(
        60,
        description="Timeout for FireCrawl API Calls in seconds",
        ge=30,
        le=120
    )
    # --- Landing AI Timeout ---
    landing_ai_timeout: int = Field(
        60,
        description="Timeout for Landing AI API Calls in seconds",
        ge=30,
        le=120
    )
    
    # --- Configuration --- 
    model_config = ConfigDict(
        env_file=Path(__file__).parents[2] / ".env", 
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# --- Singleton Pattern ---
@lru_cache()
def get_settings() -> Settings:
    """
        Get cached settings instance.
        Lazy loading to avoid import-time instantiation errors.
    """
    return Settings()
