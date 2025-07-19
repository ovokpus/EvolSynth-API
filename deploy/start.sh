#!/bin/bash

# EvolSynth API Startup Script for Railway
set -e

echo "🚀 Starting EvolSynth API on Railway"
echo "Port: ${PORT}"
echo "Environment: ${ENVIRONMENT}"
echo "Redis: ${REDIS_HOST:-localhost}:${REDIS_PORT:-6379}"

# Railway-optimized startup
if [ "${ENVIRONMENT}" = "production" ]; then
    echo "🔧 Starting with Gunicorn for Railway"
    exec gunicorn api.main:app \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers ${WORKERS:-2} \
        --bind 0.0.0.0:${PORT} \
        --timeout ${REQUEST_TIMEOUT:-120} \
        --keepalive 2 \
        --max-requests 500 \
        --max-requests-jitter 50 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --preload
else
    echo "🔧 Starting with Uvicorn for Railway"
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port ${PORT} \
        --log-level info
fi 