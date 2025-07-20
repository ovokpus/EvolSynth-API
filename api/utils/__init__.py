"""
EvolSynth API Utilities
Comprehensive utilities and helper functions for the API
"""

# Core utility imports
from .error_handling import (
    # Exception classes
    EvolSynthException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ExternalServiceError,
    TimeoutError,
    ConfigurationError,
    BusinessLogicError,
    ErrorCategory,
    
    # Utility functions
    create_error_response,
    handle_evolsynth_exception,
    handle_generic_exception,
    create_http_exception,
    global_exception_handler,
    validate_and_raise,
    safe_execute,
    ErrorCollector
)

from .validation import (
    validate_generation_request,
    validate_evaluation_request,
    ValidationUtilities,
    FileValidator,
    DataValidator,
    APIKeyValidator
)

from .cache_manager import (
    CacheManager,
    DocumentCache,
    ResultCache,
    SessionCache,
    cache_manager,
    document_cache,
    result_cache,
    session_cache
)

from .security import (
    RateLimiter,
    InputSanitizer,
    SecurityHeaders,
    rate_limiter,
    get_client_ip,
    rate_limit_dependency,
    create_rate_limit_dependency,
    RateLimit,
    StrictRateLimit,
    APIKeyRateLimit,
    configure_cors,
    hash_sensitive_data,
    mask_sensitive_data,
    SimpleAuthBearer,
    auth_bearer,
    require_auth
)

from .health_checks import (
    HealthStatus,
    DependencyType,
    HealthCheck,
    HealthCheckManager,
    health_manager,
    check_redis_connection,
    check_openai_api,
    check_system_resources,
    check_api_endpoints,
    initialize_health_checks,
    get_health_status,
    get_health_summary,
    get_readiness_status,
    get_liveness_status
)

from .logging_config import (
    StructuredFormatter,
    RequestContextFilter,
    setup_logging,
    configure_loggers,
    get_logger,
    log_function_call,
    log_performance_metric,
    log_security_event,
    initialize_api_logging
)

# Export all utilities for easy access
__all__ = [
    # Error handling
    "EvolSynthException",
    "ValidationError",
    "AuthenticationError", 
    "AuthorizationError",
    "NotFoundError",
    "RateLimitError",
    "ExternalServiceError",
    "TimeoutError",
    "ConfigurationError",
    "BusinessLogicError",
    "ErrorCategory",
    "create_error_response",
    "handle_evolsynth_exception",
    "handle_generic_exception",
    "create_http_exception",
    "global_exception_handler",
    "validate_and_raise",
    "safe_execute",
    "ErrorCollector",
    
    # Validation
    "validate_generation_request",
    "validate_evaluation_request",
    "ValidationUtilities",
    "FileValidator",
    "DataValidator", 
    "APIKeyValidator",
    
    # Caching
    "CacheManager",
    "DocumentCache",
    "ResultCache",
    "SessionCache",
    "cache_manager",
    "document_cache",
    "result_cache",
    "session_cache",
    
    # Security
    "RateLimiter",
    "InputSanitizer",
    "SecurityHeaders",
    "rate_limiter",
    "get_client_ip",
    "rate_limit_dependency",
    "create_rate_limit_dependency",
    "RateLimit",
    "StrictRateLimit", 
    "APIKeyRateLimit",
    "configure_cors",
    "hash_sensitive_data",
    "mask_sensitive_data",
    "SimpleAuthBearer",
    "auth_bearer",
    "require_auth",
    
    # Health checks
    "HealthStatus",
    "DependencyType",
    "HealthCheck",
    "HealthCheckManager",
    "health_manager",
    "check_redis_connection",
    "check_openai_api",
    "check_system_resources",
    "check_api_endpoints",
    "initialize_health_checks",
    "get_health_status",
    "get_health_summary",
    "get_readiness_status",
    "get_liveness_status",
    
    # Logging
    "StructuredFormatter",
    "RequestContextFilter",
    "setup_logging",
    "configure_loggers",
    "get_logger",
    "log_function_call",
    "log_performance_metric",
    "log_security_event",
    "initialize_api_logging"
] 