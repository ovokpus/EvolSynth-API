"""
Environment-specific configuration for EvolSynth API
Manages settings for development, staging, and production environments
"""

import os
from typing import Dict, Any, Optional, List
from enum import Enum
from pathlib import Path

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class BaseConfig(BaseSettings):
    """Base configuration with common settings"""
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, alias="ENVIRONMENT")
    
    # API Configuration
    app_name: str = "EvolSynth API"
    app_description: str = "Advanced Synthetic Data Generation using LangGraph-based Evol-Instruct methodology"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=1, alias="WORKERS")
    
    # API Keys (required in all environments)
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
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_ssl: bool = Field(default=False, alias="REDIS_SSL")
    
    # Cache Configuration
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")
    document_cache_ttl: int = Field(default=7200, alias="DOCUMENT_CACHE_TTL")
    result_cache_ttl: int = Field(default=3600, alias="RESULT_CACHE_TTL")
    
    # Performance Configuration
    max_concurrency: int = Field(default=8, alias="MAX_CONCURRENCY")
    request_timeout: int = Field(default=300, alias="REQUEST_TIMEOUT")
    max_documents_per_request: int = Field(default=10, alias="MAX_DOCUMENTS_PER_REQUEST")
    llm_request_timeout: int = Field(default=30, alias="LLM_REQUEST_TIMEOUT")
    batch_size: int = Field(default=8, alias="BATCH_SIZE")
    
    # Evolution Configuration
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
    
    # Security Configuration
    allowed_origins: List[str] = Field(default=["*"], alias="ALLOWED_ORIGINS")
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, alias="RATE_LIMIT_WINDOW")
    
    # Monitoring Configuration
    health_check_enabled: bool = Field(default=True, alias="HEALTH_CHECK_ENABLED")
    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")
    performance_monitoring: bool = Field(default=True, alias="PERFORMANCE_MONITORING")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")  # "json" or "text"
    log_file: Optional[str] = Field(default=None, alias="LOG_FILE")
    
    @validator("environment", pre=True)
    def validate_environment(cls, v):
        """Validate environment value"""
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                return Environment.DEVELOPMENT
        return v
    
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse allowed origins from string or list"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    
    # Relaxed settings for development
    workers: int = 1
    log_level: str = "DEBUG"
    log_format: str = "text"
    
    # Lower limits for faster development
    max_concurrency: int = 4
    batch_size: int = 4
    request_timeout: int = 120
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 1800  # 30 minutes
    
    # Security - relaxed for development
    allowed_origins: List[str] = ["*"]
    rate_limit_enabled: bool = False
    
    # Development-specific LLM settings
    default_model: str = "gpt-4o-mini"  # Cheaper model for dev
    max_tokens: int = 300
    
    class Config:
        env_file = ".env.development"


class StagingConfig(BaseConfig):
    """Staging environment configuration"""
    
    environment: Environment = Environment.STAGING
    debug: bool = False
    
    # Production-like settings but with some flexibility
    workers: int = 2
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "logs/evolsynth_staging.log"
    
    # Moderate performance settings
    max_concurrency: int = 6
    batch_size: int = 6
    request_timeout: int = 180
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 2400  # 40 minutes
    
    # Security - more restrictive
    allowed_origins: List[str] = [
        "https://staging.yourdomain.com",
        "https://staging-api.yourdomain.com"
    ]
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 200
    rate_limit_window: int = 3600
    
    # Use production models but with lower limits
    default_model: str = "gpt-4o-mini"
    max_tokens: int = 400
    
    class Config:
        env_file = ".env.staging"


class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    
    # Production server settings
    workers: int = 4
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "logs/evolsynth_production.log"
    
    # High performance settings
    max_concurrency: int = 12
    batch_size: int = 10
    request_timeout: int = 300
    
    # Optimized cache settings
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    document_cache_ttl: int = 7200  # 2 hours
    result_cache_ttl: int = 3600  # 1 hour
    
    # Production security
    allowed_origins: List[str] = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://api.yourdomain.com"
    ]
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600
    
    # Production LLM settings
    default_model: str = "gpt-4o"
    evaluation_model: str = "gpt-4o-mini"
    max_tokens: int = 500
    
    # Enhanced monitoring
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    performance_monitoring: bool = True
    
    class Config:
        env_file = ".env.production"


