# 🚄 Railway Deployment Guide for EvolSynth API

This guide provides step-by-step instructions for deploying the EvolSynth API to Railway.

## 🚀 Quick Setup Overview

1. **Prerequisites**: Railway account, API keys ready
2. **Redis**: Add Railway Redis service
3. **Deploy**: Connect GitHub repo and deploy
4. **Configure**: Set environment variables
5. **Test**: Verify deployment health

## 📋 Prerequisites

### Railway Account
- Sign up at [railway.app](https://railway.app)
- Install Railway CLI (optional): `npm install -g @railway/cli`

### Required API Keys
- **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com)
- **LangChain API Key**: Get from [smith.langchain.com](https://smith.langchain.com)

## 🔧 Step-by-Step Deployment

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
WORKERS=2
MAX_CONCURRENCY=8
REQUEST_TIMEOUT=120
```

#### Redis Variables (Auto-configured)
Railway automatically provides these when you add Redis service:
```bash
REDIS_HOST=${{Redis.RAILWAY_PRIVATE_DOMAIN}}
REDIS_PORT=${{Redis.RAILWAY_TCP_PROXY_PORT}}
REDIS_PASSWORD=${{Redis.REDIS_PASSWORD}}
REDIS_URL=${{Redis.REDIS_URL}}
```

#### Optional Optimizations
```bash
# Performance
MAX_TOKENS=500
BATCH_SIZE=4
LLM_REQUEST_TIMEOUT=60

# Caching
CACHE_ENABLED=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=EvolSynth-Railway
```

### Step 4: Deploy

1. Railway will automatically deploy after you set environment variables
2. Monitor the deployment in the **"Deployments"** tab
3. Watch build logs for any issues
4. First deployment takes 5-10 minutes

### Step 5: Verify Deployment

Once deployed, test your API:

```bash
# Get your Railway domain from the dashboard
curl https://your-app-name.railway.app/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "openai": "connected",
    "redis_cache": "connected",
    "cache_type": "redis"
  }
}
```

## 🔗 Railway-Specific Features

### Automatic Domain
Railway provides a free domain: `https://your-app-name.railway.app`

### Custom Domain (Optional)
1. Go to **"Settings"** → **"Domains"**
2. Add your custom domain
3. Configure DNS records as shown

### Environment-Specific Deployments
Railway supports multiple environments:
```bash
# Production (default)
ENVIRONMENT=production

# Staging
ENVIRONMENT=staging
```

## 📊 Monitoring & Logs

### Real-time Logs
1. Railway dashboard → **"Logs"** tab
2. Filter by service (API, Redis)
3. Search for specific events

### Health Monitoring
```bash
# Built-in health check
GET /health

# Cache statistics
GET /cache/stats

# Performance metrics
GET /metrics/performance
```

### Metrics Dashboard
Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network traffic
- Response times

## 🛠️ Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check build logs in Railway dashboard
# Common causes:
# 1. Missing environment variables
# 2. Dependencies installation errors
# 3. Docker build issues
```

#### Redis Connection Issues
```bash
# Verify Redis service is running
# Check environment variables are set
# Restart both services if needed
```

#### API Key Issues
```bash
# Verify API keys are correctly set
# Check for extra spaces or quotes
# Test keys independently
```

### Debug Commands

#### Check Environment Variables
```bash
# In Railway logs, look for startup output:
🚀 Starting EvolSynth API on Railway
Port: 8000
Environment: production
Redis: redis.railway.internal:6379
```

#### Test Redis Connection
```bash
# Check cache stats endpoint
curl https://your-app-name.railway.app/cache/stats
```

#### Verify API Keys
```bash
# Health endpoint will show connection status
curl https://your-app-name.railway.app/health
```

## 🔄 Updates & Redeployments

### Automatic Deployments
Railway automatically redeploys when you:
1. Push to your connected GitHub branch
2. Update environment variables
3. Change Railway configuration

### Manual Redeploy
1. Railway dashboard → **"Deployments"** tab
2. Click **"Redeploy"** on any previous deployment

### Cache Clearing on Deploy
The API automatically clears cache on startup, ensuring fresh deployments.

## 💰 Railway Pricing

### Hobby Plan (Free)
- $5 credit monthly
- Perfect for development/testing
- Includes database services

### Pro Plan ($20/month)
- $20 credit monthly + usage
- Better for production workloads
- Priority support

### Resource Usage
EvolSynth API typically uses:
- **CPU**: 0.1-0.5 vCPU
- **Memory**: 512MB-1GB
- **Storage**: Minimal (logs only)
- **Redis**: 50-200MB depending on cache

## 🔧 Performance Optimization

### Railway-Specific Optimizations

#### Resource Limits
```bash
# Optimized for Railway limits
WORKERS=2  # Don't exceed 4 workers
MAX_CONCURRENCY=8  # Railway memory limits
BATCH_SIZE=4  # Smaller batches for stability
```

#### Cold Start Optimization
```bash
# Keep service warm with health checks
# Railway automatically handles this
```

#### Cache Configuration
```bash
# Optimized cache settings for Railway Redis
CACHE_TTL=3600  # 1 hour
DOCUMENT_CACHE_TTL=7200  # 2 hours
```

## 🛡️ Security Best Practices

### Environment Variables
- Never commit API keys to git
- Use Railway's variable management
- Rotate keys regularly

### CORS Configuration
```bash
# For production, specify your frontend domain
ALLOWED_ORIGINS=https://your-frontend-domain.com

# For development, you can use wildcard
ALLOWED_ORIGINS=*
```

### Rate Limiting
```bash
# Enable rate limiting for production
RATE_LIMIT_ENABLED=true
```

## 📚 Useful Railway Commands

### CLI Commands (if Railway CLI installed)
```bash
# Login to Railway
railway login

# Link to existing project
railway link

# View logs
railway logs

# Add environment variable
railway variables set OPENAI_API_KEY=sk-...

# Deploy from CLI
railway up
```

## 🎯 Post-Deployment Checklist

- [ ] ✅ API health check passes
- [ ] ✅ Redis connection working
- [ ] ✅ OpenAI API key configured
- [ ] ✅ LangChain tracing enabled (optional)
- [ ] ✅ Cache statistics accessible
- [ ] ✅ Test document upload and generation
- [ ] ✅ Monitor logs for errors
- [ ] ✅ Set up custom domain (if needed)
- [ ] ✅ Configure frontend to use Railway URL

## 🔗 Important URLs

After deployment, bookmark these:
- **API Health**: `https://your-app-name.railway.app/health`
- **API Docs**: `https://your-app-name.railway.app/docs`
- **Cache Stats**: `https://your-app-name.railway.app/cache/stats`
- **Railway Dashboard**: `https://railway.app/project/your-project-id`

## 🆘 Support

### Railway Support
- Documentation: [docs.railway.app](https://docs.railway.app)
- Discord: [Railway Discord](https://discord.gg/railway)
- GitHub: [railway/railway](https://github.com/railway/railway)

### EvolSynth API Issues
- Check logs in Railway dashboard
- Verify environment variables
- Test health endpoints
- Review deployment logs

**Happy deploying! 🚄✨** 