"""
Enhanced Error handling utilities for the EvolSynth API
Provides custom exceptions, error categorization, and comprehensive error responses
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from api.models.responses import ErrorResponse


class ErrorCategory(str, Enum):
    """Error categories for better error classification"""
    VALIDATION = "validation_error"
    AUTHENTICATION = "authentication_error"
    AUTHORIZATION = "authorization_error"
    NOT_FOUND = "not_found_error"
    RATE_LIMIT = "rate_limit_error"
    EXTERNAL_SERVICE = "external_service_error"
    INTERNAL_SERVER = "internal_server_error"
    CONFIGURATION = "configuration_error"
    TIMEOUT = "timeout_error"
    BUSINESS_LOGIC = "business_logic_error"


class EvolSynthException(Exception):
    """Base exception class for EvolSynth API"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.INTERNAL_SERVER,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.category = category
        self.status_code = status_code
        self.details = details or {}
        self.user_message = user_message or message
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class ValidationError(EvolSynthException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {"field": field, "value": str(value)} if field else {}
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            status_code=400,
            details=details,
            user_message=f"Invalid input: {message}"
        )


class AuthenticationError(EvolSynthException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            status_code=401,
            user_message="Authentication required"
        )


class AuthorizationError(EvolSynthException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION,
            status_code=403,
            user_message="Access denied"
        )


class NotFoundError(EvolSynthException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with ID '{identifier}' not found"
        super().__init__(
            message=message,
            category=ErrorCategory.NOT_FOUND,
            status_code=404,
            details={"resource": resource, "identifier": identifier},
            user_message=f"The requested {resource.lower()} was not found"
        )


class RateLimitError(EvolSynthException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, window: str):
        message = f"Rate limit exceeded: {limit} requests per {window}"
        super().__init__(
            message=message,
            category=ErrorCategory.RATE_LIMIT,
            status_code=429,
            details={"limit": limit, "window": window},
            user_message="Too many requests. Please try again later."
        )


class ExternalServiceError(EvolSynthException):
    """Raised when external service calls fail"""
    
    def __init__(self, service: str, message: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"External service error ({service}): {message}",
            category=ErrorCategory.EXTERNAL_SERVICE,
            status_code=503,
            details={"service": service, "external_status_code": status_code},
            user_message="Service temporarily unavailable. Please try again later."
        )


class TimeoutError(EvolSynthException):
    """Raised when operations timeout"""
    
    def __init__(self, operation: str, timeout: float):
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(
            message=message,
            category=ErrorCategory.TIMEOUT,
            status_code=408,
            details={"operation": operation, "timeout": timeout},
            user_message="The request timed out. Please try again."
        )


class ConfigurationError(EvolSynthException):
    """Raised when configuration is invalid"""
    
    def __init__(self, setting: str, message: str):
        super().__init__(
            message=f"Configuration error for '{setting}': {message}",
            category=ErrorCategory.CONFIGURATION,
            status_code=500,
            details={"setting": setting},
            user_message="Service configuration error. Please contact support."
        )


class BusinessLogicError(EvolSynthException):
    """Raised when business logic validation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.BUSINESS_LOGIC,
            status_code=422,
            details=details,
            user_message=message
        )


def create_error_response(
    error: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 500,
    category: Optional[ErrorCategory] = None
) -> ErrorResponse:
    """Create a standardized error response"""
    return ErrorResponse(
        error=error,
        message=message,
        details=details or {},
        category=category.value if category else ErrorCategory.INTERNAL_SERVER.value,
        timestamp=datetime.utcnow(),
        status_code=status_code
    )


def handle_evolsynth_exception(exc: EvolSynthException) -> ErrorResponse:
    """Handle EvolSynth custom exceptions"""
    logger = logging.getLogger("api.errors")
    
    # Log the error
    logger.error(
        f"EvolSynth exception: {exc.message}",
        extra={
            "extra_fields": {
                "category": exc.category.value,
                "status_code": exc.status_code,
                "details": exc.details,
                "timestamp": exc.timestamp.isoformat()
            }
        },
        exc_info=True
    )
    
    return ErrorResponse(
        error=exc.category.value,
        message=exc.user_message,
        details=exc.details,
        category=exc.category.value,
        timestamp=exc.timestamp,
        status_code=exc.status_code
    )


def handle_generic_exception(exc: Exception) -> ErrorResponse:
    """Handle generic exceptions"""
    logger = logging.getLogger("api.errors")
    
    # Log the full exception
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "extra_fields": {
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc()
            }
        },
        exc_info=True
    )
    
    return ErrorResponse(
        error="internal_server_error",
        message="An unexpected error occurred",
        details={"exception_type": type(exc).__name__},
        category=ErrorCategory.INTERNAL_SERVER.value,
        timestamp=datetime.utcnow(),
        status_code=500
    )


def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create an HTTPException with proper error format"""
    error_response = create_error_response(
        error=f"http_{status_code}",
        message=message,
        details=details,
        status_code=status_code
    )
    
    return HTTPException(
        status_code=status_code,
        detail=error_response.dict()
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the FastAPI application"""
    
    if isinstance(exc, EvolSynthException):
        error_response = handle_evolsynth_exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict()
        )
    
    elif isinstance(exc, HTTPException):
        # Handle FastAPI HTTPExceptions
        error_response = create_error_response(
            error="http_exception",
            message=str(exc.detail),
            status_code=exc.status_code
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict()
        )
    
    else:
        # Handle all other exceptions
        error_response = handle_generic_exception(exc)
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )


def validate_and_raise(
    condition: bool,
    message: str,
    exception_class: type = ValidationError,
    **kwargs
) -> None:
    """Validate a condition and raise an exception if it fails"""
    if not condition:
        raise exception_class(message, **kwargs)


def safe_execute(
    func,
    *args,
    default_return=None,
    log_errors: bool = True,
    **kwargs
) -> Any:
    """Safely execute a function and handle exceptions"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger = logging.getLogger("api.errors")
            logger.error(f"Safe execution failed for {func.__name__}: {str(e)}", exc_info=True)
        return default_return


class ErrorCollector:
    """Collect multiple errors and raise them together"""
    
    def __init__(self):
        self.errors: List[str] = []
    
    def add_error(self, message: str) -> None:
        """Add an error message"""
        self.errors.append(message)
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0
    
    def raise_if_errors(self, exception_class: type = ValidationError) -> None:
        """Raise an exception if there are any errors"""
        if self.has_errors():
            raise exception_class(
                f"Multiple validation errors: {'; '.join(self.errors)}",
                details={"errors": self.errors}
            )
    
    def get_errors(self) -> List[str]:
        """Get all collected errors"""
        return self.errors.copy() 