class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    
    environment: Environment = Environment.TESTING
    debug: bool = True
    
    # Test-specific settings
    workers: int = 1
    log_level: str = "DEBUG"
    log_format: str = "text"
    
    # Fast settings for tests
    max_concurrency: int = 2
    batch_size: int = 2
    request_timeout: int = 30
    
    # Minimal cache for testing
    cache_enabled: bool = False
    
    # No rate limiting in tests
    rate_limit_enabled: bool = False
    
    # Test models (mock or minimal)
    default_model: str = "gpt-3.5-turbo"
    max_tokens: int = 100
    
    # Minimal evolution for faster tests
    max_base_questions_per_doc: int = 1
    simple_evolution_count: int = 1
    multi_context_evolution_count: int = 0
    reasoning_evolution_count: int = 0
    complex_evolution_count: int = 0
    
    class Config:
        env_file = ".env.testing"


# Configuration factory
def get_config(environment: Optional[str] = None) -> BaseConfig:
    """
    Get configuration based on environment
    
    Args:
        environment: Environment name (development, staging, production, testing)
        
    Returns:
        Configuration instance
    """
    env = environment or os.getenv("ENVIRONMENT", "development")
    env = env.lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "dev": DevelopmentConfig,
        "staging": StagingConfig,
        "stage": StagingConfig,
        "production": ProductionConfig,
        "prod": ProductionConfig,
        "testing": TestingConfig,
        "test": TestingConfig,
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()


def validate_config(config: BaseConfig) -> Dict[str, Any]:
    """
    Validate configuration and return validation results
    
    Args:
        config: Configuration instance to validate
        
    Returns:
        Dictionary with validation results
    """
    issues = []
    warnings = []
    
    # Validate required API keys
    if not config.openai_api_key:
        issues.append("OPENAI_API_KEY is required")
    
    if not config.langchain_api_key:
        warnings.append("LANGCHAIN_API_KEY is recommended for tracing")
    
    # Validate Redis configuration
    if config.cache_enabled:
        if not config.redis_host:
            issues.append("REDIS_HOST is required when cache is enabled")
        if config.redis_port < 1 or config.redis_port > 65535:
            issues.append("REDIS_PORT must be between 1 and 65535")
    
    # Validate performance settings
    if config.max_concurrency < 1:
        issues.append("MAX_CONCURRENCY must be at least 1")
    
    if config.batch_size < 1:
        issues.append("BATCH_SIZE must be at least 1")
    
    # Validate file paths
    if config.log_file:
        log_dir = Path(config.log_file).parent
        if not log_dir.exists():
            warnings.append(f"Log directory does not exist: {log_dir}")
    
    # Environment-specific validations
    if config.environment == Environment.PRODUCTION:
        if config.debug:
            warnings.append("Debug mode is enabled in production")
        
        if "*" in config.allowed_origins:
            issues.append("Wildcard CORS origins not allowed in production")
        
        if not config.rate_limit_enabled:
            warnings.append("Rate limiting is disabled in production")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "environment": config.environment.value,
        "config_summary": {
            "workers": config.workers,
            "max_concurrency": config.max_concurrency,
            "cache_enabled": config.cache_enabled,
            "rate_limit_enabled": config.rate_limit_enabled,
            "debug_mode": config.debug,
            "log_level": config.log_level
        }
    }


# Example environment files content
ENVIRONMENT_FILES = {
    ".env.development": """
# Development Environment Configuration
ENVIRONMENT=development

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Redis (local development)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Performance (development optimized)
MAX_CONCURRENCY=4
BATCH_SIZE=4
REQUEST_TIMEOUT=120

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# Security (relaxed for development)
ALLOWED_ORIGINS=*
RATE_LIMIT_ENABLED=false
""",
    
    ".env.staging": """
# Staging Environment Configuration
ENVIRONMENT=staging

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=2

# Redis
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Performance
MAX_CONCURRENCY=6
BATCH_SIZE=6
REQUEST_TIMEOUT=180

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/evolsynth_staging.log

# Security
ALLOWED_ORIGINS=https://staging.yourdomain.com,https://staging-api.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=200
""",
    
    ".env.production": """
# Production Environment Configuration
ENVIRONMENT=production

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Redis
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_SSL=true

# Performance
MAX_CONCURRENCY=12
BATCH_SIZE=10
REQUEST_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/evolsynth_production.log

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://api.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000

# LLM
DEFAULT_MODEL=gpt-4o
EVALUATION_MODEL=gpt-4o-mini
"""
}


def create_environment_files():
    """Create example environment files"""
    for filename, content in ENVIRONMENT_FILES.items():
        if not Path(filename).exists():
            with open(filename, 'w') as f:
                f.write(content.strip())
            print(f"Created {filename}")
        else:
            print(f"{filename} already exists, skipping")


if __name__ == "__main__":
    # Create example environment files
    create_environment_files()
    
    # Test configuration loading
    config = get_config()
    validation = validate_config(config)
    
    print(f"Loaded configuration for {config.environment.value}")
    print(f"Configuration valid: {validation['valid']}")
    
    if validation['issues']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}") 