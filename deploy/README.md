# 🚄 **EvolSynth API - Railway Deployment**

> **🧭 Navigation**: [🏠 Root](../README.md) | [🚀 API](../api/README.md) | [🎨 Frontend](../frontend/README.md) | [🔀 Branches](../MERGE.md) | [📋 Changelog](../CHANGELOG.md)

Complete guide for deploying the **EvolSynth API to Railway** with Redis caching, environment configuration, and production optimization.

## 📊 **Current Deployment Status**

| Component | Platform | Status | URL |
|-----------|----------|--------|-----|
| **Backend API** | Railway | ✅ **LIVE** | https://evolsynth-api-production.up.railway.app |
| **Frontend** | Vercel | 🚀 **Ready** | Deploy from `/frontend` folder |
| **Database** | Railway Redis | ✅ **Connected** | Internal Railway network |
| **Documentation** | API Docs | ✅ **Live** | https://evolsynth-api-production.up.railway.app/docs |

## 🛠️ **Recent Fixes & Improvements**

### ✅ **Production Issues Resolved**

| Issue | Fix Applied | Status |
|-------|-------------|--------|
| **Swagger UI Layout Error** | Updated to Swagger UI v5.11.0 with OpenAPI 3.1.0 support | ✅ **Fixed** |
| **Document Count Display** | Fixed frontend calculation to show correct upload count | ✅ **Fixed** |
| **502 Bad Gateway** | Fixed Railway port configuration and Dockerfile | ✅ **Fixed** |
| **Favicon 404 Errors** | Added favicon endpoint to reduce log noise | ✅ **Fixed** |
| **CORS Issues** | Enhanced CORS configuration for Vercel domains | ✅ **Fixed** |

## 🚀 **Quick Setup Overview**

1. **Prerequisites**: Railway account, API keys ready
2. **Redis**: Add Railway Redis service
3. **Deploy**: Connect GitHub repo and deploy
4. **Configure**: Set environment variables
5. **Test**: Verify deployment health

## 📋 **Prerequisites**

### Railway Account
- Sign up at [railway.app](https://railway.app)
- Install Railway CLI (optional): `npm install -g @railway/cli`

### Required API Keys
- **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com)
- **LangChain API Key**: Get from [smith.langchain.com](https://smith.langchain.com)

## 🔧 **Step-by-Step Deployment**

### Step 1: Create New Railway Project

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your EvolSynth API repository
5. Railway will automatically detect the Dockerfile

### Step 2: Add Redis Service

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add Redis"**
3. Railway will create a Redis service with automatic connection variables

### Step 3: Configure Environment Variables

Go to your API service → **"Variables"** tab and add:

#### Required Variables
```bash
# API Keys (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here
LANGCHAIN_API_KEY=your-langchain-api-key-here

# Railway Configuration
ENVIRONMENT=production
```

#### Optional Variables
```bash
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=EvolSynth-API

# Performance Settings
MAX_CONCURRENCY=12
REQUEST_TIMEOUT=300
WORKERS=2

# LLM Settings
DEFAULT_MODEL=gpt-4o-mini
EVALUATION_MODEL=gpt-4o-mini
TEMPERATURE=0.7

# Cache Settings
CACHE_ENABLED=true
CACHE_TTL=3600
```

### Step 4: Redis Connection (Automatic)

Railway automatically provides Redis connection variables:
- `REDIS_HOST` - Internal Redis hostname
- `REDIS_PORT` - Redis port (6379)
- `REDIS_URL` - Complete Redis connection URL

**No manual configuration needed!** ✅

### Step 5: Deploy and Verify

1. Click **"Deploy"** in Railway dashboard
2. Monitor build logs for any errors
3. Wait for deployment to complete (2-3 minutes)
4. Test health endpoint: `https://your-app.up.railway.app/health`

## 🎉 **What Was Fixed in Recent Deployments**

### 🚨 **Railway 502 Error → RESOLVED**
- **Issue**: Port binding mismatch between app and Railway
- **Fix**: Updated `deploy/start.sh` to properly handle Railway's dynamic PORT
- **Result**: API now responds with 200 OK

### 🔗 **Frontend Integration → COMPLETE**
- **Updated**: `frontend/src/lib/constants.ts` to use Railway API
- **Added**: `frontend/vercel.json` for production deployment
- **Tested**: Build successful, ready for Vercel

### 🧹 **Cache Management → ACTIVE**
- **Added**: Automatic cache clearing on deployment
- **Configured**: Redis cache with fallback
- **Status**: Cache cleared after every fix

### 🚨 **HEAD/OPTIONS Request Support → FIXED**
- **Issue**: 405 errors for HEAD requests, 400 errors for OPTIONS preflight
- **Fix**: Added HEAD method support and proper CORS configuration
- **Result**: Health checkers and frontend now work correctly

## 🚀 **Architecture Overview**

```
[User] → [Vercel Frontend] → [Railway API] → [Railway Redis]
                                   ↓
                            [OpenAI/LangChain]
```

## ✅ **Health Check Results**

Expected healthy response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "openai": "connected",
    "langsmith": "connected", 
    "evol_instruct_service": "running",
    "evaluation_service": "running",
    "document_service": "running",
    "redis_cache": "connected"
  }
}
```

## 📂 **Deployment Files Overview**

This folder contains all Railway deployment configuration:

### Core Files
- **`start.sh`**: Railway startup script with environment validation
- **`health_check.py`**: Health check script for Railway monitoring
- **`railway.toml`**: Railway service configuration
- **`railway.env.example`**: Example environment variables

### Configuration Details

#### `start.sh` Features:
- ✅ Dynamic PORT handling for Railway
- ✅ Environment variable validation
- ✅ Graceful error handling
- ✅ Production-optimized Gunicorn startup
- ✅ Debug logging for troubleshooting

#### `railway.toml` Configuration:
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "./start.sh"
healthcheckPath = "/health"
healthcheckTimeout = 300
```

