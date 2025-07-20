#!/usr/bin/env python3
"""
Railway health check script for EvolSynth API
"""
import requests
import sys
import os

try:
    port = os.getenv("PORT", "8000")
    response = requests.get(f"http://localhost:{port}/health", timeout=10)
    if response.status_code == 200 and response.json().get("status") == "healthy":
        print("✅ Railway health check passed")
        sys.exit(0)
    else:
        print(f"❌ Railway health check failed: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Railway health check error: {e}")
    sys.exit(1) 