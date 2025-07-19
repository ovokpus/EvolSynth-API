"""
Core Configuration for EvolSynth API
Main settings and environment variables for the synthetic data generation API
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    app_name: str = "EvolSynth API"
    app_description: str = "Advanced Synthetic Data Generation using LangGraph-based Evol-Instruct methodology"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    
    # API Keys (required)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    langchain_api_key: Optional[str] = Field(default=None, alias="LANGCHAIN_API_KEY")
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(default=True, alias="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field(default="EvolSynth-API", alias="LANGCHAIN_PROJECT")
    
    # LLM Configuration
    default_model: str = Field(default="gpt-4o-mini", alias="DEFAULT_MODEL")
    evaluation_model: str = Field(default="gpt-4o-mini", alias="EVALUATION_MODEL")
    temperature: float = Field(default=0.7, alias="TEMPERATURE")
    max_tokens: int = Field(default=500, alias="MAX_TOKENS")
    
    # Evolution Configuration (optimized for speed)
    max_base_questions_per_doc: int = Field(default=2, alias="MAX_BASE_QUESTIONS_PER_DOC")
    simple_evolution_count: int = Field(default=2, alias="SIMPLE_EVOLUTION_COUNT")
    multi_context_evolution_count: int = Field(default=1, alias="MULTI_CONTEXT_EVOLUTION_COUNT")
    reasoning_evolution_count: int = Field(default=1, alias="REASONING_EVOLUTION_COUNT")
    complex_evolution_count: int = Field(default=1, alias="COMPLEX_EVOLUTION_COUNT")
    
    # Document Processing
    max_document_size_mb: int = Field(default=10, alias="MAX_DOCUMENT_SIZE_MB")
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")
    max_content_length: int = Field(default=2000, alias="MAX_CONTENT_LENGTH")
    context_max_length: int = Field(default=1500, alias="CONTEXT_MAX_LENGTH")
    
    # Performance Configuration
    max_concurrency: int = Field(default=8, alias="MAX_CONCURRENCY")
    request_timeout: int = Field(default=300, alias="REQUEST_TIMEOUT")
    max_documents_per_request: int = Field(default=10, alias="MAX_DOCUMENTS_PER_REQUEST")
    llm_request_timeout: int = Field(default=30, alias="LLM_REQUEST_TIMEOUT")
    batch_size: int = Field(default=8, alias="BATCH_SIZE")
    
    # Execution Modes
    default_execution_mode: str = Field(default="concurrent", alias="DEFAULT_EXECUTION_MODE")
    
    # Redis Configuration (for compatibility)
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    @validator('redis_port', pre=True)
    def parse_redis_port(cls, v):
        """Parse Redis port, handling Railway variable resolution issues"""
        if isinstance(v, str):
            # Handle Railway unresolved variables
            if v.startswith('${') and v.endswith('}'):
                print(f"⚠️  Redis port variable not resolved: {v}, using default 6379")
                return 6379
            try:
                return int(v)
            except ValueError:
                print(f"⚠️  Invalid Redis port: {v}, using default 6379")
                return 6379
        return v
    
    # Security Configuration (for compatibility)
    allowed_origins: str = Field(default="*", alias="ALLOWED_ORIGINS")
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, alias="RATE_LIMIT_WINDOW")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()


def validate_api_keys():
    """Validate that required API keys are present"""
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    if not settings.langchain_api_key:
        print("⚠️  LANGCHAIN_API_KEY not set - LangSmith tracing will be disabled")


def setup_environment():
    """Setup environment variables for LangChain and OpenAI"""
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    
    if settings.langchain_api_key:
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project 