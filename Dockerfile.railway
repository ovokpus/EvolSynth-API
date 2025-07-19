# Railway-optimized Dockerfile for EvolSynth API
# Simplified single-stage build optimized for Railway's build environment

FROM python:3.11-slim

# Set environment variables optimized for Railway
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production \
    PORT=8000

# Install system dependencies (minimal for Railway)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app directory
WORKDIR /app

# Copy dependency files first (for better Docker layer caching)
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn uvloop httptools

# Copy application code
COPY api/ ./api/

# Create startup script optimized for Railway
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Starting EvolSynth API on Railway"\n\
echo "Port: ${PORT}"\n\
echo "Environment: ${ENVIRONMENT}"\n\
echo "Redis: ${REDIS_HOST:-localhost}:${REDIS_PORT:-6379}"\n\
\n\
# Railway-optimized startup\n\
if [ "${ENVIRONMENT}" = "production" ]; then\n\
    echo "🔧 Starting with Gunicorn for Railway"\n\
    exec gunicorn api.main:app \\\n\
        --worker-class uvicorn.workers.UvicornWorker \\\n\
        --workers ${WORKERS:-2} \\\n\
        --bind 0.0.0.0:${PORT} \\\n\
        --timeout ${REQUEST_TIMEOUT:-120} \\\n\
        --keepalive 2 \\\n\
        --max-requests 500 \\\n\
        --max-requests-jitter 50 \\\n\
        --access-logfile - \\\n\
        --error-logfile - \\\n\
        --log-level info \\\n\
        --preload\n\
else\n\
    echo "🔧 Starting with Uvicorn for Railway"\n\
    exec uvicorn api.main:app \\\n\
        --host 0.0.0.0 \\\n\
        --port ${PORT} \\\n\
        --log-level info\n\
fi' > start.sh && chmod +x start.sh

# Create Railway health check
RUN echo '#!/usr/bin/env python3\n\
import requests\n\
import sys\n\
import os\n\
\n\
try:\n\
    port = os.getenv("PORT", "8000")\n\
    response = requests.get(f"http://localhost:{port}/health", timeout=10)\n\
    if response.status_code == 200 and response.json().get("status") == "healthy":\n\
        print("✅ Railway health check passed")\n\
        sys.exit(0)\n\
    else:\n\
        print(f"❌ Railway health check failed: {response.status_code}")\n\
        sys.exit(1)\n\
except Exception as e:\n\
    print(f"❌ Railway health check error: {e}")\n\
    sys.exit(1)' > health_check.py && chmod +x health_check.py

# Expose port for Railway
EXPOSE $PORT

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python health_check.py

# Railway metadata labels
LABEL railway.service="evolsynth-api" \
      railway.environment="production" \
      version="1.0.0"

# Start command
CMD ["./start.sh"] 