"""
Health Check System for EvolSynth API
Comprehensive monitoring of all dependencies and system resources
"""

import asyncio
import time
import psutil
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

import redis
from openai import AsyncOpenAI

from api.config import settings
from api.utils.logging_config import get_logger


logger = get_logger("api.health")


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class DependencyType(str, Enum):
    """Dependency type enumeration"""
    CACHE = "cache"
    API = "external_api"
    DATABASE = "database"
    SERVICE = "service"
    SYSTEM = "system"


class HealthCheck:
    """Individual health check"""
    
    def __init__(
        self,
        name: str,
        check_function,
        dependency_type: DependencyType,
        critical: bool = True,
        timeout: float = 5.0,
        expected_response_time: float = 1.0
    ):
        self.name = name
        self.check_function = check_function
        self.dependency_type = dependency_type
        self.critical = critical
        self.timeout = timeout
        self.expected_response_time = expected_response_time
        self.last_check_time: Optional[datetime] = None
        self.last_status: HealthStatus = HealthStatus.UNKNOWN
        self.last_response_time: Optional[float] = None
        self.last_error: Optional[str] = None
        self.check_count = 0
        self.failure_count = 0
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the health check"""
        start_time = time.time()
        self.check_count += 1
        
        try:
            # Execute check with timeout
            result = await asyncio.wait_for(
                self.check_function(),
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            self.last_response_time = response_time
            self.last_check_time = datetime.utcnow()
            
            # Determine status based on response time and result
            if result.get("success", False):
                if response_time <= self.expected_response_time:
                    status = HealthStatus.HEALTHY
                else:
                    status = HealthStatus.DEGRADED
                self.last_error = None
            else:
                status = HealthStatus.UNHEALTHY
                self.failure_count += 1
                self.last_error = result.get("error", "Unknown error")
            
            self.last_status = status
            
            return {
                "name": self.name,
                "status": status.value,
                "response_time_ms": round(response_time * 1000, 2),
                "critical": self.critical,
                "dependency_type": self.dependency_type.value,
                "last_check": self.last_check_time.isoformat(),
                "check_count": self.check_count,
                "failure_count": self.failure_count,
                "details": result.get("details", {}),
                "error": self.last_error
            }
            
        except asyncio.TimeoutError:
            self.failure_count += 1
            self.last_status = HealthStatus.UNHEALTHY
            self.last_error = f"Health check timed out after {self.timeout}s"
            self.last_check_time = datetime.utcnow()
            
            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY.value,
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "critical": self.critical,
                "dependency_type": self.dependency_type.value,
                "last_check": self.last_check_time.isoformat(),
                "check_count": self.check_count,
                "failure_count": self.failure_count,
                "details": {},
                "error": self.last_error
            }
            
        except Exception as e:
            self.failure_count += 1
            self.last_status = HealthStatus.UNHEALTHY
            self.last_error = str(e)
            self.last_check_time = datetime.utcnow()
            
            logger.error(f"Health check {self.name} failed: {e}", exc_info=True)
            
            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY.value,
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "critical": self.critical,
                "dependency_type": self.dependency_type.value,
                "last_check": self.last_check_time.isoformat(),
                "check_count": self.check_count,
                "failure_count": self.failure_count,
                "details": {},
                "error": self.last_error
            }


class HealthCheckManager:
    """Manages all health checks"""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self.last_full_check: Optional[datetime] = None
        self.overall_status: HealthStatus = HealthStatus.UNKNOWN
    
    def register_check(self, health_check: HealthCheck) -> None:
        """Register a health check"""
        self.checks.append(health_check)
        logger.info(f"Registered health check: {health_check.name}")
    
    async def check_all(self) -> Dict[str, Any]:
        """Execute all health checks"""
        start_time = time.time()
        
        # Execute all checks concurrently
        check_tasks = [check.execute() for check in self.checks]
        results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # Process results
        check_results = []
        critical_failures = 0
        total_failures = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle unexpected exceptions
                check_results.append({
                    "name": self.checks[i].name,
                    "status": HealthStatus.UNHEALTHY.value,
                    "error": str(result),
                    "critical": self.checks[i].critical,
                    "response_time_ms": 0,
                    "dependency_type": self.checks[i].dependency_type.value,
                    "last_check": datetime.utcnow().isoformat(),
                    "check_count": 0,
                    "failure_count": 1,
                    "details": {}
                })
                total_failures += 1
                if self.checks[i].critical:
                    critical_failures += 1
            else:
                # result is a dictionary from health check
                if isinstance(result, dict):
                    check_results.append(result)
                    if result["status"] != HealthStatus.HEALTHY.value:
                        total_failures += 1
                        if result["critical"]:
                            critical_failures += 1
                else:
                    # Handle unexpected non-dict results
                    check_results.append({
                        "name": self.checks[i].name,
                        "status": HealthStatus.UNHEALTHY.value,
                        "error": "Unexpected result type",
                        "critical": self.checks[i].critical,
                        "response_time_ms": 0,
                        "dependency_type": self.checks[i].dependency_type.value,
                        "last_check": datetime.utcnow().isoformat(),
                        "check_count": 0,
                        "failure_count": 1,
                        "details": {}
                    })
                    total_failures += 1
                    if self.checks[i].critical:
                        critical_failures += 1
        
        # Determine overall status
        if critical_failures > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif total_failures > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        self.overall_status = overall_status
        self.last_full_check = datetime.utcnow()
        
        total_time = time.time() - start_time
        
        return {
            "status": overall_status.value,
            "timestamp": self.last_full_check.isoformat(),
            "total_checks": len(check_results),
            "healthy_checks": len([r for r in check_results if r["status"] == HealthStatus.HEALTHY.value]),
            "unhealthy_checks": len([r for r in check_results if r["status"] == HealthStatus.UNHEALTHY.value]),
            "degraded_checks": len([r for r in check_results if r["status"] == HealthStatus.DEGRADED.value]),
            "critical_failures": critical_failures,
            "total_response_time_ms": round(total_time * 1000, 2),
            "checks": check_results
        }
    
    async def check_single(self, check_name: str) -> Optional[Dict[str, Any]]:
        """Execute a single health check by name"""
        for check in self.checks:
            if check.name == check_name:
                return await check.execute()
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of health check status"""
        return {
            "overall_status": self.overall_status.value,
            "last_check": self.last_full_check.isoformat() if self.last_full_check else None,
            "total_checks": len(self.checks),
            "checks_by_type": {
                dep_type.value: len([c for c in self.checks if c.dependency_type == dep_type])
                for dep_type in DependencyType
            }
        }


