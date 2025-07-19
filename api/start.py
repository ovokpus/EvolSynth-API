#!/usr/bin/env python3
"""
EvolSynth API Startup Script
Easy startup for development and production environments
"""

import os
import sys
import argparse
from pathlib import Path


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY", "LANGCHAIN_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Create a .env file with these variables or set them in your environment")
        print("   See README.md for setup instructions")
        return False
    
    return True


def start_api(host="0.0.0.0", port=8000, reload=False, workers=1):
    """Start the EvolSynth API"""
    import uvicorn
    
    print("🚀 Starting EvolSynth API...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"👥 Workers: {workers}")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 API stopped by user")
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EvolSynth API Startup Script")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (development)")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--skip-env-check", action="store_true", help="Skip environment variable check")
    
    args = parser.parse_args()
    
    # Change to API directory
    api_dir = Path(__file__).parent
    os.chdir(api_dir)
    
    # Check environment variables
    if not args.skip_env_check and not check_environment():
        sys.exit(1)
    
    # Start the API
    start_api(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )


if __name__ == "__main__":
    main() 