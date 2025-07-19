"""
CacheManager - Redis-based caching for EvolSynth
Handles document processing cache, result cache, and session management
"""

import redis
import pickle
import hashlib
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import json

from api.config import settings


class CacheManager:
    """Manages Redis caching for improved performance"""
    
    def __init__(self):
        """Initialize Redis connection with failover"""
        try:
            self.redis_client = redis.Redis(
                host=getattr(settings, 'redis_host', 'localhost'),
                port=getattr(settings, 'redis_port', 6379),
                db=getattr(settings, 'redis_db', 0),
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5,
                max_connections=20
            )
            # Test connection
            self.redis_client.ping()
            self.cache_enabled = True
            print("✅ Redis cache connected")
        except Exception as e:
            print(f"⚠️  Redis unavailable: {e}. Using memory cache")
            self.memory_cache = {}
            self.cache_enabled = False
    
    def generate_key(self, prefix: str, data: Any) -> str:
        """Generate consistent cache key"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.cache_enabled:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return pickle.loads(cached_data)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            if self.cache_enabled:
                serialized_value = pickle.dumps(value)
                return self.redis_client.setex(key, ttl, serialized_value)
            else:
                self.memory_cache[key] = value
                return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.cache_enabled:
                return bool(self.redis_client.delete(key))
            else:
                return self.memory_cache.pop(key, None) is not None
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.cache_enabled:
                return bool(self.redis_client.exists(key))
            else:
                return key in self.memory_cache
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with given prefix"""
        try:
            if self.cache_enabled:
                keys = self.redis_client.keys(f"{prefix}:*")
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"{prefix}:")]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                return len(keys_to_delete)
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.cache_enabled:
            try:
                info = self.redis_client.info()
                return {
                    "cache_type": "redis",
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "0B"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "cache_hit_ratio": self._calculate_hit_ratio(info)
                }
            except:
                return {"cache_type": "redis", "status": "error"}
        else:
            return {
                "cache_type": "memory",
                "cached_items": len(self.memory_cache),
                "memory_usage": "N/A"
            }
    
    def _calculate_hit_ratio(self, info: Dict) -> float:
        """Calculate cache hit ratio"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


# Cache instances for different data types
class DocumentCache:
    """Specialized cache for document processing"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "docs"
        self.default_ttl = 7200  # 2 hours
    
    def get_processed_document(self, doc_hash: str) -> Optional[Dict]:
        """Get processed document from cache"""
        key = self.cache.generate_key(self.prefix, doc_hash)
        return self.cache.get(key)
    
    def save_processed_document(self, doc_hash: str, processed_data: Dict) -> bool:
        """Save processed document to cache"""
        key = self.cache.generate_key(self.prefix, doc_hash)
        return self.cache.set(key, processed_data, self.default_ttl)


class ResultCache:
    """Specialized cache for generation results"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "results"
        self.default_ttl = 3600  # 1 hour
    
    def get_generation_result(self, request_hash: str) -> Optional[Dict]:
        """Get generation result from cache"""
        key = self.cache.generate_key(self.prefix, request_hash)
        return self.cache.get(key)
    
    def save_generation_result(self, request_hash: str, result: Dict) -> bool:
        """Save generation result to cache"""
        key = self.cache.generate_key(self.prefix, request_hash)
        return self.cache.set(key, result, self.default_ttl)


class SessionCache:
    """Specialized cache for user sessions and progress tracking"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "sessions"
        self.default_ttl = 1800  # 30 minutes
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get session data from cache"""
        key = f"{self.prefix}:{session_id}"
        return self.cache.get(key)
    
    def save_session_data(self, session_id: str, data: Dict) -> bool:
        """Save session data to cache"""
        key = f"{self.prefix}:{session_id}"
        return self.cache.set(key, data, self.default_ttl)
    
    def update_progress(self, session_id: str, progress: float, status: str) -> bool:
        """Update session progress"""
        session_data = self.get_session_data(session_id) or {}
        session_data.update({
            "progress": progress,
            "status": status,
            "last_update": datetime.now().isoformat()
        })
        return self.save_session_data(session_id, session_data)


# Global cache instances
cache_manager = CacheManager()
document_cache = DocumentCache(cache_manager)
result_cache = ResultCache(cache_manager)
session_cache = SessionCache(cache_manager) 