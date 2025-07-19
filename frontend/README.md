# 🎨 EvolSynth Frontend

A modern, responsive Next.js frontend for the EvolSynth synthetic data generation platform. Built with TypeScript, Tailwind CSS, and designed for seamless integration with the FastAPI backend.

## ✨ Features

- **📄 Document Upload**: Upload PDF/TXT files or paste text directly
- **⚙️ Advanced Configuration**: Configure evolution levels, temperature, and processing settings
- **🚀 Real-time Generation**: Live progress tracking for synthetic data generation
- **📊 Results Visualization**: Beautiful display of evolved questions, answers, and contexts
- **🎯 Quality Evaluation**: Built-in LLM-as-judge evaluation with detailed scoring
- **🌙 Dark Mode**: Elegant dark blue theme for better UX
- **📱 Responsive Design**: Works perfectly on desktop and mobile

## 🚀 Quick Start

### 1. Prerequisites

Make sure you have the EvolSynth backend running:

```bash
# From project root
cd api
python start_optimized.py
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

### 4. Start Frontend

```bash
npm run dev
```

Visit: http://localhost:3000

## 🔗 Backend Integration

### 🎯 Current Status
✅ **Frontend is now fully connected to your FastAPI backend!**

The frontend makes real API calls to:
- `POST /generate` - Generate synthetic data using Evol-Instruct
- `POST /evaluate` - Evaluate question quality with LLM-as-judge  
- `GET /health` - Check backend status and dependencies

### 🧪 Testing the Integration

1. **Upload Documents** - Upload PDF/TXT files or paste text
2. **Configure Settings** - Set evolution levels, temperature, execution mode
3. **Generate Data** - Click "Start Generation" and watch real-time progress
4. **View Results** - See actual evolved questions and answers from your backend
5. **Check Network Tab** - Verify real API calls to `/generate` endpoint

### 🔍 Backend Health Check

Visit: http://localhost:8000/health

Should return:
```json
{
  "status": "healthy", 
  "version": "1.0.0-optimized",
  "dependencies": {
    "openai": "connected",
    "langsmith": "connected",
    "redis_cache": "connected",
    "optimized_service": true
  }
}
```

### 📊 Data Flow

```
Frontend Upload Component
    ↓ (UploadedDocument[])
API Service Conversion  
    ↓ (DocumentInput[])
FastAPI /generate Endpoint
    ↓ (GenerationResponse)
Backend Processing (LangGraph + Evol-Instruct + Redis Caching)
    ↓ (EvolvedQuestion[], QuestionAnswer[], etc.)
Frontend Results Display
```

## 🛠️ Development

### Project Structure

```
frontend/
├── app/
│   ├── page.tsx                 # Main application page
│   ├── layout.tsx              # Root layout with global styles
│   └── globals.css             # Global styles and Tailwind
├── components/
│   ├── DocumentUpload.tsx      # File upload and text input
│   ├── GenerationSettings.tsx  # Configuration interface
│   ├── ProgressDisplay.tsx     # Real-time progress tracking
│   └── ResultsDisplay.tsx      # Results visualization
├── types/
│   └── api.ts                  # TypeScript types matching FastAPI models
├── services/
│   └── api.ts                  # HTTP client for backend communication
└── public/                     # Static assets
```

### Key Technologies

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first styling
- **React Hooks** - State management and effects
- **Fetch API** - HTTP client for backend communication

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
npm run type-check # TypeScript type checking
```

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**: Backend should allow frontend origin (already configured)
2. **API Key Missing**: Check OpenAI/LangSmith keys in backend `.env`
3. **Port Conflicts**: Backend on :8000, frontend on :3000
4. **Network Errors**: Ensure backend is running and accessible

### Debug Checklist

- [ ] Backend running at http://localhost:8000
- [ ] Backend health check passes
- [ ] Frontend environment variables set
- [ ] No console errors in browser dev tools
- [ ] Network tab shows successful API calls

### Logs & Monitoring

- **Backend Logs**: Check FastAPI terminal output
- **Frontend Logs**: Browser dev tools console
- **Network Requests**: Browser dev tools Network tab
- **Performance Metrics**: http://localhost:8000/metrics/performance

## 🎨 UI/UX Features

### Design Philosophy

- **Modern & Clean**: Minimalist interface focused on usability
- **Dark Theme**: Elegant dark blue color scheme
- **Responsive**: Mobile-first design principles
- **Accessible**: WCAG compliant components
- **Fast**: Optimized for performance and loading speed

### Interactive Elements

- **File Drop Zone**: Drag & drop file upload
- **Real-time Progress**: Live generation status updates
- **Collapsible Sections**: Organized content layout
- **Loading States**: Visual feedback for all async operations
- **Error Handling**: User-friendly error messages

## 🚀 Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Connect to Vercel
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-backend-domain.com`
4. Deploy automatically

### Environment Variables

```env
# Production
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
NODE_ENV=production

# Development  
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## 🎉 What You Should See

- **Real Questions**: Generated by your LangGraph Evol-Instruct workflow
- **Actual Processing**: Real-time progress from backend processing
- **Quality Scores**: Genuine evaluation from LLM-as-judge
- **Performance**: Fast responses thanks to Redis caching
- **Network Activity**: HTTP requests visible in browser dev tools

---

**Ready to generate amazing synthetic data with a beautiful UI! 🚀**

For backend documentation and API details, see `../api/README.md`
