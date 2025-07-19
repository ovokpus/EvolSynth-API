#!/usr/bin/env python3
"""
Simple Redis Connection Test for EvolSynth
Tests the containerized Redis connection and basic operations
"""

import time
from datetime import datetime

def test_redis_connection():
    """Test basic Redis connection and operations"""
    
    print("🔧 Testing Redis Connection...")
    print("=" * 50)
    
    try:
        import redis
        print("✅ Redis package is available")
    except ImportError:
        print("❌ Redis package not installed. Run: pip install redis")
        return False
    
    try:
        # Connect to Redis container
        client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connection
        response = client.ping()
        if response:
            print("✅ Redis connection successful")
        else:
            print("❌ Redis ping failed")
            return False
        
        # Test basic operations
        print("\n🧪 Testing basic operations...")
        
        # Set a test key
        test_key = "evolsynth:test"
        test_value = f"test_value_{int(time.time())}"
        
        client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
        print(f"✅ SET operation successful: {test_key} = {test_value}")
        
        # Get the test key
        retrieved_value = client.get(test_key)
        if retrieved_value == test_value:
            print(f"✅ GET operation successful: {retrieved_value}")
        else:
            print(f"❌ GET operation failed: expected {test_value}, got {retrieved_value}")
            return False
        
        # Test key expiration
        ttl = client.ttl(test_key)
        print(f"✅ TTL check successful: {ttl} seconds remaining")
        
        # Test cache simulation
        print("\n💾 Testing cache simulation...")
        
        cache_key = "evolsynth:cache:test"
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "test_data": "This is cached data",
            "version": "1.0"
        }
        
        # Store JSON data
        import json
        client.setex(cache_key, 300, json.dumps(cache_data))  # 5 minute expiry
        print("✅ Cache SET successful")
        
        # Retrieve JSON data
        cached_result = client.get(cache_key)
        if cached_result:
            parsed_data = json.loads(cached_result)
            print(f"✅ Cache GET successful: {parsed_data['test_data']}")
        else:
            print("❌ Cache GET failed")
            return False
        
        # Clean up test keys
        client.delete(test_key, cache_key)
        print("✅ Cleanup successful")
        
        # Test Redis info
        print("\n📊 Redis Server Info:")
        info = client.info()
        print(f"  Redis Version: {info.get('redis_version', 'unknown')}")
        print(f"  Memory Used: {info.get('used_memory_human', 'unknown')}")
        print(f"  Connected Clients: {info.get('connected_clients', 0)}")
        print(f"  Total Commands: {info.get('total_commands_processed', 0)}")
        
        print("\n🎉 All Redis tests passed successfully!")
        print("   Your Redis container is ready for EvolSynth optimization!")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection error: {e}")
        print("   Make sure Redis container is running: docker compose up redis -d")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_performance_config():
    """Test if performance configuration is available"""
    
    print("\n🔧 Testing Performance Configuration...")
    print("=" * 50)
    
    try:
        from api.performance_optimization_config import (
            PerformanceConfig, 
            OptimizationLevel, 
            get_optimization_config,
            performance_monitor
        )
        print("✅ Performance configuration is available")
        
        # Test configuration loading
        config = get_optimization_config(OptimizationLevel.DEVELOPMENT)
        print(f"✅ Configuration loaded: {config.max_concurrent_requests} max requests")
        
        # Test performance monitor
        performance_monitor.record_request(0.5, True)
        metrics = performance_monitor.get_current_metrics()
        print(f"✅ Performance monitoring working: {metrics}")
        
        return True
        
    except ImportError as e:
        print(f"⚠️  Performance config not available: {e}")
        return False


if __name__ == "__main__":
    print("🚀 EvolSynth Redis & Performance Test")
    print("====================================")
    
    # Test Redis
    redis_ok = test_redis_connection()
    
    # Test Performance Config
    perf_ok = test_performance_config()
    
    print("\n📋 Test Summary:")
    print("================")
    print(f"Redis Connection: {'✅ PASS' if redis_ok else '❌ FAIL'}")
    print(f"Performance Config: {'✅ PASS' if perf_ok else '⚠️  NOT AVAILABLE'}")
    
    if redis_ok:
        print("\n🎯 Next Steps:")
        print("1. Install performance packages: pip install -r requirements-performance.txt")
        print("2. Update .env with settings from env.performance.example")
        print("3. Start optimized backend: python api/main_optimized.py")
    else:
        print("\n🔧 Fix Required:")
        print("1. Ensure Redis container is running: docker compose up redis -d")
        print("2. Install Redis package: pip install redis")
        print("3. Check network connectivity to localhost:6379") 