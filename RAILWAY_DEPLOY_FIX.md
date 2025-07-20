# 🔧 Railway Deployment Fix Guide

## ❌ Current Issue: 502 Application Failed to Respond

**Root Cause**: Missing environment variables causing startup crashes

## ✅ Solution: Set Required Environment Variables

### **Step 1: Go to Railway Dashboard**
1. Open [railway.app](https://railway.app)
2. Go to your project: **hospitable-joy**
3. Click on **EvolSynth-API** service (not Redis)
4. Click **"Variables"** tab

### **Step 2: Add Required Variables**

**CRITICAL - Add these 2 variables:**

```bash
Variable Name: OPENAI_API_KEY
Variable Value: sk-your-actual-openai-api-key-here
```

```bash
Variable Name: LANGCHAIN_API_KEY  
Variable Value: your-actual-langchain-api-key-here
```

### **Step 3: Add Redis Variables (Optional but Recommended)**

If you have a Redis service in Railway, add these:

```bash
Variable Name: REDIS_HOST
Variable Value: ${{Redis.RAILWAY_PRIVATE_DOMAIN}}
```

```bash
Variable Name: REDIS_PORT
Variable Value: ${{Redis.RAILWAY_TCP_PROXY_PORT}}
```

```bash
Variable Name: REDIS_PASSWORD
Variable Value: ${{Redis.REDIS_PASSWORD}}
```

### **Step 4: Deploy and Test**

1. **Save the variables** - Railway will auto-redeploy
2. **Wait 2-3 minutes** for deployment to complete
3. **Test the API**:
   ```bash
   curl https://evolsynth-api-production.up.railway.app/health
   ```

### **Expected Result After Fix:**

**Before (502 error):**
```json
{"status":"error","code":502,"message":"Application failed to respond"}
```

**After (working):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "openai": "connected",
    "redis_cache": "connected"
  }
}
```

## 🔍 Debug Information

### **Startup Validation Added**
The startup script now validates:
- ✅ `OPENAI_API_KEY` is required (will fail if missing)
- ⚠️ `LANGCHAIN_API_KEY` warning if missing (optional)

### **Railway Logs Will Show:**
```
🚀 Starting EvolSynth API on Railway
Port: 8080
Environment: production
Redis: redis.railway.internal:6379
✅ Environment validation passed
🔧 Starting with Gunicorn for Railway
```

## 🚨 If Still Not Working

1. **Check Railway Logs** for error messages
2. **Verify API keys** are valid and active
3. **Ensure Redis service** is running in Railway
4. **Contact support** if deployment logs show other errors

**Once working, we'll wire it into your frontend for Vercel deployment!** 🚀 