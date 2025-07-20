# EvolSynth API - Production Deployment Guide

This guide covers deploying the EvolSynth API to production using Docker with comprehensive monitoring, security, and scalability considerations.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 22.04 LTS (recommended) or similar Linux distribution
- **CPU**: Minimum 2 cores, recommended 4+ cores
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 20GB, recommended 50GB+ SSD
- **Network**: Stable internet connection for API calls

### Required Software
- Docker Engine 20.10+
- Docker Compose v2.0+
- Git
- OpenSSL (for SSL certificates)
- Nginx (if not using Docker Compose nginx service)

### API Keys Required
- OpenAI API Key (required)
- LangChain API Key (recommended for tracing)

## 🚀 Quick Start Deployment

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd EvolSynth-API

# Switch to deploy branch
git checkout deploy

# Create environment file
cp .env.production .env
```

### 2. Configure Environment
Edit `.env` file with your settings:
```bash
# Essential Configuration
ENVIRONMENT=production
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Server Configuration
PORT=8000
WORKERS=4
MAX_CONCURRENCY=12

# Redis Configuration
REDIS_PASSWORD=your_secure_redis_password_here

# Security Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000

# Monitoring
GRAFANA_PASSWORD=your_secure_grafana_password_here
```

### 3. Deploy with Docker Compose
```bash
# Start core services (API + Redis)
docker-compose -f docker-compose.deploy.yml up -d

# Or start with monitoring stack
docker-compose -f docker-compose.deploy.yml --profile monitoring up -d

# Check service status
docker-compose -f docker-compose.deploy.yml ps
```

### 4. Verify Deployment
```bash
# Check API health
curl http://localhost:8000/health

# Check logs
docker-compose -f docker-compose.deploy.yml logs -f evolsynth-api

# Monitor Redis
docker-compose -f docker-compose.deploy.yml logs -f redis
```

## 🔧 Detailed Configuration

### Environment Configurations

#### Production Environment (.env.production)
```bash
# Production Environment Configuration
ENVIRONMENT=production

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password
REDIS_SSL=false

# Performance Settings
MAX_CONCURRENCY=12
BATCH_SIZE=10
REQUEST_TIMEOUT=300
LLM_REQUEST_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/evolsynth_production.log

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# LLM Configuration
DEFAULT_MODEL=gpt-4o
EVALUATION_MODEL=gpt-4o-mini
MAX_TOKENS=500
TEMPERATURE=0.7

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=3600
DOCUMENT_CACHE_TTL=7200
RESULT_CACHE_TTL=3600
```

#### Staging Environment (.env.staging)
```bash
# Staging Environment Configuration
ENVIRONMENT=staging

# API Keys (same as production)
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Server Configuration
WORKERS=2
MAX_CONCURRENCY=6
BATCH_SIZE=6

# Security (more permissive for testing)
ALLOWED_ORIGINS=https://staging.yourdomain.com
RATE_LIMIT_REQUESTS=200

# LLM Configuration (cost-optimized)
DEFAULT_MODEL=gpt-4o-mini
MAX_TOKENS=400
```

### Docker Configuration

#### Multi-stage Dockerfile Benefits
- **Security**: Runs as non-root user
- **Size**: Multi-stage build reduces image size
- **Performance**: Optimized Python dependencies
- **Monitoring**: Built-in health checks

#### Container Features
- Health checks every 30 seconds
- Graceful shutdown handling
- Log rotation and management
- Resource limits and monitoring

### Redis Configuration

#### Production Redis Settings
```bash
# redis.conf (production optimizations)
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
tcp-keepalive 300
timeout 0
```

## 🔐 Security Best Practices

### 1. SSL/TLS Configuration
```bash
# Generate SSL certificates (Let's Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d api.yourdomain.com

# Or use provided nginx configuration with SSL
cp nginx/ssl.conf.example nginx/conf.d/ssl.conf
# Edit nginx/conf.d/ssl.conf with your domain
```

### 2. Firewall Configuration
```bash
# UFW Configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # API port
sudo ufw enable
```

### 3. Environment Security
```bash
# Secure environment file
chmod 600 .env*
chown root:root .env*

# Use Docker secrets in production
echo "your_openai_api_key" | docker secret create openai_api_key -
echo "your_redis_password" | docker secret create redis_password -
```

### 4. Rate Limiting & DDoS Protection
- Cloudflare or similar CDN (recommended)
- Built-in rate limiting (configurable)
- Nginx rate limiting as backup
- IP whitelisting for admin endpoints

## 📊 Monitoring & Observability

### Available Monitoring Stack
1. **Prometheus**: Metrics collection
2. **Grafana**: Dashboards and alerting
3. **Loki**: Log aggregation
4. **Redis Insight**: Redis monitoring

### Start Monitoring Services
```bash
# Start full monitoring stack
docker-compose -f docker-compose.deploy.yml --profile monitoring up -d

