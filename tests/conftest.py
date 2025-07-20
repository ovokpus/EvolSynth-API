"""
Pytest configuration and fixtures for EvolSynth API tests
Provides common fixtures and test setup for comprehensive testing
"""

import pytest
import tempfile
import os
from typing import Dict, Any, Generator
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import redis
from fastapi.testclient import TestClient

# Add project root to path for imports
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from api.main import app
from api.config import settings
from api.utils.cache_manager import CacheManager
from api.utils.logging_config import setup_logging


@pytest.fixture(scope="session")
def test_settings():
    """Test settings configuration"""
    # Override settings for testing
    original_settings = {}
    test_overrides = {
        'debug': True,
        'openai_api_key': 'sk-test-key-for-testing-only',
        'langchain_api_key': 'ls__test-key-for-testing-only',
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 1,  # Use different DB for testing
        'max_concurrency': 2,
        'request_timeout': 30
    }
    
    # Store original values
    for key, value in test_overrides.items():
        if hasattr(settings, key):
            original_settings[key] = getattr(settings, key)
        setattr(settings, key, value)
    
    yield settings
    
    # Restore original values
    for key, value in original_settings.items():
        setattr(settings, key, value)


@pytest.fixture(scope="session")
def test_client(test_settings):
    """FastAPI test client"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    mock_client = Mock(spec=redis.Redis)
    mock_client.ping.return_value = True
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    mock_client.setex.return_value = True
    mock_client.delete.return_value = 1
    mock_client.exists.return_value = False
    mock_client.keys.return_value = []
    mock_client.info.return_value = {
        'redis_version': '7.0.0',
        'connected_clients': 1,
        'used_memory': 1000000,
        'used_memory_human': '1MB',
        'keyspace_hits': 100,
        'keyspace_misses': 10,
        'total_commands_processed': 1000
    }
    return mock_client


@pytest.fixture
def mock_cache_manager(mock_redis):
    """Mock cache manager with Redis mock"""
    with patch('api.utils.cache_manager.redis.Redis', return_value=mock_redis):
        cache_manager = CacheManager()
        cache_manager.redis_client = mock_redis
        cache_manager.cache_enabled = True
        yield cache_manager


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Test response from OpenAI"
    
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def temp_file():
    """Temporary file for testing file operations"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as f:
        f.write("This is test content for file validation")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_document():
    """Sample document data for testing"""
    return {
        "content": "This is a sample document for testing synthetic data generation.",
        "metadata": {
            "title": "Test Document",
            "source": "test_suite",
            "category": "testing"
        }
    }


@pytest.fixture
def sample_generation_request():
    """Sample generation request for testing"""
    return {
        "documents": [
            {
                "content": "This is a test document for generating questions.",
                "metadata": {"title": "Test Doc 1"}
            },
            {
                "content": "Another test document with different content.",
                "metadata": {"title": "Test Doc 2"}
            }
        ],
        "max_iterations": 2,
        "settings": {
            "temperature": 0.7,
            "max_tokens": 500
        }
    }


@pytest.fixture
def sample_evaluation_request():
    """Sample evaluation request for testing"""
    return {
        "evolved_questions": [
            {"id": "q1", "question": "What is the main topic?", "complexity": "simple"},
            {"id": "q2", "question": "How does this relate to other concepts?", "complexity": "complex"}
        ],
        "question_answers": [
            {"question_id": "q1", "answer": "The main topic is testing."},
            {"question_id": "q2", "answer": "It relates through validation processes."}
        ],
        "question_contexts": [
            {"question_id": "q1", "context": "Testing context for question 1"},
            {"question_id": "q2", "context": "Testing context for question 2"}
        ]
    }


@pytest.fixture(scope="session")
def test_logging():
    """Setup test logging configuration"""
    setup_logging(level="DEBUG", use_json=False)
    yield


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing"""
    original_env = {}
    test_env = {
        'OPENAI_API_KEY': 'sk-test-key',
        'LANGCHAIN_API_KEY': 'ls__test-key',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'DEBUG': 'true',
        'ENVIRONMENT': 'testing'
    }
    
    # Store original values and set test values
    for key, value in test_env.items():
        if key in os.environ:
            original_env[key] = os.environ[key]
        os.environ[key] = value
    
    yield test_env
    
    # Restore original environment
    for key in test_env.keys():
        if key in original_env:
            os.environ[key] = original_env[key]
        else:
            os.environ.pop(key, None)


@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing"""
    return {
        'redis_connection_error': redis.ConnectionError("Connection refused"),
        'redis_timeout_error': redis.TimeoutError("Operation timed out"),
        'openai_api_error': Exception("OpenAI API error"),
        'validation_error': ValueError("Invalid input data"),
        'file_not_found': FileNotFoundError("File not found"),
        'permission_error': PermissionError("Access denied")
    }


@pytest.fixture
def performance_test_data():
    """Data for performance testing"""
    return {
        'small_document': "Short test document." * 10,
        'medium_document': "Medium test document." * 100,
        'large_document': "Large test document." * 1000,
        'concurrent_requests': 5,
        'timeout_threshold': 10.0
    }


# Test markers for organizing test types
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests") 
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "redis: Tests requiring Redis")
    config.addinivalue_line("markers", "openai: Tests requiring OpenAI API")
    config.addinivalue_line("markers", "slow: Slow running tests")


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # Reset any global state that might affect tests
    yield
    # Cleanup logic if needed 