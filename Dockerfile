# Railway-optimized Dockerfile for EvolSynth API
# Simplified single-stage build optimized for Railway's build environment

FROM python:3.13-slim

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

# Copy startup and health check scripts
COPY deploy/start.sh deploy/health_check.py ./
RUN chmod +x start.sh health_check.py

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