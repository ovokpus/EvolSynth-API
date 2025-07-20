#!/bin/bash

# EvolSynth API Startup Script for Railway
set -e

echo "🚀 Starting EvolSynth API on Railway"

# Railway assigns PORT dynamically - ensure it's set
export PORT=${PORT:-8000}
echo "Port: ${PORT}"
echo "Environment: ${ENVIRONMENT:-production}"
echo "Redis: ${REDIS_HOST:-localhost}:${REDIS_PORT:-6379}"

# Debug Railway environment
echo "🔍 Railway Debug Info:"
echo "  - PORT: ${PORT}"
echo "  - RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-unknown}"
echo "  - RAILWAY_SERVICE_NAME: ${RAILWAY_SERVICE_NAME:-unknown}"

# Validate critical environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY environment variable is required"
    exit 1
fi

if [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "⚠️  WARNING: LANGCHAIN_API_KEY not set - tracing will be disabled"
fi

echo "✅ Environment validation passed"

# Railway-optimized startup with debugging
echo "🔧 Starting with Gunicorn for Railway"
echo "📍 Final startup command: gunicorn api.main:app --bind 0.0.0.0:${PORT}"

exec gunicorn api.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${WORKERS:-2} \
    --bind 0.0.0.0:${PORT} \
    --timeout ${REQUEST_TIMEOUT:-120} \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info 