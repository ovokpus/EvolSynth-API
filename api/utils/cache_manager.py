"""
CacheManager - Redis-based caching for EvolSynth
Handles document processing cache, result cache, and session management with proper logging and error handling
"""

import redis
import pickle
import hashlib
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import json

from api.config import settings
from api.utils.logging_config import get_logger
from api.utils.error_handling import safe_execute

logger = get_logger("api.cache")


class CacheManager:
    """Manages Redis caching for improved performance with proper error handling"""
    
    def __init__(self):
        """Initialize Redis connection with failover"""
        self.redis_client = None
        self.cache_enabled = False
        self.memory_cache = {}
        
        try:
            self.redis_client = redis.Redis(
                host=getattr(settings, 'redis_host', 'localhost'),
                port=getattr(settings, 'redis_port', 6379),
                db=getattr(settings, 'redis_db', 0),
                password=getattr(settings, 'redis_password', None),
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5,
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            self.cache_enabled = True
            logger.info("Redis cache connected successfully", extra={
                "extra_fields": {
                    "host": getattr(settings, 'redis_host', 'localhost'),
                    "port": getattr(settings, 'redis_port', 6379),
                    "db": getattr(settings, 'redis_db', 0)
                }
            })
            
        except Exception as e:
            logger.warning(
                "Redis unavailable, using memory cache fallback",
                extra={"extra_fields": {"error": str(e), "fallback": "memory_cache"}},
                exc_info=True
            )
            self.memory_cache = {}
            self.cache_enabled = False
    
    def generate_key(self, prefix: str, data: Any) -> str:
        """Generate consistent cache key with improved hashing"""
        try:
            if isinstance(data, (dict, list)):
                # Use deterministic JSON serialization
                data_str = json.dumps(data, sort_keys=True, ensure_ascii=True)
            else:
                data_str = str(data)
            
            # Use SHA-256 for better security than MD5
            hash_obj = hashlib.sha256(data_str.encode('utf-8'))
            key = f"{prefix}:{hash_obj.hexdigest()[:16]}"  # Truncate for readability
            
            logger.debug(f"Generated cache key: {key}", extra={
                "extra_fields": {"prefix": prefix, "data_type": type(data).__name__}
            })
            
            return key
            
        except Exception as e:
            logger.error(f"Failed to generate cache key: {e}", exc_info=True)
            # Fallback to simple key generation
            return f"{prefix}:{hash(str(data))}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with error handling"""
        try:
            if self.cache_enabled and self.redis_client:
                cached_data = self.redis_client.get(key)
                if cached_data and isinstance(cached_data, bytes):
                    result = pickle.loads(cached_data)
                    logger.debug(f"Cache hit for key: {key}")
                    return result
                else:
                    logger.debug(f"Cache miss for key: {key}")
                    return None
            else:
                result = self.memory_cache.get(key)
                if result:
                    logger.debug(f"Memory cache hit for key: {key}")
                else:
                    logger.debug(f"Memory cache miss for key: {key}")
                return result
                
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection error during get: {e}")
            self._handle_redis_failure()
            return self.memory_cache.get(key)
        except pickle.PickleError as e:
            logger.error(f"Failed to deserialize cached data for key {key}: {e}")
            # Remove corrupted data
            self.delete(key)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}", exc_info=True)
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL and error handling"""
        try:
            if self.cache_enabled and self.redis_client:
                serialized_value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                result = self.redis_client.setex(key, ttl, serialized_value)
                if result:
                    logger.debug(f"Cache set successful for key: {key}, TTL: {ttl}s")
                return bool(result)
            else:
                # Memory cache with simple TTL simulation
                expiry_time = datetime.now() + timedelta(seconds=ttl)
                self.memory_cache[key] = {
                    'value': value,
                    'expiry': expiry_time
                }
                logger.debug(f"Memory cache set for key: {key}")
                return True
                
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection error during set: {e}")
            self._handle_redis_failure()
            # Fallback to memory cache
            self.memory_cache[key] = {'value': value, 'expiry': datetime.now() + timedelta(seconds=ttl)}
            return True
        except pickle.PickleError as e:
            logger.error(f"Failed to serialize value for key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}", exc_info=True)
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache with error handling"""
        try:
            if self.cache_enabled and self.redis_client:
                result = self.redis_client.delete(key)
                logger.debug(f"Cache delete for key: {key}, result: {result}")
                return bool(result)
            else:
                result = self.memory_cache.pop(key, None) is not None
                logger.debug(f"Memory cache delete for key: {key}, result: {result}")
                return result
                
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection error during delete: {e}")
            self._handle_redis_failure()
            return self.memory_cache.pop(key, None) is not None
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}", exc_info=True)
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache with error handling"""
        try:
            if self.cache_enabled and self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                if key in self.memory_cache:
                    # Check expiry for memory cache
                    cache_item = self.memory_cache[key]
                    if isinstance(cache_item, dict) and 'expiry' in cache_item:
                        if datetime.now() > cache_item['expiry']:
                            del self.memory_cache[key]
                            return False
                    return True
                return False
                
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection error during exists check: {e}")
            self._handle_redis_failure()
            return key in self.memory_cache
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}", exc_info=True)
            return False
    
    def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with given prefix with error handling"""
        try:
            if self.cache_enabled and self.redis_client:
                keys = self.redis_client.keys(f"{prefix}:*")
                if keys and isinstance(keys, list):
                    deleted = self.redis_client.delete(*keys)
                    deleted_count = int(deleted) if isinstance(deleted, (int, float)) else 0
                    logger.info(f"Cleared {deleted_count} keys with prefix: {prefix}")
                    return deleted_count
                return 0
            else:
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"{prefix}:")]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                logger.info(f"Cleared {len(keys_to_delete)} memory cache keys with prefix: {prefix}")
                return len(keys_to_delete)
                
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection error during clear_prefix: {e}")
            self._handle_redis_failure()
            keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"{prefix}:")]
            for key in keys_to_delete:
                del self.memory_cache[key]
            return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache clear error for prefix {prefix}: {e}", exc_info=True)
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics with error handling"""
        stats = {
            "cache_type": "memory" if not self.cache_enabled else "redis",
            "cache_enabled": self.cache_enabled,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if self.cache_enabled and self.redis_client:
                info = self.redis_client.info()
                if isinstance(info, dict):
                    stats.update({
                        "redis_version": info.get("redis_version", "unknown"),
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory": info.get("used_memory", 0),
                        "used_memory_human": info.get("used_memory_human", "unknown"),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0),
                        "total_commands_processed": info.get("total_commands_processed", 0)
                    })
                    
                    # Calculate hit ratio
                    hits = info.get("keyspace_hits", 0)
                    misses = info.get("keyspace_misses", 0)
                    total = hits + misses
                    stats["hit_ratio"] = round((hits / total * 100), 2) if total > 0 else 0
                else:
                    stats["error"] = "Unable to retrieve Redis info"
                
            else:
                stats.update({
                    "memory_cache_size": len(self.memory_cache),
                    "hit_ratio": 0  # Could implement hit tracking for memory cache
                })
                
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}", exc_info=True)
            stats["error"] = str(e)
        
        return stats
    
    def _handle_redis_failure(self):
        """Handle Redis connection failure by switching to memory cache"""
        if self.cache_enabled:
            logger.warning("Switching to memory cache due to Redis failure")
            self.cache_enabled = False
            # Could implement Redis reconnection logic here
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on cache system"""
        health = {
            "healthy": False,
            "cache_type": "memory" if not self.cache_enabled else "redis",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if self.cache_enabled and self.redis_client:
                # Test Redis connection
                response = self.redis_client.ping()
                if response:
                    # Test basic operations
                    test_key = f"health_check:{int(time.time())}"
                    self.redis_client.setex(test_key, 10, "test")
                    retrieved = self.redis_client.get(test_key)
                    self.redis_client.delete(test_key)
                    
                    health["healthy"] = retrieved == b"test"
                    health["details"] = "Redis connection and operations successful"
                else:
                    health["details"] = "Redis ping failed"
            else:
                # Memory cache is always "healthy"
                health["healthy"] = True
                health["details"] = "Memory cache operational"
                
        except Exception as e:
            health["details"] = f"Health check failed: {str(e)}"
            logger.error(f"Cache health check failed: {e}", exc_info=True)
        
        return health


class DocumentCache:
    """Document-specific caching with enhanced error handling"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "docs"
        self.default_ttl = getattr(settings, 'document_cache_ttl', 7200)  # 2 hours
    
    def get_document_content(self, document_id: str) -> Optional[str]:
        """Get cached document content"""
        key = f"{self.prefix}:{document_id}"
        return self.cache.get(key)
    
    def save_document_content(self, document_id: str, content: str) -> bool:
        """Save document content to cache"""
        key = f"{self.prefix}:{document_id}"
        return self.cache.set(key, content, self.default_ttl)


class ResultCache:
    """Result-specific caching with enhanced error handling"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "results"
        self.default_ttl = getattr(settings, 'result_cache_ttl', 3600)  # 1 hour
    
    def get_generation_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached generation result"""
        key = f"{self.prefix}:{cache_key}"
        return self.cache.get(key)
    
    def save_generation_result(self, cache_key: str, result: Dict[str, Any]) -> bool:
        """Save generation result to cache"""
        key = f"{self.prefix}:{cache_key}"
        return self.cache.set(key, result, self.default_ttl)


class SessionCache:
    """Session-specific caching with enhanced error handling"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "sessions"
        self.default_ttl = 1800  # 30 minutes
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        key = f"{self.prefix}:{session_id}"
        return self.cache.get(key)
    
    def save_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save session data"""
        key = f"{self.prefix}:{session_id}"
        return self.cache.set(key, data, self.default_ttl)
    
    def update_progress(self, session_id: str, progress: float, status: str) -> bool:
        """Update session progress with error handling"""
        session_data = self.get_session_data(session_id) or {}
        session_data.update({
            "progress": progress,
            "status": status,
            "last_update": datetime.now().isoformat()
        })
        return self.save_session_data(session_id, session_data)


# Global cache instances with error handling
try:
    cache_manager = CacheManager()
    document_cache = DocumentCache(cache_manager)
    result_cache = ResultCache(cache_manager)
    session_cache = SessionCache(cache_manager)
    
    logger.info("Cache system initialized successfully", extra={
        "extra_fields": {
            "cache_enabled": cache_manager.cache_enabled,
            "cache_type": "redis" if cache_manager.cache_enabled else "memory"
        }
    })
    
except Exception as e:
    logger.error(f"Failed to initialize cache system: {e}", exc_info=True)
    # Create fallback instances
    cache_manager = None
    document_cache = None
    result_cache = None
    session_cache = None 