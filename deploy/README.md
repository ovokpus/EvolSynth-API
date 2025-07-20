# 🚄 Deploy Folder - Railway Deployment

This folder contains all the configuration files needed to deploy EvolSynth API to Railway.

## 📁 Files Overview

### **Core Configuration**
- **`railway.toml`** - Railway platform configuration and environment variables
- **`start.sh`** - Startup script for the API server (Gunicorn/Uvicorn)
- **`health_check.py`** - Health check script for Railway monitoring

### **Documentation**
- **`RAILWAY_DEPLOYMENT.md`** - Complete deployment guide with troubleshooting
- **`RAILWAY_QUICK_START.md`** - 5-minute deployment checklist
- **`railway.env.example`** - Environment variables template

## 🚀 Quick Deployment

1. Copy this entire folder to your Railway project
2. Set environment variables from `railway.env.example`
3. Railway will automatically use `railway.toml` configuration
4. Deploy! ✨

## 📄 File Details

### `railway.toml`
```toml
[build]
dockerfilePath = "../Dockerfile"  # Points to root Dockerfile
healthcheckPath = "/health"        # API health endpoint
```

### `start.sh`
- Production: Gunicorn with 2 workers
- Development: Uvicorn single worker
- Automatic port binding and Redis connection

### `health_check.py`
- Railway health monitoring
- Checks `/health` endpoint
- Auto-restart on failures

## 🔧 Usage

Railway will automatically:
- ✅ Use `railway.toml` for configuration
- ✅ Execute `start.sh` to launch the API
- ✅ Monitor with `health_check.py`
- ✅ Clear cache on deployment startup

Perfect for Railway deployment! 🚄 