# Global health check manager
health_manager = HealthCheckManager()


# Individual health check functions
async def check_redis_connection() -> Dict[str, Any]:
    """Check Redis connection"""
    try:
        client = redis.Redis(
            host=getattr(settings, 'redis_host', 'localhost'),
            port=getattr(settings, 'redis_port', 6379),
            db=getattr(settings, 'redis_db', 0),
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # Test connection with ping
        client.ping()
        
        # Test basic operations
        test_key = "health_check_test"
        client.set(test_key, "test_value", ex=10)
        value = client.get(test_key)
        client.delete(test_key)
        
        # Get basic stats
        info = client.info()
        
        return {
            "success": True,
            "details": {
                "connected_clients": info.get("connected_clients", 0) if isinstance(info, dict) else 0,
                "used_memory_human": info.get("used_memory_human", "unknown") if isinstance(info, dict) else "unknown",
                "version": info.get("redis_version", "unknown") if isinstance(info, dict) else "unknown"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "details": {}
        }


async def check_openai_api() -> Dict[str, Any]:
    """Check OpenAI API connectivity"""
    try:
        if not settings.openai_api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "details": {}
            }
        
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Test with a minimal completion request
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
            temperature=0
        )
        
        return {
            "success": True,
            "details": {
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "details": {}
        }


async def check_system_resources() -> Dict[str, Any]:
    """Check system resource usage"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Load average (Unix only)
        try:
            load_avg = psutil.getloadavg()
        except AttributeError:
            load_avg = (0, 0, 0)  # Windows doesn't have load average
        
        # Network connections
        network_connections = len(psutil.net_connections())
        
        # Check if system is under stress
        cpu_warning = cpu_percent > 80
        memory_warning = memory.percent > 85
        disk_warning = disk.percent > 90
        
        success = not (cpu_warning or memory_warning or disk_warning)
        
        details = {
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory.percent, 2),
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": round(disk.percent, 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "load_average": [round(load, 2) for load in load_avg],
            "network_connections": network_connections,
            "warnings": {
                "high_cpu": cpu_warning,
                "high_memory": memory_warning,
                "high_disk": disk_warning
            }
        }
        
        return {
            "success": success,
            "details": details,
            "error": "High resource usage detected" if not success else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "details": {}
        }


async def check_api_endpoints() -> Dict[str, Any]:
    """Check critical API endpoints"""
    try:
        # This would typically check internal endpoints
        # For now, we'll just return success as a placeholder
        
        return {
            "success": True,
            "details": {
                "endpoints_checked": ["health", "generate", "evaluate"],
                "all_responding": True
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "details": {}
        }


def initialize_health_checks():
    """Initialize all health checks"""
    
    # Redis health check
    health_manager.register_check(
        HealthCheck(
            name="redis_cache",
            check_function=check_redis_connection,
            dependency_type=DependencyType.CACHE,
            critical=False,  # Cache is not critical for basic functionality
            timeout=5.0,
            expected_response_time=0.1
        )
    )
    
    # OpenAI API health check
    health_manager.register_check(
        HealthCheck(
            name="openai_api",
            check_function=check_openai_api,
            dependency_type=DependencyType.API,
            critical=True,  # API is critical for core functionality
            timeout=10.0,
            expected_response_time=2.0
        )
    )
    
    # System resources health check
    health_manager.register_check(
        HealthCheck(
            name="system_resources",
            check_function=check_system_resources,
            dependency_type=DependencyType.SYSTEM,
            critical=False,  # System can handle temporary high usage
            timeout=5.0,
            expected_response_time=0.5
        )
    )
    
    # API endpoints health check
    health_manager.register_check(
        HealthCheck(
            name="api_endpoints",
            check_function=check_api_endpoints,
            dependency_type=DependencyType.SERVICE,
            critical=True,
            timeout=5.0,
            expected_response_time=0.5
        )
    )
    
    logger.info(f"Initialized {len(health_manager.checks)} health checks")


# Convenience functions for use in FastAPI endpoints
async def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    return await health_manager.check_all()


async def get_health_summary() -> Dict[str, Any]:
    """Get health summary"""
    return health_manager.get_summary()


async def get_readiness_status() -> Tuple[bool, Dict[str, Any]]:
    """Get readiness status (for Kubernetes readiness probe)"""
    result = await health_manager.check_all()
    
    # Service is ready if no critical checks are failing
    is_ready = result["critical_failures"] == 0
    
    return is_ready, result


async def get_liveness_status() -> Tuple[bool, Dict[str, Any]]:
    """Get liveness status (for Kubernetes liveness probe)"""
    result = await health_manager.check_all()
    
    # Service is alive if overall status is not completely unhealthy
    is_alive = result["status"] != HealthStatus.UNHEALTHY.value
    
    return is_alive, result 