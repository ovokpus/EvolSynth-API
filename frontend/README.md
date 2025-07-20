# 🎨 **EvolSynth Frontend**

> **🧭 Navigation**: [🏠 Root](../README.md) | [🚀 API](../api/README.md) | [🚄 Deploy](../deploy/README.md) | [🔀 Branches](../MERGE.md)

A modern, responsive **Next.js frontend** for the EvolSynth synthetic data generation platform. Built with TypeScript, Tailwind CSS, and designed for seamless integration with the FastAPI backend.

## ✨ **Features**

- **📄 Document Upload**: Upload PDF/TXT files or paste text directly
- **⚙️ Advanced Configuration**: Configure evolution levels, temperature, and processing settings
- **🚀 Real-time Generation**: Live progress tracking for synthetic data generation
- **📊 Results Visualization**: Beautiful display of evolved questions, answers, and contexts
- **🎯 Quality Evaluation**: Built-in LLM-as-judge evaluation with detailed scoring
- **🌙 Dark Mode**: Elegant dark blue theme for better UX
- **📱 Responsive Design**: Works perfectly on desktop and mobile
- **⚡ Fast API Integration**: Optimized for Railway backend deployment

## 🛠️ **Recent Updates**

### ✅ **Latest Fixes**
- **📊 Document Count Display**: Fixed bug where results showed "1 Documents Processed" regardless of actual upload count
- **🔗 API Integration**: Enhanced backend-to-frontend data transformation for accurate metrics
- **📈 Results Accuracy**: Improved calculation of processing statistics and document counts

## 🚀 **Quick Start**

### 1. Prerequisites

Make sure you have the EvolSynth backend running:

```bash
# From project root
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should be available at: http://localhost:8000

### 2. Install Dependencies

```bash
cd frontend
npm install
```

### 3. Environment Configuration

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

For production (connecting to Railway):
```env
NEXT_PUBLIC_API_URL=https://evolsynth-api-production.up.railway.app
NODE_ENV=production
```

### 4. Start Frontend

```bash
npm run dev
```

Visit: http://localhost:3000

## 🚄 **Production Deployment to Vercel**

### 📋 **Prerequisites**

✅ **Railway API**: Working at `https://evolsynth-api-production.up.railway.app`  
✅ **Frontend**: Configured to use Railway API  
✅ **Vercel Account**: Required for deployment  

### 🎯 **Quick Deploy Options**

#### Option 1: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ovokpus/EvolSynth-API&project-name=evolsynth-frontend&repository-name=EvolSynth-Frontend)

#### Option 2: Vercel CLI Deploy

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Navigate to frontend directory
cd frontend

# 3. Build and deploy
vercel --prod
```

#### Option 3: Manual Vercel Setup

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

### ⚙️ **Environment Configuration**

The frontend automatically uses the Railway API URL from `vercel.json`:

```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://evolsynth-api-production.up.railway.app"
  }
}
```

### 🧪 **Test Deployment**

After deployment, verify:

1. **Frontend loads**: No 404 errors
2. **API connection**: Health check in UI works
3. **File upload**: PDF/text processing works
4. **Generation**: Synthetic data creation works

### 🔍 **Troubleshooting**

#### Build Errors
```bash
# Clear cache and rebuild
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

#### API Connection Issues
- Verify Railway API is healthy: `curl https://evolsynth-api-production.up.railway.app/health`
- Check CORS settings if needed
- Verify environment variables in Vercel dashboard

#### Performance Optimization
- Images are optimized via Next.js
- API calls are cached
- Static assets are CDN-delivered via Vercel

## 🏗️ **Architecture & Development**

### 📂 **Project Structure**

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx          # Root layout with navigation
│   │   ├── page.tsx            # Main application page
│   │   └── globals.css         # Global styles
│   ├── components/             # React components
│   │   ├── DocumentUpload.tsx  # File upload interface
│   │   ├── GenerationInterface.tsx # Generation settings
│   │   ├── ResultsDisplay.tsx  # Results visualization
│   │   ├── HeroSection.tsx     # Landing section
│   │   ├── Navigation.tsx      # Top navigation
│   │   └── Documentation.tsx   # Embedded docs
│   ├── services/
│   │   └── api.ts              # API client services
│   ├── types/
│   │   └── index.ts            # TypeScript definitions
│   └── lib/
│       └── constants.ts        # App configuration
├── public/                     # Static assets
├── tailwind.config.ts          # Tailwind CSS config
├── next.config.ts              # Next.js configuration
├── vercel.json                 # Vercel deployment config
└── package.json                # Dependencies
```

### 🎨 **UI/UX Features**

- **🌙 Dark Blue Theme**: Professional, easy on the eyes
- **📱 Responsive Design**: Mobile-first approach
- **⚡ Real-time Updates**: Progress tracking during generation
- **🎯 Form Validation**: Client-side validation with clear error messages
- **📊 Data Visualization**: Clean, accessible results display
- **🔄 Loading States**: Smooth loading animations

### 🔧 **API Integration**

The frontend integrates with the FastAPI backend through:

```typescript
// API Configuration
const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'https://evolsynth-api-production.up.railway.app',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
};

// Main API calls
- /health              # Health check
- /generate            # Synthetic data generation
- /evaluate            # Quality evaluation
- /upload/extract-content # File processing
```

### 🛠️ **Development Commands**

```bash
# Development
npm run dev            # Start development server
npm run build          # Build for production
npm run start          # Start production server
npm run lint           # Run ESLint
npm run type-check     # TypeScript check

# Testing
npm run test           # Run tests (if configured)
npm run test:e2e       # End-to-end tests (if configured)
```

### 📦 **Dependencies**

#### Core Dependencies
- **Next.js 15.4.2**: React framework with App Router
- **React 19**: UI library
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling

#### UI Components
- **Lucide React**: Icon library
- **Headless UI**: Accessible components
- **React Hook Form**: Form management

#### API & Utils
- **Axios**: HTTP client (if used)
- **Date-fns**: Date utilities
- **Lodash**: Utility functions

## 🚀 **Expected Results**

### 🌐 **Live URLs**
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://evolsynth-api-production.up.railway.app`

### 📊 **Performance Metrics**
- **First Load**: < 3 seconds
- **API Response**: 3-8 seconds for generation
- **Cache Hit Ratio**: 85-95% for repeated requests
- **Mobile Performance**: Lighthouse score > 90

## 🎊 **Production Ready!**

Your EvolSynth frontend is now:
- ✅ **Deployed**: Vercel global CDN
- ✅ **Optimized**: Auto-scaling and caching
- ✅ **Secure**: HTTPS with security headers
- ✅ **Fast**: Next.js optimizations
- ✅ **Connected**: Railway API integration

---

> **🧭 Navigation**: [🏠 Root](../README.md) | [🚀 API](../api/README.md) | [🚄 Deploy](../deploy/README.md) | [🔀 Branches](../MERGE.md)
