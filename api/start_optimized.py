#!/usr/bin/env python3
"""
EvolSynth Optimized Backend Startup Script
Starts the performance-enhanced FastAPI backend with Redis caching
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the optimized EvolSynth backend"""
    
    print("🚀 Starting EvolSynth Optimized Backend")
    print("=" * 50)
    
    # Set Python path (we're in api/, so parent is project root)
    api_dir = Path(__file__).parent
    project_root = api_dir.parent
    sys.path.insert(0, str(project_root))
    os.environ['PYTHONPATH'] = str(project_root)
    
    # Load performance environment if available
    env_file = project_root / ".env.performance"
    if env_file.exists():
        print("✅ Loading performance configuration")
        # Load .env.performance variables
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # Set default environment variables
    os.environ.setdefault('REDIS_HOST', 'localhost')
    os.environ.setdefault('REDIS_PORT', '6379')
    os.environ.setdefault('OPTIMIZATION_LEVEL', 'production')
    
    print("🔧 Configuration:")
    print(f"  Redis: {os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}")
    print(f"  Optimization: {os.environ.get('OPTIMIZATION_LEVEL', 'production')}")
    print(f"  Debug: {os.environ.get('DEBUG', 'false')}")
    
    # Start the FastAPI server
    try:
        print("\n🌟 Starting optimized FastAPI server...")
        print("   Access at: http://localhost:8000")
        print("   Docs at: http://localhost:8000/docs")
        print("   Performance metrics: http://localhost:8000/metrics/performance")
        print("\n" + "=" * 50)
        
        # Import and run the app
        from main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for production
            access_log=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 