## 🔧 **Advanced Configuration**

### Environment Variables Reference

#### Core Settings
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | OpenAI API access |
| `LANGCHAIN_API_KEY` | ⚠️ Recommended | - | LangSmith tracing |
| `ENVIRONMENT` | No | `production` | Runtime environment |

#### Performance Settings
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MAX_CONCURRENCY` | No | `8` | Max concurrent operations |
| `REQUEST_TIMEOUT` | No | `300` | Request timeout (seconds) |
| `WORKERS` | No | `2` | Gunicorn worker processes |

#### LLM Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEFAULT_MODEL` | No | `gpt-4o-mini` | Primary LLM model |
| `EVALUATION_MODEL` | No | `gpt-4o-mini` | Evaluation LLM model |
| `TEMPERATURE` | No | `0.7` | LLM creativity setting |

#### Cache Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CACHE_ENABLED` | No | `true` | Enable Redis caching |
| `CACHE_TTL` | No | `3600` | Cache time-to-live (seconds) |
| `REDIS_HOST` | Auto | Railway | Redis hostname |
| `REDIS_PORT` | Auto | Railway | Redis port |

### Performance Optimization

#### High-Performance Setup
```bash
# Environment variables for maximum performance
MAX_CONCURRENCY=15
WORKERS=4
REQUEST_TIMEOUT=600
BATCH_SIZE=10

# Redis optimization
CACHE_TTL=7200
DOCUMENT_CACHE_TTL=14400
RESULT_CACHE_TTL=3600

# LLM optimization
LLM_REQUEST_TIMEOUT=60
LLM_MAX_RETRIES=3
ENABLE_LLM_BATCHING=true
```

## 🔍 **Troubleshooting**

### Common Issues & Solutions

#### 1. **502 Bad Gateway**
```bash
# Check if port is properly configured
# Solution: Ensure start.sh handles $PORT correctly
export PORT=${PORT:-8000}
exec gunicorn api.main:app --bind 0.0.0.0:${PORT}
```

#### 2. **Environment Variables Not Found**
```bash
# Check Railway dashboard → Variables tab
# Ensure required variables are set:
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=...
```

#### 3. **Redis Connection Issues**
```bash
# Railway provides these automatically:
REDIS_HOST=redis.railway.internal
REDIS_PORT=6379
# No manual configuration needed
```

#### 4. **Build Failures**
```bash
# Check Dockerfile validity
docker build -t evolsynth-test .

# Verify requirements.txt
pip install -r requirements.txt
```

#### 5. **Application Crashes**
```bash
# Check Railway logs for:
# - Missing environment variables
# - Port binding issues
# - Dependency errors
```

