# Multi-stage Docker build for EvolSynth API
# Optimized for production deployment with security best practices

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for building
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /home/app

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Additional dependencies for production
RUN pip install --user --no-cache-dir \
    gunicorn \
    uvloop \
    httptools \
    psutil \
    bleach

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/app/.local/bin:$PATH" \
    ENVIRONMENT=production

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Create necessary directories
RUN mkdir -p /home/app/logs /home/app/tmp \
    && chown -R app:app /home/app

# Switch to non-root user
USER app

# Set work directory
WORKDIR /home/app

# Copy Python dependencies from builder
COPY --from=builder --chown=app:app /home/app/.local /home/app/.local

# Copy application code
COPY --chown=app:app api/ ./api/
COPY --chown=app:app requirements.txt pyproject.toml ./

# Create startup script
COPY --chown=app:app <<EOF ./start.sh
#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting EvolSynth API in \${ENVIRONMENT:-production} mode"

# Validate environment
python -c "
from api.config.environments import get_config, validate_config
config = get_config()
validation = validate_config(config)
print(f'Environment: {config.environment.value}')
print(f'Valid: {validation[\"valid\"]}')
if not validation['valid']:
    print('Configuration issues:')
    for issue in validation['issues']:
        print(f'  - {issue}')
    exit(1)
if validation['warnings']:
    print('Configuration warnings:')
    for warning in validation['warnings']:
        print(f'  - {warning}')
"

# Initialize logging directory
mkdir -p logs

# Health check before starting
python -c "
import asyncio
from api.utils.health_checks import initialize_health_checks, get_health_status

async def check():
    initialize_health_checks()
    try:
        status = await get_health_status()
        print(f'Health check: {status[\"status\"]}')
        if status['critical_failures'] > 0:
            print('Critical health check failures detected')
            exit(1)
    except Exception as e:
        print(f'Health check failed: {e}')
        # Don't exit on health check failure during startup

asyncio.run(check())
"

# Start the application
if [ "\${ENVIRONMENT}" = "production" ]; then
    echo "🔧 Starting with Gunicorn (Production)"
    exec gunicorn api.main:app \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers \${WORKERS:-4} \
        --bind 0.0.0.0:\${PORT:-8000} \
        --timeout \${REQUEST_TIMEOUT:-300} \
        --keepalive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
else
    echo "🔧 Starting with Uvicorn (Development/Staging)"
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port \${PORT:-8000} \
        --workers \${WORKERS:-1} \
        --log-level info
fi
EOF

# Make startup script executable
RUN chmod +x start.sh

# Health check script
COPY --chown=app:app <<EOF ./health_check.py
#!/usr/bin/env python3
"""
Docker health check script for EvolSynth API
"""
import asyncio
import sys
import aiohttp
import os

async def health_check():
    port = os.getenv('PORT', '8000')
    timeout = aiohttp.ClientTimeout(total=10)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f'http://localhost:{port}/health') as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'healthy':
                        print("✅ Health check passed")
                        return 0
                    else:
                        print(f"❌ Health check failed: {data.get('status')}")
                        return 1
                else:
                    print(f"❌ Health check failed with status: {response.status}")
                    return 1
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(health_check())
    sys.exit(exit_code)
EOF

# Make health check executable
RUN chmod +x health_check.py

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python health_check.py

# Start command
CMD ["./start.sh"]

# Labels for metadata
LABEL maintainer="EvolSynth Team" \
      version="1.0.0" \
      description="EvolSynth API - Advanced Synthetic Data Generation" \
      org.opencontainers.image.title="EvolSynth API" \
      org.opencontainers.image.description="Advanced Synthetic Data Generation using LangGraph-based Evol-Instruct methodology" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="EvolSynth Team" 