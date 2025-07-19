#!/bin/bash

# EvolSynth API Startup Script for Railway
set -e

echo "🚀 Starting EvolSynth API on Railway"
echo "Port: ${PORT}"
echo "Environment: ${ENVIRONMENT}"
echo "Redis: ${REDIS_HOST:-localhost}:${REDIS_PORT:-6379}"

# Validate critical environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY environment variable is required"
    exit 1
fi

if [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "⚠️  WARNING: LANGCHAIN_API_KEY not set - tracing will be disabled"
fi

echo "✅ Environment validation passed"

# Railway-optimized startup
if [ "${ENVIRONMENT}" = "production" ]; then
    echo "🔧 Starting with Gunicorn for Railway"
    exec gunicorn api.main:app \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers ${WORKERS:-2} \
        --bind 0.0.0.0:${PORT} \
        --timeout ${REQUEST_TIMEOUT:-120} \
        --access-logfile - \
        --error-logfile - \
        --log-level info
else
    echo "🔧 Starting with Uvicorn for Railway"
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port ${PORT} \
        --log-level info
fi 