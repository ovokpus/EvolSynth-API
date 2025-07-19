"""
Unit tests for cache manager utilities
Tests CacheManager, DocumentCache, ResultCache, and SessionCache with comprehensive coverage
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import redis
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path for imports  
project_root = Path(__file__).parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from api.utils.cache_manager import (
    CacheManager,
    DocumentCache,
    ResultCache,
    SessionCache
)


class TestCacheManager(unittest.TestCase):
    """Test CacheManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_redis = Mock(spec=redis.Redis)
        self.mock_redis.ping.return_value = True
        self.mock_redis.get.return_value = None
        self.mock_redis.setex.return_value = True
        self.mock_redis.delete.return_value = 1
        self.mock_redis.exists.return_value = False
        self.mock_redis.keys.return_value = []
        self.mock_redis.info.return_value = {
            'redis_version': '7.0.0',
            'connected_clients': 1,
            'used_memory': 1000000,
            'used_memory_human': '1MB',
            'keyspace_hits': 100,
            'keyspace_misses': 10,
            'total_commands_processed': 1000
        }
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_cache_manager_redis_success(self, mock_redis_class):
        """Test CacheManager initialization with successful Redis connection"""
        mock_redis_class.return_value = self.mock_redis
        
        cache_manager = CacheManager()
        
        assert cache_manager.cache_enabled is True
        assert cache_manager.redis_client == self.mock_redis
        self.mock_redis.ping.assert_called_once()
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_cache_manager_redis_failure(self, mock_redis_class):
        """Test CacheManager initialization with Redis connection failure"""
        mock_redis_class.side_effect = redis.ConnectionError("Connection failed")
        
        cache_manager = CacheManager()
        
        assert cache_manager.cache_enabled is False
        assert isinstance(cache_manager.memory_cache, dict)
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_generate_key_with_dict(self, mock_redis_class):
        """Test cache key generation with dictionary data"""
        mock_redis_class.return_value = self.mock_redis
        cache_manager = CacheManager()
        
        data = {"key1": "value1", "key2": "value2"}
        key = cache_manager.generate_key("test", data)
        
        assert key.startswith("test:")
        assert len(key.split(":")[1]) == 16  # SHA-256 truncated to 16 chars
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_generate_key_with_string(self, mock_redis_class):
        """Test cache key generation with string data"""
        mock_redis_class.return_value = self.mock_redis
        cache_manager = CacheManager()
        
        data = "test_string"
        key = cache_manager.generate_key("test", data)
        
        assert key.startswith("test:")
        assert len(key.split(":")[1]) == 16
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_get_cache_hit(self, mock_redis_class):
        """Test cache get operation - cache hit"""
        mock_redis_class.return_value = self.mock_redis
        test_data = {"test": "data"}
        self.mock_redis.get.return_value = pickle.dumps(test_data)
        
        cache_manager = CacheManager()
        result = cache_manager.get("test:key")
        
        assert result == test_data
        self.mock_redis.get.assert_called_once_with("test:key")
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_get_cache_miss(self, mock_redis_class):
        """Test cache get operation - cache miss"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.get.return_value = None
        
        cache_manager = CacheManager()
        result = cache_manager.get("test:key")
        
        assert result is None
        self.mock_redis.get.assert_called_once_with("test:key")
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_get_pickle_error(self, mock_redis_class):
        """Test cache get operation with pickle error"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.get.return_value = b"invalid pickle data"
        self.mock_redis.delete.return_value = 1
        
        cache_manager = CacheManager()
        result = cache_manager.get("test:key")
        
        assert result is None
        self.mock_redis.delete.assert_called_once_with("test:key")
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_get_redis_connection_error(self, mock_redis_class):
        """Test cache get operation with Redis connection error"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.get.side_effect = redis.ConnectionError("Connection lost")
        
        cache_manager = CacheManager()
        cache_manager.memory_cache["test:key"] = {"value": "test"}
        result = cache_manager.get("test:key")
        
        assert result == {"value": "test"}
        assert cache_manager.cache_enabled is False
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_set_success(self, mock_redis_class):
        """Test cache set operation - success"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.setex.return_value = True
        
        cache_manager = CacheManager()
        test_data = {"test": "data"}
        result = cache_manager.set("test:key", test_data, 3600)
        
        assert result is True
        self.mock_redis.setex.assert_called_once()
        args = self.mock_redis.setex.call_args[0]
        assert args[0] == "test:key"
        assert args[1] == 3600
        assert pickle.loads(args[2]) == test_data
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_set_redis_connection_error(self, mock_redis_class):
        """Test cache set operation with Redis connection error"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.setex.side_effect = redis.ConnectionError("Connection lost")
        
        cache_manager = CacheManager()
        test_data = {"test": "data"}
        result = cache_manager.set("test:key", test_data, 3600)
        
        assert result is True  # Falls back to memory cache
        assert "test:key" in cache_manager.memory_cache
        assert cache_manager.cache_enabled is False
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_delete_success(self, mock_redis_class):
        """Test cache delete operation - success"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.delete.return_value = 1
        
        cache_manager = CacheManager()
        result = cache_manager.delete("test:key")
        
        assert result is True
        self.mock_redis.delete.assert_called_once_with("test:key")
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_exists_true(self, mock_redis_class):
        """Test cache exists operation - key exists"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.exists.return_value = 1
        
        cache_manager = CacheManager()
        result = cache_manager.exists("test:key")
        
        assert result is True
        self.mock_redis.exists.assert_called_once_with("test:key")
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_exists_false(self, mock_redis_class):
        """Test cache exists operation - key doesn't exist"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.exists.return_value = 0
        
        cache_manager = CacheManager()
        result = cache_manager.exists("test:key")
        
        assert result is False
        self.mock_redis.exists.assert_called_once_with("test:key")
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_clear_prefix_success(self, mock_redis_class):
        """Test cache clear prefix operation - success"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.keys.return_value = ["test:key1", "test:key2"]
        self.mock_redis.delete.return_value = 2
        
        cache_manager = CacheManager()
        result = cache_manager.clear_prefix("test")
        
        assert result == 2
        self.mock_redis.keys.assert_called_once_with("test:*")
        self.mock_redis.delete.assert_called_once_with("test:key1", "test:key2")
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_clear_prefix_no_keys(self, mock_redis_class):
        """Test cache clear prefix operation - no keys found"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.keys.return_value = []
        
        cache_manager = CacheManager()
        result = cache_manager.clear_prefix("test")
        
        assert result == 0
        self.mock_redis.keys.assert_called_once_with("test:*")
        self.mock_redis.delete.assert_not_called()
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_get_stats_redis(self, mock_redis_class):
        """Test cache statistics with Redis"""
        mock_redis_class.return_value = self.mock_redis
        
        cache_manager = CacheManager()
        stats = cache_manager.get_stats()
        
        assert stats["cache_type"] == "redis"
        assert stats["cache_enabled"] is True
        assert stats["redis_version"] == "7.0.0"
        assert stats["hit_ratio"] == round((100 / 110 * 100), 2)
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_get_stats_memory(self, mock_redis_class):
        """Test cache statistics with memory cache"""
        mock_redis_class.side_effect = redis.ConnectionError("No Redis")
        
        cache_manager = CacheManager()
        cache_manager.memory_cache = {"key1": "value1", "key2": "value2"}
        stats = cache_manager.get_stats()
        
        assert stats["cache_type"] == "memory"
        assert stats["cache_enabled"] is False
        assert stats["memory_cache_size"] == 2
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_health_check_redis_healthy(self, mock_redis_class):
        """Test health check with healthy Redis"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.ping.return_value = True
        self.mock_redis.get.return_value = b"test"
        
        cache_manager = CacheManager()
        health = cache_manager.health_check()
        
        assert health["healthy"] is True
        assert health["cache_type"] == "redis"
        assert "successful" in health["details"]
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_health_check_redis_unhealthy(self, mock_redis_class):
        """Test health check with unhealthy Redis"""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.ping.side_effect = redis.ConnectionError("Connection failed")
        
        cache_manager = CacheManager()
        health = cache_manager.health_check()
        
        assert health["healthy"] is False
        assert "failed" in health["details"]
    
    @patch('api.utils.cache_manager.redis.Redis')
    def test_health_check_memory_cache(self, mock_redis_class):
        """Test health check with memory cache"""
        mock_redis_class.side_effect = redis.ConnectionError("No Redis")
        
        cache_manager = CacheManager()
        health = cache_manager.health_check()
        
        assert health["healthy"] is True
        assert health["cache_type"] == "memory"
        assert "operational" in health["details"]
    
    def test_memory_cache_operations(self):
        """Test memory cache operations when Redis is unavailable"""
        with patch('api.utils.cache_manager.redis.Redis') as mock_redis_class:
            mock_redis_class.side_effect = redis.ConnectionError("No Redis")
            
            cache_manager = CacheManager()
            
            # Test set
            result = cache_manager.set("test:key", {"data": "test"}, 3600)
            assert result is True
            
                     # Test get
         result = cache_manager.get("test:key")
         assert result is not None and result["data"] == "test"
            
            # Test exists
            result = cache_manager.exists("test:key")
            assert result is True
            
            # Test delete
            result = cache_manager.delete("test:key")
            assert result is True
            
            # Verify key is gone
            result = cache_manager.exists("test:key")
            assert result is False
    
    def test_memory_cache_expiry(self):
        """Test memory cache expiry functionality"""
        with patch('api.utils.cache_manager.redis.Redis') as mock_redis_class:
            mock_redis_class.side_effect = redis.ConnectionError("No Redis")
            
            cache_manager = CacheManager()
            
            # Set key with expiry in the past
            past_time = datetime.now() - timedelta(seconds=3600)
            cache_manager.memory_cache["test:key"] = {
                "value": {"data": "test"},
                "expiry": past_time
            }
            
            # Should return False and clean up expired key
            result = cache_manager.exists("test:key")
            assert result is False
            assert "test:key" not in cache_manager.memory_cache


class TestDocumentCache(unittest.TestCase):
    """Test DocumentCache class"""
    
    @patch('api.utils.cache_manager.CacheManager')
    def test_document_cache_get_content(self, mock_cache_manager_class):
        """Test getting document content from cache"""
        mock_cache_manager = Mock()
        mock_cache_manager.get.return_value = "document content"
        mock_cache_manager_class.return_value = mock_cache_manager
        
        doc_cache = DocumentCache(mock_cache_manager)
        result = doc_cache.get_document_content("doc123")
        
        assert result == "document content"
        mock_cache_manager.get.assert_called_once_with("docs:doc123")
    
    @patch('api.utils.cache_manager.CacheManager')
    def test_document_cache_save_content(self, mock_cache_manager_class):
        """Test saving document content to cache"""
        mock_cache_manager = Mock()
        mock_cache_manager.set.return_value = True
        mock_cache_manager_class.return_value = mock_cache_manager
        
        doc_cache = DocumentCache(mock_cache_manager)
        result = doc_cache.save_document_content("doc123", "content")
        
        assert result is True
        mock_cache_manager.set.assert_called_once_with("docs:doc123", "content", doc_cache.default_ttl)


class TestResultCache(unittest.TestCase):
    """Test ResultCache class"""
    
    @patch('api.utils.cache_manager.CacheManager')
    def test_result_cache_get_result(self, mock_cache_manager_class):
        """Test getting generation result from cache"""
        mock_cache_manager = Mock()
        test_result = {"questions": ["Q1", "Q2"], "status": "completed"}
        mock_cache_manager.get.return_value = test_result
        mock_cache_manager_class.return_value = mock_cache_manager
        
        result_cache = ResultCache(mock_cache_manager)
        result = result_cache.get_generation_result("result123")
        
        assert result == test_result
        mock_cache_manager.get.assert_called_once_with("results:result123")
    
    @patch('api.utils.cache_manager.CacheManager')
    def test_result_cache_save_result(self, mock_cache_manager_class):
        """Test saving generation result to cache"""
        mock_cache_manager = Mock()
        mock_cache_manager.set.return_value = True
        mock_cache_manager_class.return_value = mock_cache_manager
        
        test_result = {"questions": ["Q1", "Q2"], "status": "completed"}
        result_cache = ResultCache(mock_cache_manager)
        result = result_cache.save_generation_result("result123", test_result)
        
        assert result is True
        mock_cache_manager.set.assert_called_once_with("results:result123", test_result, result_cache.default_ttl)


class TestSessionCache(unittest.TestCase):
    """Test SessionCache class"""
    
    @patch('api.utils.cache_manager.CacheManager')
    def test_session_cache_get_data(self, mock_cache_manager_class):
        """Test getting session data from cache"""
        mock_cache_manager = Mock()
        session_data = {"user_id": "user123", "progress": 50}
        mock_cache_manager.get.return_value = session_data
        mock_cache_manager_class.return_value = mock_cache_manager
        
        session_cache = SessionCache(mock_cache_manager)
        result = session_cache.get_session_data("session123")
        
        assert result == session_data
        mock_cache_manager.get.assert_called_once_with("sessions:session123")
    
    @patch('api.utils.cache_manager.CacheManager')
    def test_session_cache_save_data(self, mock_cache_manager_class):
        """Test saving session data to cache"""
        mock_cache_manager = Mock()
        mock_cache_manager.set.return_value = True
        mock_cache_manager_class.return_value = mock_cache_manager
        
        session_data = {"user_id": "user123", "progress": 50}
        session_cache = SessionCache(mock_cache_manager)
        result = session_cache.save_session_data("session123", session_data)
        
        assert result is True
        mock_cache_manager.set.assert_called_once_with("sessions:session123", session_data, session_cache.default_ttl)
    
    @patch('api.utils.cache_manager.CacheManager')
    def test_session_cache_update_progress(self, mock_cache_manager_class):
        """Test updating session progress"""
        mock_cache_manager = Mock()
        existing_data = {"user_id": "user123", "progress": 30}
        mock_cache_manager.get.return_value = existing_data
        mock_cache_manager.set.return_value = True
        mock_cache_manager_class.return_value = mock_cache_manager
        
        session_cache = SessionCache(mock_cache_manager)
        result = session_cache.update_progress("session123", 75.0, "processing")
        
        assert result is True
        
        # Verify get was called to retrieve existing data
        mock_cache_manager.get.assert_called_once_with("sessions:session123")
        
        # Verify set was called with updated data
        set_call_args = mock_cache_manager.set.call_args[0]
        updated_data = set_call_args[1]
        assert updated_data["progress"] == 75.0
        assert updated_data["status"] == "processing"
        assert updated_data["user_id"] == "user123"  # Preserved from existing data
        assert "last_update" in updated_data
    
    @patch('api.utils.cache_manager.CacheManager')
    def test_session_cache_update_progress_no_existing_data(self, mock_cache_manager_class):
        """Test updating session progress with no existing data"""
        mock_cache_manager = Mock()
        mock_cache_manager.get.return_value = None  # No existing data
        mock_cache_manager.set.return_value = True
        mock_cache_manager_class.return_value = mock_cache_manager
        
        session_cache = SessionCache(mock_cache_manager)
        result = session_cache.update_progress("session123", 25.0, "started")
        
        assert result is True
        
        # Verify set was called with new data
        set_call_args = mock_cache_manager.set.call_args[0]
        updated_data = set_call_args[1]
        assert updated_data["progress"] == 25.0
        assert updated_data["status"] == "started"
        assert "last_update" in updated_data


if __name__ == '__main__':
    unittest.main() 