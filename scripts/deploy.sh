#!/bin/bash

# EvolSynth API Deployment Script
# Ensures cache is cleared after deployment

set -e  # Exit on any error

echo "🚀 Starting EvolSynth API deployment..."

# Function to clear cache via API
clear_cache_via_api() {
    local api_url="${1:-http://localhost:8000}"
    echo "🧹 Clearing cache via API..."
    
    # Wait for API to be ready
    echo "⏳ Waiting for API to be ready..."
    for i in {1..30}; do
        if curl -s "$api_url/health" > /dev/null 2>&1; then
            echo "✅ API is ready"
            break
        fi
        echo "   Attempt $i/30: API not ready, waiting 5 seconds..."
        sleep 5
    done
    
    # Clear cache
    response=$(curl -s -X DELETE "$api_url/cache/clear" || echo "failed")
    if [[ "$response" == *"success"* ]]; then
        echo "✅ Cache cleared successfully via API"
        echo "   Response: $response"
    else
        echo "⚠️  Cache clear via API failed or API not available"
        echo "   Response: $response"
    fi
}

# Function to clear cache directly via Redis
clear_cache_via_redis() {
    local redis_host="${REDIS_HOST:-localhost}"
    local redis_port="${REDIS_PORT:-6379}"
    
    echo "🧹 Clearing cache directly via Redis..."
    
    # Check if Redis is available
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h "$redis_host" -p "$redis_port" ping > /dev/null 2>&1; then
            echo "✅ Redis is available, clearing cache..."
            redis-cli -h "$redis_host" -p "$redis_port" FLUSHDB
            echo "✅ Redis cache cleared successfully"
        else
            echo "⚠️  Redis not reachable at $redis_host:$redis_port"
        fi
    else
        echo "⚠️  redis-cli not available, skipping direct Redis cache clear"
    fi
}

# Function to clear cache via Python script
clear_cache_via_python() {
    echo "🧹 Clearing cache via Python..."
    
    python3 -c "
import redis
import sys
try:
    r = redis.Redis(host='${REDIS_HOST:-localhost}', port=${REDIS_PORT:-6379}, db=0)
    r.ping()
    
    # Get all cache prefixes and clear them
    prefixes = ['docs', 'results', 'sessions', 'evolsynth', 'generation']
    total_cleared = 0
    
    for prefix in prefixes:
        keys = r.keys(f'{prefix}:*')
        if keys:
            cleared = r.delete(*keys)
            total_cleared += cleared
            print(f'   Cleared {cleared} keys with prefix: {prefix}')
    
    print(f'✅ Python cache clear: {total_cleared} total keys cleared')
    
except Exception as e:
    print(f'⚠️  Python cache clear failed: {e}')
    sys.exit(1)
" || echo "⚠️  Python cache clear failed"
}

# Parse command line arguments
API_URL="${API_URL:-http://localhost:8000}"
DEPLOYMENT_TYPE="${1:-api}"  # api, docker, kubernetes
CLEAR_CACHE="${CLEAR_CACHE:-true}"

case "$DEPLOYMENT_TYPE" in
    "docker")
        echo "🐳 Docker deployment detected"
        # For Docker deployments, we rely on startup cache clearing
        # But also try to clear via Redis directly
        if [[ "$CLEAR_CACHE" == "true" ]]; then
            clear_cache_via_redis
            clear_cache_via_python
        fi
        ;;
    "kubernetes")
        echo "☸️  Kubernetes deployment detected"
        # For Kubernetes, try multiple methods
        if [[ "$CLEAR_CACHE" == "true" ]]; then
            clear_cache_via_redis
            clear_cache_via_python
            # Wait for pods to be ready, then clear via API
            sleep 10
            clear_cache_via_api "$API_URL"
        fi
        ;;
    "api"|*)
        echo "🌐 API deployment detected"
        # For direct API deployments
        if [[ "$CLEAR_CACHE" == "true" ]]; then
            clear_cache_via_api "$API_URL"
            # Fallback methods
            clear_cache_via_python
            clear_cache_via_redis
        fi
        ;;
esac

echo ""
echo "🎉 EvolSynth API deployment script completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Verify API health: curl $API_URL/health"
echo "   2. Check cache stats: curl $API_URL/cache/stats"
echo "   3. Test generation: Upload documents and generate questions"
echo ""
echo "🔗 Useful endpoints:"
echo "   - Health: $API_URL/health"
echo "   - Docs: $API_URL/docs"
echo "   - Cache Stats: $API_URL/cache/stats"
echo "   - Clear Cache: curl -X DELETE $API_URL/cache/clear" 