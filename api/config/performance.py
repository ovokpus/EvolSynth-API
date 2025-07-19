"""
Performance Configuration for EvolSynth API
Settings and utilities for high-performance backend optimization
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class PerformanceConfig:
    """Configuration for performance optimizations"""
    
    # Async/Concurrency Settings
    max_concurrent_requests: int = 10
    max_llm_connections: int = 5
    thread_pool_workers: int = 8
    async_batch_size: int = 5
    batch_timeout_seconds: float = 2.0
    
    # Caching Settings
    redis_enabled: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    cache_ttl_seconds: int = 3600
    document_cache_ttl: int = 7200
    result_cache_ttl: int = 3600
    
    # Background Processing
    celery_enabled: bool = True
    celery_broker: str = "redis://localhost:6379/1"
    celery_backend: str = "redis://localhost:6379/1"
    task_time_limit: int = 1800  # 30 minutes
    worker_prefetch_multiplier: int = 1
    max_tasks_per_child: int = 50
    
    # Database/Connection Pooling
    connection_pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # LLM Optimization
    llm_request_timeout: int = 60
    llm_max_retries: int = 3
    llm_retry_delay: float = 1.0
    enable_llm_batching: bool = True
    batch_processing_enabled: bool = True
    
    # Memory Management
    max_document_size_mb: int = 50
    max_memory_usage_mb: int = 2048
    garbage_collection_threshold: int = 1000
    
    # Performance Monitoring
    enable_metrics: bool = True
    metrics_collection_interval: int = 30
    performance_logging: bool = True
    slow_query_threshold: float = 5.0


class OptimizationLevel(Enum):
    """Performance optimization levels"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    HIGH_THROUGHPUT = "high_throughput"


# Optimization presets
OPTIMIZATION_PRESETS: Dict[OptimizationLevel, PerformanceConfig] = {
    OptimizationLevel.DEVELOPMENT: PerformanceConfig(
        max_concurrent_requests=5,
        max_llm_connections=2,
        thread_pool_workers=4,
        redis_enabled=False,
        celery_enabled=False,
        enable_metrics=True,
        performance_logging=True
    ),
    
    OptimizationLevel.TESTING: PerformanceConfig(
        max_concurrent_requests=8,
        max_llm_connections=3,
        thread_pool_workers=6,
        redis_enabled=True,
        celery_enabled=True,
        enable_metrics=True,
        performance_logging=True
    ),
    
    OptimizationLevel.PRODUCTION: PerformanceConfig(
        max_concurrent_requests=15,
        max_llm_connections=8,
        thread_pool_workers=12,
        redis_enabled=True,
        celery_enabled=True,
        enable_metrics=True,
        performance_logging=False,
        cache_ttl_seconds=7200
    ),
    
    OptimizationLevel.HIGH_THROUGHPUT: PerformanceConfig(
        max_concurrent_requests=25,
        max_llm_connections=12,
        thread_pool_workers=16,
        redis_enabled=True,
        celery_enabled=True,
        async_batch_size=10,
        connection_pool_size=50,
        max_tasks_per_child=100,
        enable_metrics=True,
        performance_logging=False
    )
}


def get_optimization_config(level: OptimizationLevel = OptimizationLevel.PRODUCTION) -> PerformanceConfig:
    """Get performance configuration for specified optimization level"""
    return OPTIMIZATION_PRESETS[level]


def apply_environment_overrides(config: PerformanceConfig) -> PerformanceConfig:
    """Apply environment variable overrides to configuration"""
    
    # Redis settings
    redis_host = os.getenv("REDIS_HOST")
    if redis_host:
        config.redis_host = redis_host
    
    redis_port = os.getenv("REDIS_PORT")
    if redis_port:
        config.redis_port = int(redis_port)
    
    redis_password = os.getenv("REDIS_PASSWORD")
    if redis_password:
        config.redis_password = redis_password
    
    redis_enabled = os.getenv("REDIS_ENABLED")
    if redis_enabled:
        config.redis_enabled = redis_enabled.lower() == "true"
    
    # Concurrency settings
    max_concurrent = os.getenv("MAX_CONCURRENT_REQUESTS")
    if max_concurrent:
        config.max_concurrent_requests = int(max_concurrent)
    
    max_llm_connections = os.getenv("MAX_LLM_CONNECTIONS")
    if max_llm_connections:
        config.max_llm_connections = int(max_llm_connections)
    
    thread_pool_workers = os.getenv("THREAD_POOL_WORKERS")
    if thread_pool_workers:
        config.thread_pool_workers = int(thread_pool_workers)
    
    # Celery settings
    celery_enabled = os.getenv("CELERY_ENABLED")
    if celery_enabled:
        config.celery_enabled = celery_enabled.lower() == "true"
    
    celery_broker = os.getenv("CELERY_BROKER")
    if celery_broker:
        config.celery_broker = celery_broker
    
    celery_backend = os.getenv("CELERY_BACKEND")
    if celery_backend:
        config.celery_backend = celery_backend
    
    return config


# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "requests_per_second": 0.0,
            "average_response_time": 0.0,
            "cache_hit_ratio": 0.0,
            "active_connections": 0,
            "memory_usage_mb": 0.0,
            "cpu_usage_percent": 0.0,
            "queue_length": 0,
            "error_rate": 0.0
        }
        self.request_times = []
        self.request_count = 0
        self.error_count = 0
    
    def record_request(self, response_time: float, success: bool = True):
        """Record a request for metrics"""
        self.request_times.append(response_time)
        self.request_count += 1
        
        if not success:
            self.error_count += 1
        
        # Keep only recent request times (last 100)
        if len(self.request_times) > 100:
            self.request_times = self.request_times[-100:]
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if self.request_times:
            avg_response_time = sum(self.request_times) / len(self.request_times)
            self.metrics["average_response_time"] = round(avg_response_time, 3)
        
        if self.request_count > 0:
            self.metrics["error_rate"] = round((self.error_count / self.request_count) * 100, 2)
        
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.request_times = []
        self.request_count = 0
        self.error_count = 0


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# Performance optimization recommendations
PERFORMANCE_RECOMMENDATIONS = {
    "high_response_time": [
        "Enable Redis caching",
        "Increase LLM connection pool size",
        "Enable background task processing",
        "Optimize document processing batch size"
    ],
    "high_memory_usage": [
        "Implement document streaming",
        "Reduce batch sizes",
        "Enable garbage collection tuning",
        "Optimize cache TTL settings"
    ],
    "low_cache_hit_ratio": [
        "Increase cache TTL values",
        "Optimize cache key generation",
        "Review caching strategy",
        "Increase Redis memory allocation"
    ],
    "high_error_rate": [
        "Implement circuit breaker pattern",
        "Add retry logic with exponential backoff",
        "Improve error handling",
        "Monitor external service health"
    ],
    "high_queue_length": [
        "Increase Celery worker count",
        "Optimize task processing time",
        "Implement task prioritization",
        "Scale horizontally with more worker nodes"
    ]
}


def get_performance_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Get performance optimization recommendations based on current metrics"""
    recommendations = []
    
    # Analyze metrics and provide recommendations
    if metrics.get("average_response_time", 0) > 10:
        recommendations.extend(PERFORMANCE_RECOMMENDATIONS["high_response_time"])
    
    if metrics.get("memory_usage_mb", 0) > 1500:
        recommendations.extend(PERFORMANCE_RECOMMENDATIONS["high_memory_usage"])
    
    if metrics.get("cache_hit_ratio", 100) < 70:
        recommendations.extend(PERFORMANCE_RECOMMENDATIONS["low_cache_hit_ratio"])
    
    if metrics.get("error_rate", 0) > 5:
        recommendations.extend(PERFORMANCE_RECOMMENDATIONS["high_error_rate"])
    
    if metrics.get("queue_length", 0) > 100:
        recommendations.extend(PERFORMANCE_RECOMMENDATIONS["high_queue_length"])
    
    return list(set(recommendations))  # Remove duplicates


# Load balancing configuration
@dataclass
class LoadBalancingConfig:
    """Configuration for load balancing and scaling"""
    
    enable_load_balancing: bool = True
    max_requests_per_worker: int = 1000
    worker_timeout: int = 30
    graceful_shutdown_timeout: int = 30
    auto_scaling_enabled: bool = False
    min_workers: int = 2
    max_workers: int = 10
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.3


def get_production_config() -> Dict[str, Any]:
    """Get production-ready performance configuration"""
    config = get_optimization_config(OptimizationLevel.PRODUCTION)
    config = apply_environment_overrides(config)
    
    return {
        "performance": config,
        "load_balancing": LoadBalancingConfig(),
        "monitoring": {
            "enabled": True,
            "metrics_endpoint": "/metrics",
            "health_check_endpoint": "/health/detailed"
        }
    }


def integrate_with_core_settings(core_settings) -> PerformanceConfig:
    """Integrate performance config with core settings"""
    # Get base performance config
    env = getattr(core_settings, 'environment', 'production')
    
    if env == 'development':
        config = get_optimization_config(OptimizationLevel.DEVELOPMENT)
    elif env == 'testing':
        config = get_optimization_config(OptimizationLevel.TESTING)
    elif env == 'production':
        config = get_optimization_config(OptimizationLevel.PRODUCTION)
    else:
        config = get_optimization_config(OptimizationLevel.PRODUCTION)
    
    # Override with core settings values
    config.max_concurrent_requests = getattr(core_settings, 'max_concurrency', config.max_concurrent_requests)
    config.redis_host = getattr(core_settings, 'redis_host', config.redis_host)
    config.redis_port = getattr(core_settings, 'redis_port', config.redis_port)
    config.redis_password = getattr(core_settings, 'redis_password', config.redis_password)
    config.llm_request_timeout = getattr(core_settings, 'llm_request_timeout', config.llm_request_timeout)
    config.async_batch_size = getattr(core_settings, 'batch_size', config.async_batch_size)
    
    # Apply environment overrides
    config = apply_environment_overrides(config)
    
    return config 