# 🧹 Automatic Cache Clearing on Deployment

This document explains how EvolSynth API automatically clears cache after deployments to ensure fresh, updated functionality.

## 🚀 Automatic Cache Clearing

### 1. **Startup Cache Clearing**
The API automatically clears all cache entries when it starts up:

```python
# In api/main.py startup event
if CACHE_AVAILABLE:
    # Clear all cache prefixes on startup
    cleared_total = clear_all_cache_prefixes()
    print(f"🧹 Deployment cache clear: {cleared_total} entries removed")
```

**Cache prefixes cleared:**
- `docs:*` - Document processing cache
- `results:*` - API response cache  
- `sessions:*` - Session data cache
- `evolsynth:*` - Service-level cache
- `generation:*` - Generation request cache

### 2. **Deployment Script**
Use the provided deployment script for comprehensive cache clearing:

```bash
# Basic usage
./scripts/deploy.sh

# Docker deployment
./scripts/deploy.sh docker

# Kubernetes deployment  
./scripts/deploy.sh kubernetes

# Custom API URL
API_URL=https://api.yourdomain.com ./scripts/deploy.sh
```

The script provides **multiple fallback methods**:
1. ✅ **API endpoint** - `/cache/clear` 
2. ✅ **Direct Redis** - `redis-cli FLUSHDB`
3. ✅ **Python script** - Direct Redis connection

## 🐳 Docker Deployments

### Docker Compose
```yaml
services:
  evolsynth-api:
    # ... configuration ...
    depends_on:
      redis:
        condition: service_healthy
```

**Cache clearing happens:**
1. **Automatically** on container startup
2. **Via deployment script** if run manually

### Manual Docker Commands
```bash
# Start services
docker-compose up -d

# Clear cache manually (if needed)
docker-compose exec evolsynth-api python -c "
import redis; 
r = redis.Redis(host='redis', port=6379); 
r.flushdb(); 
print('Cache cleared')
"
```

## ☸️ Kubernetes Deployments

### Cache Clearing Strategy
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: clear-cache-job
spec:
  template:
    spec:
      containers:
      - name: cache-clearer
        image: redis:alpine
        command: ['redis-cli']
        args: ['-h', 'redis-service', 'FLUSHDB']
      restartPolicy: Never
```

**Or use the deployment script:**
```bash
# After deploying to Kubernetes
kubectl port-forward service/evolsynth-api 8000:8000 &
./scripts/deploy.sh kubernetes
```

## 🔧 Manual Cache Clearing

### Via API Endpoint
```bash
# Clear all cache entries
curl -X DELETE http://localhost:8000/cache/clear

# Check cache stats
curl http://localhost:8000/cache/stats
```

### Direct Redis Access
```bash
# Connect to Redis
redis-cli -h localhost -p 6379

# Clear specific prefixes
EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "evolsynth:*"

# Clear entire database
FLUSHDB
```

### Python Script
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Clear all cache prefixes
prefixes = ['docs', 'results', 'sessions', 'evolsynth', 'generation']
for prefix in prefixes:
    keys = r.keys(f'{prefix}:*')
    if keys:
        r.delete(*keys)
        print(f'Cleared {len(keys)} keys with prefix: {prefix}')
```

## 🎯 Why Cache Clearing is Important

### Problem Prevention
- ✅ **Prevents stale context rendering** from old code
- ✅ **Ensures new features work correctly** 
- ✅ **Avoids cache hits with outdated data structures**
- ✅ **Guarantees fresh testing after deployments**

### Before Cache Clearing
```bash
# User reports: Still getting "[object Object]" in context
🚀 Using FAST mode for generation
🎯 Cache hit! Returning cached result  # ← OLD CACHED DATA!
```

### After Cache Clearing
```bash
# Fresh generation with fixed code
🚀 Using FAST mode for generation
💾 No cache hit, generating fresh result
✅ Context: "Machine Learning Concepts - This document discusses..."
```

## 📊 Monitoring Cache Clearing

### Startup Logs
```bash
🚀 Starting EvolSynth API initialization...
✅ Cache system: redis (enabled: True)
🧹 Deployment cache clear: 15 entries removed
✅ Core services initialized
```

### Deployment Script Output
```bash
🚀 Starting EvolSynth API deployment...
🧹 Clearing cache via API...
✅ Cache cleared successfully via API
   Response: {"success":true,"cleared_entries":{"total":15}}
🎉 EvolSynth API deployment script completed!
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Deploy and Clear Cache
  run: |
    # Deploy application
    docker-compose up -d
    
    # Clear cache using deployment script
    ./scripts/deploy.sh docker
    
    # Verify deployment
    curl -f http://localhost:8000/health
```

### Jenkins Pipeline
```groovy
stage('Deploy') {
    steps {
        sh 'docker-compose up -d'
        sh './scripts/deploy.sh docker'
        sh 'curl -f http://localhost:8000/health'
    }
}
```

## 🚨 Troubleshooting

### Cache Clear Failures
```bash
# Check Redis connectivity
redis-cli ping

# Check API health
curl http://localhost:8000/health

# Manual Python clear as fallback
python3 -c "import redis; redis.Redis().flushdb()"
```

### Common Issues
1. **Redis not available** → API will use memory cache (cleared on restart)
2. **API not ready** → Use Redis direct access methods
3. **Permission errors** → Ensure deployment script is executable

## 📝 Summary

**Cache clearing happens automatically on:**
- ✅ Every API startup/restart
- ✅ Every deployment (if using deployment script)  
- ✅ Manual cache clear requests

**This ensures:**
- ✅ Fresh functionality after code updates
- ✅ No stale cache interfering with new features
- ✅ Consistent behavior for all users
- ✅ Proper testing of new deployments 