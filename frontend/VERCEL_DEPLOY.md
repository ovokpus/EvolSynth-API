# 🚀 **Deploy EvolSynth Frontend to Vercel**

## 📋 **Prerequisites**

✅ **Railway API**: Working at `https://evolsynth-api-production.up.railway.app`  
✅ **Frontend**: Configured to use Railway API  
✅ **Vercel Account**: Required for deployment  

## 🎯 **Quick Deploy**

### Option 1: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ovokpus/EvolSynth-API&project-name=evolsynth-frontend&repository-name=EvolSynth-Frontend)

### Option 2: Manual Deploy

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Navigate to frontend directory
cd frontend

# 3. Build and deploy
vercel --prod
```

## ⚙️ **Environment Configuration**

Vercel will automatically use the Railway API URL from `vercel.json`:

```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://evolsynth-api-production.up.railway.app"
  }
}
```

## 🔧 **Manual Vercel Setup**

1. **Connect Repository**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Select the `frontend` folder as root directory

2. **Configure Build**:
   - **Framework**: Next.js (auto-detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install`

3. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://evolsynth-api-production.up.railway.app
   ```

4. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes for build
   - Get your live URL!

## 🎊 **Expected Result**

🌐 **Live URLs**:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://evolsynth-api-production.up.railway.app`

## 🧪 **Test Deployment**

After deployment, verify:

1. **Frontend loads**: No 404 errors
2. **API connection**: Health check in UI works
3. **File upload**: PDF/text processing works
4. **Generation**: Synthetic data creation works

## 🔍 **Troubleshooting**

### Build Errors
```bash
# Clear cache and rebuild
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### API Connection Issues
- Verify Railway API is healthy: `curl https://evolsynth-api-production.up.railway.app/health`
- Check CORS settings if needed
- Verify environment variables in Vercel dashboard

### Performance Optimization
- Images are optimized via Next.js
- API calls are cached
- Static assets are CDN-delivered via Vercel

## 🚀 **Ready for Production!**

Your EvolSynth app is now:
- ✅ **Backend**: Railway (scalable, Redis-cached)
- ✅ **Frontend**: Vercel (global CDN, auto-scaling)
- ✅ **Database**: Redis on Railway
- ✅ **Monitoring**: Built-in health checks

**Perfect production setup!** 🎉 