# Access dashboards
echo "Grafana: http://localhost:3000 (admin/your_grafana_password)"
echo "Prometheus: http://localhost:9090"
echo "Redis Insight: http://localhost:8001"
```

### Key Metrics to Monitor
- **API Performance**: Response times, throughput, error rates
- **System Resources**: CPU, memory, disk usage
- **Redis Performance**: Cache hit ratio, memory usage
- **LLM Usage**: Token consumption, API costs
- **Security**: Failed authentication attempts, rate limit hits

### Log Management
```bash
# View application logs
docker-compose -f docker-compose.deploy.yml logs -f evolsynth-api

# View structured logs (production)
tail -f logs/evolsynth_production.log | jq .

# Rotate logs
logrotate -f /etc/logrotate.d/evolsynth-api
```

## 🔄 Deployment Strategies

### 1. Blue-Green Deployment
```bash
# Deploy new version to green environment
docker-compose -f docker-compose.deploy.yml -p evolsynth-green up -d

# Test green environment
curl http://localhost:8001/health

# Switch traffic (update load balancer)
# Then stop blue environment
docker-compose -f docker-compose.deploy.yml -p evolsynth-blue down
```

### 2. Rolling Updates
```bash
# Update image
docker-compose -f docker-compose.deploy.yml pull evolsynth-api

# Rolling restart
docker-compose -f docker-compose.deploy.yml up -d --no-deps evolsynth-api
```

### 3. Canary Deployment
```bash
# Deploy canary instance
docker run -d --name evolsynth-canary \
  -p 8001:8000 \
  -e ENVIRONMENT=production \
  evolsynth-api:latest

# Route 10% traffic to canary
# Monitor metrics and gradually increase traffic
```

## 📈 Scaling Considerations

### Horizontal Scaling
```bash
# Scale API instances
docker-compose -f docker-compose.deploy.yml up -d --scale evolsynth-api=3

# Use load balancer (nginx/traefik)
# Configure session affinity if needed
```

### Vertical Scaling
```bash
# Update Docker Compose resource limits
services:
  evolsynth-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Redis Scaling
```bash
# Redis Cluster (for high availability)
docker-compose -f docker-compose.redis-cluster.yml up -d

# Redis Sentinel (for failover)
docker-compose -f docker-compose.redis-sentinel.yml up -d
```

## 🛠 Maintenance & Operations

### Backup Strategy
```bash
# Database backups (if using persistent storage)
docker exec evolsynth-redis redis-cli --rdb /data/backup.rdb

# Log backups
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Configuration backups
cp .env* /backup/configs/
```

### Updates & Patches
```bash
# Update application
git pull origin deploy
docker-compose -f docker-compose.deploy.yml build
docker-compose -f docker-compose.deploy.yml up -d

# Update base images
docker-compose -f docker-compose.deploy.yml pull
docker-compose -f docker-compose.deploy.yml up -d
```

### Health Checks
```bash
# Manual health check
curl -f http://localhost:8000/health || exit 1

# Automated monitoring script
#!/bin/bash
while true; do
  if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Health check failed, restarting service"
    docker-compose -f docker-compose.deploy.yml restart evolsynth-api
  fi
  sleep 30
done
```

## 🔧 Troubleshooting

### Common Issues

#### 1. API Not Starting
```bash
# Check logs
docker-compose -f docker-compose.deploy.yml logs evolsynth-api

# Common causes:
# - Missing environment variables
# - Invalid API keys
# - Redis connection issues
# - Port conflicts
```

#### 2. High Memory Usage
```bash
# Check container stats
docker stats evolsynth-api

# Optimize settings
# - Reduce MAX_CONCURRENCY
# - Lower cache TTL
# - Reduce BATCH_SIZE
```

#### 3. Redis Connection Issues
```bash
# Test Redis connection
docker exec evolsynth-redis redis-cli ping

# Check Redis logs
docker-compose -f docker-compose.deploy.yml logs redis
```

#### 4. SSL Certificate Issues
```bash
# Renew Let's Encrypt certificates
sudo certbot renew

# Test SSL configuration
openssl s_client -connect api.yourdomain.com:443
```

### Performance Tuning

#### API Optimization
```bash
# Environment variables for performance
MAX_CONCURRENCY=16        # Increase for more CPU cores
BATCH_SIZE=12            # Optimize based on memory
LLM_REQUEST_TIMEOUT=90   # Increase for complex requests
CACHE_TTL=7200          # Increase for better cache hit ratio
```

#### System Optimization
```bash
# Increase file descriptor limits
echo "fs.file-max = 100000" >> /etc/sysctl.conf
echo "* soft nofile 65535" >> /etc/security/limits.conf
echo "* hard nofile 65535" >> /etc/security/limits.conf

# Optimize network settings
echo "net.core.somaxconn = 1024" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 1024" >> /etc/sysctl.conf
```

## 📞 Support & Contact

### Deployment Support
- Check logs first: `docker-compose logs`
- Review configuration: Environment variables and Docker Compose settings
- Monitor resources: CPU, memory, disk usage
- Test connectivity: Redis, external APIs

### Production Readiness Checklist
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Monitoring enabled
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Health checks working
- [ ] Performance testing completed
- [ ] Security scanning done
- [ ] Documentation updated

---

**Note**: This deployment guide assumes a production environment. Always test in staging first and follow your organization's deployment procedures. 