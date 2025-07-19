# 🚄 Railway Quick Start - EvolSynth API

## ⚡ 5-Minute Deployment

### 1. Create Railway Project
- Go to [railway.app/dashboard](https://railway.app/dashboard)
- Click **"New Project"** → **"Deploy from GitHub repo"**
- Select your EvolSynth API repository

### 2. Add Redis Service
- In project dashboard: **"+ New"** → **"Database"** → **"Add Redis"**

### 3. Set Environment Variables
In your API service → **"Variables"** tab, add these **REQUIRED** variables:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
LANGCHAIN_API_KEY=your-langchain-api-key-here
ENVIRONMENT=production
WORKERS=2
```

**Redis variables are automatically set by Railway when you add Redis service.**

### 4. Deploy & Test
- Railway auto-deploys after setting variables
- Test: `curl https://your-app-name.railway.app/health`

## 🎯 Quick Checklist

- [ ] ✅ Railway account created
- [ ] ✅ GitHub repo connected
- [ ] ✅ Redis service added  
- [ ] ✅ API keys configured
- [ ] ✅ Deployment successful
- [ ] ✅ Health check passes

## 🔗 Key URLs After Deployment
- **API Health**: `https://your-app-name.railway.app/health`
- **API Docs**: `https://your-app-name.railway.app/docs`
- **Railway Dashboard**: Check your project page

## 🚨 Common Issues
1. **Build fails**: Check API keys are set correctly
2. **Redis connection fails**: Ensure Redis service is added
3. **Timeout**: Railway first deploy takes 5-10 minutes

## 📚 Full Guide
See `RAILWAY_DEPLOYMENT.md` for comprehensive deployment guide.

**That's it! Your API should be live on Railway! 🎉** 