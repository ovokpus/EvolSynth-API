"""
Security utilities for EvolSynth API
Provides rate limiting, input sanitization, authentication, and other security measures
"""

import hashlib
import re
import time
import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from urllib.parse import urlparse

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import bleach

from api.config import settings
from api.utils.error_handling import RateLimitError, ValidationError, AuthenticationError
from api.utils.logging_config import get_logger, log_security_event


# Security logger
security_logger = get_logger("api.security")


class RateLimiter:
    """Token bucket rate limiter with Redis support"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.local_buckets: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int,
        burst: Optional[int] = None
    ) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Unique identifier for rate limiting (IP, user ID, etc.)
            limit: Number of requests allowed
            window: Time window in seconds
            burst: Optional burst limit (defaults to limit)
        """
        burst = burst or limit
        current_time = time.time()
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_expired_entries()
            self.last_cleanup = current_time
        
        if self.redis_client:
            return await self._redis_rate_limit(key, limit, window, burst, current_time)
        else:
            return await self._local_rate_limit(key, limit, window, burst, current_time)
    
    async def _redis_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        burst: int,
        current_time: float
    ) -> bool:
        """Redis-based rate limiting"""
        try:
            if not self.redis_client:
                return await self._local_rate_limit(key, limit, window, burst, current_time)
            
            pipe = self.redis_client.pipeline()
            
            # Use sliding window log approach
            window_key = f"rate_limit:{key}:{window}"
            
            # Remove expired entries
            expire_time = current_time - window
            pipe.zremrangebyscore(window_key, 0, expire_time)
            
            # Count current requests
            pipe.zcard(window_key)
            
            # Add current request
            pipe.zadd(window_key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(window_key, window + 1)
            
            results = pipe.execute()
            current_count = results[1] if len(results) > 1 else 0
            
            return current_count < limit
            
        except Exception as e:
            security_logger.warning(f"Redis rate limiting failed, falling back to local: {e}")
            return await self._local_rate_limit(key, limit, window, burst, current_time)
    
    async def _local_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        burst: int,
        current_time: float
    ) -> bool:
        """Local memory-based rate limiting"""
        if key not in self.local_buckets:
            self.local_buckets[key] = {
                "tokens": burst,
                "last_refill": current_time,
                "requests": deque()
            }
        
        bucket = self.local_buckets[key]
        
        # Remove old requests outside the window
        cutoff_time = current_time - window
        while bucket["requests"] and bucket["requests"][0] < cutoff_time:
            bucket["requests"].popleft()
        
        # Check if under limit
        if len(bucket["requests"]) < limit:
            bucket["requests"].append(current_time)
            return True
        
        return False
    
    async def _cleanup_expired_entries(self):
        """Clean up expired local rate limit entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, bucket in self.local_buckets.items():
            # Remove old requests
            cutoff_time = current_time - 3600  # 1 hour
            while bucket["requests"] and bucket["requests"][0] < cutoff_time:
                bucket["requests"].popleft()
            
            # Mark bucket for deletion if empty and old
            if (not bucket["requests"] and 
                current_time - bucket["last_refill"] > 3600):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.local_buckets[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


class InputSanitizer:
    """Input sanitization and validation"""
    
    # Common patterns for validation
    PATTERNS = {
        "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
        "username": re.compile(r"^[a-zA-Z0-9_-]{3,50}$"),
        "filename": re.compile(r"^[a-zA-Z0-9._-]+$"),
        "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"),
        "alphanumeric": re.compile(r"^[a-zA-Z0-9]+$"),
    }
    
    # Allowed HTML tags for content that might need formatting
    ALLOWED_HTML_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
    ]
    
    # Allowed HTML attributes
    ALLOWED_HTML_ATTRIBUTES = {
        '*': ['class'],
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title'],
    }
    
    @staticmethod
    def sanitize_html(content: str) -> str:
        """Sanitize HTML content"""
        if not content:
            return ""
        
        return bleach.clean(
            content,
            tags=InputSanitizer.ALLOWED_HTML_TAGS,
            attributes=InputSanitizer.ALLOWED_HTML_ATTRIBUTES,
            strip=True
        )
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        if not filename:
            return ""
        
        # Remove directory separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        sanitized = sanitized.replace('..', '')
        
        # Limit length
        return sanitized[:255] if sanitized else "unnamed"
    
    @staticmethod
    def validate_pattern(value: str, pattern_name: str) -> bool:
        """Validate input against a pattern"""
        pattern = InputSanitizer.PATTERNS.get(pattern_name)
        if not pattern:
            return False
        
        return bool(pattern.match(value))
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        """Sanitize plain text input"""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Limit length
        return sanitized[:max_length] if len(sanitized) > max_length else sanitized
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[Set[str]] = None) -> bool:
        """Validate URL format and scheme"""
        if not url:
            return False
        
        allowed_schemes = allowed_schemes or {'http', 'https'}
        
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in allowed_schemes and
                bool(parsed.netloc) and
                len(url) <= 2000  # Reasonable URL length limit
            )
        except Exception:
            return False


class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), location=()"
        }


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers (common in production with load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct connection
    if request.client and hasattr(request.client, "host"):
        return request.client.host
    
    return "unknown"


async def rate_limit_dependency(
    request: Request,
    limit: int = 100,
    window: int = 3600,
    per: str = "ip"
) -> None:
    """
    FastAPI dependency for rate limiting
    
    Args:
        request: FastAPI request object
        limit: Number of requests allowed
        window: Time window in seconds
        per: What to rate limit by ("ip", "user", etc.)
    """
    if per == "ip":
        key = f"ip:{get_client_ip(request)}"
    else:
        key = f"{per}:unknown"
    
    if not await rate_limiter.is_allowed(key, limit, window):
        log_security_event(
            "RATE_LIMIT_EXCEEDED",
            f"Rate limit exceeded for {key}",
            "WARNING",
            {"key": key, "limit": limit, "window": window}
        )
        raise RateLimitError(limit, f"{window} seconds")


def create_rate_limit_dependency(limit: int, window: int, per: str = "ip"):
    """Create a rate limit dependency with specific parameters"""
    async def dependency(request: Request):
        await rate_limit_dependency(request, limit, window, per)
    return dependency


# Common rate limit dependencies
RateLimit = create_rate_limit_dependency(100, 3600)  # 100 per hour
StrictRateLimit = create_rate_limit_dependency(10, 600)  # 10 per 10 minutes
APIKeyRateLimit = create_rate_limit_dependency(1000, 3600)  # 1000 per hour for API keys


def configure_cors(app, allowed_origins: Optional[List[str]] = None) -> None:
    """Configure CORS middleware with security best practices"""
    if allowed_origins is None:
        if settings.debug:
            # Development: Allow common development origins
            allowed_origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000", 
                "http://localhost:3001",
                "http://127.0.0.1:3001",
                "http://localhost:8000",
                "http://127.0.0.1:8000"
            ]
        else:
            # Production: Specify exact origins
            allowed_origins = [
                "https://yourdomain.com",
                "https://www.yourdomain.com",
                "https://api.yourdomain.com"
            ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-Request-ID"],
        max_age=600,  # 10 minutes
    )


def hash_sensitive_data(data: str, salt: str = "") -> str:
    """Hash sensitive data for logging/storage"""
    return hashlib.sha256((data + salt).encode()).hexdigest()[:16]


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data for logging"""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


# Simple authentication for demonstration (replace with proper auth in production)
class SimpleAuthBearer(HTTPBearer):
    """Simple bearer token authentication"""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super().__call__(request)
        
        if credentials:
            # In production, validate the token properly
            if not self.verify_token(credentials.credentials):
                log_security_event(
                    "INVALID_TOKEN",
                    f"Invalid authentication token from {get_client_ip(request)}",
                    "WARNING",
                    {"ip": get_client_ip(request)}
                )
                raise AuthenticationError("Invalid authentication token")
        
        return credentials
    
    def verify_token(self, token: str) -> bool:
        """Verify bearer token (implement proper verification in production)"""
        # This is a placeholder - implement proper JWT verification
        return len(token) > 10  # Minimal validation for demo


# Global auth instance
auth_bearer = SimpleAuthBearer()


def require_auth():
    """Dependency that requires authentication"""
    return Depends(auth_bearer) 