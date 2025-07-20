"""
Logging Configuration for EvolSynth API
Provides structured logging with different levels and formatters for development and production
"""

import logging
import logging.config
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from api.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(getattr(record, "extra_fields", {}))
        
        # Add request ID if present
        if hasattr(record, "request_id"):
            log_entry["request_id"] = getattr(record, "request_id", None)
        
        # Add user ID if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = getattr(record, "user_id", None)
        
        return json.dumps(log_entry)


class RequestContextFilter(logging.Filter):
    """Filter to add request context to log records"""
    
    def __init__(self):
        super().__init__()
        self.request_id = None
        self.user_id = None
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request context to log record"""
        if self.request_id:
            record.request_id = self.request_id
        if self.user_id:
            record.user_id = self.user_id
        return True


def setup_logging(
    level: str = "INFO",
    use_json: bool = False,
    log_file: Optional[str] = None
) -> None:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting
        log_file: Optional log file path
    """
    
    # Create logs directory if it doesn't exist
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure formatters
    if use_json:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Configure handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestContextFilter())
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestContextFilter())
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers,
        force=True
    )
    
    # Configure specific loggers
    configure_loggers(level)


def configure_loggers(level: str) -> None:
    """Configure specific loggers for different components"""
    
    # API logger
    api_logger = logging.getLogger("api")
    api_logger.setLevel(getattr(logging, level.upper()))
    
    # Service loggers
    service_logger = logging.getLogger("api.services")
    service_logger.setLevel(getattr(logging, level.upper()))
    
    # Utils logger
    utils_logger = logging.getLogger("api.utils")
    utils_logger.setLevel(getattr(logging, level.upper()))
    
    # Performance logger
    perf_logger = logging.getLogger("api.performance")
    perf_logger.setLevel(logging.INFO)
    
    # Security logger
    security_logger = logging.getLogger("api.security")
    security_logger.setLevel(logging.WARNING)
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)


def log_function_call(func_name: str, args: Dict[str, Any], logger: logging.Logger) -> None:
    """Log function call with arguments"""
    logger.debug(
        f"Function call: {func_name}",
        extra={"extra_fields": {"function": func_name, "arguments": args}}
    )


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = "seconds",
    extra_data: Optional[Dict[str, Any]] = None
) -> None:
    """Log performance metrics"""
    perf_logger = logging.getLogger("api.performance")
    
    log_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if extra_data:
        log_data.update(extra_data)
    
    perf_logger.info(
        f"Performance metric: {metric_name} = {value} {unit}",
        extra={"extra_fields": log_data}
    )


def log_security_event(
    event_type: str,
    message: str,
    severity: str = "WARNING",
    extra_data: Optional[Dict[str, Any]] = None
) -> None:
    """Log security events"""
    security_logger = logging.getLogger("api.security")
    
    log_data = {
        "event_type": event_type,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if extra_data:
        log_data.update(extra_data)
    
    log_level = getattr(logging, severity.upper(), logging.WARNING)
    security_logger.log(
        log_level,
        f"Security event [{event_type}]: {message}",
        extra={"extra_fields": log_data}
    )


# Initialize logging based on settings
def initialize_api_logging():
    """Initialize logging for the API based on configuration"""
    log_level = "DEBUG" if settings.debug else "INFO"
    use_json = not settings.debug  # Use JSON in production
    log_file = "logs/evolsynth_api.log" if not settings.debug else None
    
    setup_logging(
        level=log_level,
        use_json=use_json,
        log_file=log_file
    )
    
    # Log startup message
    logger = get_logger("api.startup")
    logger.info(
        f"EvolSynth API logging initialized",
        extra={
            "extra_fields": {
                "version": settings.app_version,
                "debug_mode": settings.debug,
                "log_level": log_level,
                "json_logging": use_json
            }
        }
    ) 