### Health Check Commands

```bash
# Test Railway deployment
curl https://your-app.up.railway.app/health

# Expected response
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z"
}

# Test specific endpoints
curl https://your-app.up.railway.app/docs
curl https://your-app.up.railway.app/cache/stats
curl https://your-app.up.railway.app/metrics/performance
```

## 🧹 **Cache Management**

### Automatic Cache Clearing

The API automatically clears cache on:
- ✅ **Application startup** (fresh deployments)
- ✅ **Manual trigger** via `/cache/clear` endpoint
- ✅ **After deployment fixes** (configurable)

### Cache Statistics

Monitor cache performance:

```bash
# Get cache statistics
curl https://your-app.up.railway.app/cache/stats

# Expected response
{
  "cache_type": "redis",
  "cache_enabled": true,
  "total_keys": 145,
  "memory_usage": "2.4MB",
  "hit_ratio": 0.87,
  "health": "connected"
}
```

### Manual Cache Management

```bash
# Clear all cache
curl -X DELETE https://your-app.up.railway.app/cache/clear

# Clear specific prefixes
curl -X DELETE https://your-app.up.railway.app/cache/clear?prefix=docs
curl -X DELETE https://your-app.up.railway.app/cache/clear?prefix=generation
```

### Cache Configuration

Optimize cache performance:

```bash
# Environment variables
CACHE_ENABLED=true
CACHE_TTL=3600                    # General cache: 1 hour
DOCUMENT_CACHE_TTL=7200          # Documents: 2 hours  
RESULT_CACHE_TTL=3600            # Results: 1 hour

# Redis settings (auto-configured by Railway)
REDIS_HOST=redis.railway.internal
REDIS_PORT=6379
REDIS_DB=0
```

## 📈 **Monitoring & Performance**

### Performance Metrics

Monitor real-time performance:

```bash
# Performance dashboard
curl https://your-app.up.railway.app/metrics/performance

# Response example
{
  "current_requests": 3,
  "total_requests": 1547,
  "avg_response_time": 2.3,
  "cache_hit_ratio": 0.89,
  "uptime_seconds": 86400
}
```

### Health Monitoring

```bash
# Basic health check
curl https://your-app.up.railway.app/health

# Detailed health check
curl https://your-app.up.railway.app/health/detailed

# Summary for monitoring systems
curl https://your-app.up.railway.app/health/summary
```

### Expected Performance

| Metric | Target | Description |
|--------|--------|-------------|
| **Response Time** | < 8s | API generation requests |
| **Cache Hit Ratio** | > 85% | Repeated request optimization |
| **Uptime** | > 99.5% | Service availability |
| **Memory Usage** | < 500MB | Resource efficiency |
| **Error Rate** | < 1% | Request success rate |

## 🎯 **Next Steps**

After successful Railway deployment:

1. **Deploy Frontend**: Follow `/frontend/README.md` for Vercel deployment
2. **Test End-to-End**: Upload documents → Generate data
3. **Monitor Performance**: Use built-in health checks and logs
4. **Scale**: Railway auto-scales based on traffic

## 💡 **Key Learnings**

- ✅ Railway requires dynamic PORT handling
- ✅ Frontend environment configuration crucial
- ✅ Cache clearing improves user experience
- ✅ Health checks essential for monitoring
- ✅ Proper CORS configuration prevents frontend issues

## 🔗 **Useful Links**

- **API Health**: https://evolsynth-api-production.up.railway.app/health
- **API Docs**: https://evolsynth-api-production.up.railway.app/docs
- **Railway Dashboard**: Your Railway project dashboard
- **Performance Metrics**: https://evolsynth-api-production.up.railway.app/metrics/performance

---

## 🎊 **Congratulations!**

Your **EvolSynth API is now production-ready on Railway!**

- ✅ **Deployed**: Railway with auto-scaling
- ✅ **Cached**: Redis for optimal performance  
- ✅ **Monitored**: Health checks and metrics
- ✅ **Optimized**: Production configuration
- ✅ **Ready**: For frontend integration

---

> **🧭 Navigation**: [🏠 Root](../README.md) | [🚀 API](../api/README.md) | [🎨 Frontend](../frontend/README.md) | [🔀 Branches](../MERGE.md) 