"""
EvolSynth API Configuration
Settings and environment variables for the synthetic data generation API
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    app_name: str = "EvolSynth API"
    app_description: str = "Advanced Synthetic Data Generation using LangGraph-based Evol-Instruct methodology"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Keys (required)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    langchain_api_key: Optional[str] = Field(default=None, alias="LANGCHAIN_API_KEY")
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(default=True, alias="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field(default="EvolSynth-API", alias="LANGCHAIN_PROJECT")
    
    # LLM Configuration
    default_model: str = "gpt-4.1-nano"
    evaluation_model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500
    
    # Evolution Configuration
    max_base_questions_per_doc: int = 3
    simple_evolution_count: int = 3
    multi_context_evolution_count: int = 2
    reasoning_evolution_count: int = 2
    
    # Document Processing
    max_document_size_mb: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 50
    max_content_length: int = 2000
    
    # Performance Configuration
    max_concurrency: int = 3
    request_timeout: int = 300  # 5 minutes
    max_documents_per_request: int = 10
    
    # Execution Modes
    default_execution_mode: str = "concurrent"  # "concurrent" or "sequential"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()


# Validation functions
def validate_api_keys():
    """Validate that required API keys are present"""
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    if not settings.langchain_api_key:
        raise ValueError("LANGCHAIN_API_KEY environment variable is required")


def setup_environment():
    """Setup environment variables for LangChain and OpenAI"""
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    
    if settings.langchain_api_key:
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project 