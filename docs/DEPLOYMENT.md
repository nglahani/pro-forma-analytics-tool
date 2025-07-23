# Deployment Guide

This document provides comprehensive guidance for deploying the Pro-Forma Analytics Tool in various environments, from development to production.

## 🚀 Deployment Overview

The Pro-Forma Analytics Tool can be deployed using multiple strategies:

- **Docker Containers**: Recommended for production
- **Virtual Machines**: Traditional deployment
- **Cloud Platforms**: AWS, Azure, Google Cloud
- **Serverless**: AWS Lambda, Azure Functions

## 📋 Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 20GB | 50GB+ |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| **Python** | 3.8+ | 3.11+ |
| **Database** | SQLite | PostgreSQL |

### Software Dependencies

```bash
# System packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y nginx postgresql postgresql-contrib
sudo apt install -y redis-server supervisor

# Python packages (will be installed via requirements.txt)
# See requirements.txt for complete list
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/proforma
      - REDIS_URL=redis://redis:6379
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - DEBUG=False
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=proforma
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Nginx Configuration

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name api.proforma-analytics.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.proforma-analytics.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
        limit_req zone=api burst=20 nodelay;

        # Proxy configuration
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check
        location /health {
            proxy_pass http://app;
            access_log off;
        }

        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## ☁️ Cloud Deployment

### AWS Deployment

#### AWS ECS with Fargate

```yaml
# task-definition.json
{
  "family": "proforma-analytics",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/proforma-analytics:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:password@rds-endpoint:5432/proforma"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://elasticache-endpoint:6379"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/proforma-analytics",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### AWS Lambda Deployment

```python
# lambda_function.py
import json
from mangum import Mangum
from src.main import app

handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
```

```yaml
# serverless.yml
service: proforma-analytics

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    DATABASE_URL: ${ssm:/proforma/database_url}
    REDIS_URL: ${ssm:/proforma/redis_url}

functions:
  api:
    handler: lambda_function.lambda_handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
    memorySize: 512
    timeout: 30
    environment:
      POWERTOOLS_SERVICE_NAME: proforma-analytics
```

### Google Cloud Platform

#### Cloud Run Deployment

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/proforma-analytics:$COMMIT_SHA', '.']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/proforma-analytics:$COMMIT_SHA']
  
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'proforma-analytics'
      - '--image'
      - 'gcr.io/$PROJECT_ID/proforma-analytics:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'DATABASE_URL=postgresql://user:password@host:5432/proforma'

images:
  - 'gcr.io/$PROJECT_ID/proforma-analytics:$COMMIT_SHA'
```

### Azure Deployment

#### Azure Container Instances

```yaml
# azure-deploy.yml
apiVersion: 2019-12-01
location: eastus
name: proforma-analytics
properties:
  containers:
  - name: app
    properties:
      image: proformaanalytics.azurecr.io/proforma-analytics:latest
      ports:
      - port: 8000
      environmentVariables:
      - name: DATABASE_URL
        value: "postgresql://user:password@host:5432/proforma"
      - name: REDIS_URL
        value: "redis://host:6379"
      resources:
        requests:
          cpu: 1.0
          memoryInGB: 1.5
        limits:
          cpu: 2.0
          memoryInGB: 3.0
  osType: Linux
  restartPolicy: Always
```

## 🔧 Environment Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/proforma
MARKET_DATA_DB=data/databases/market_data.db
ECONOMIC_DATA_DB=data/databases/economic_data.db
PROPERTY_DATA_DB=data/databases/property_data.db
FORECAST_CACHE_DB=data/databases/forecast_cache.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Storage
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=proforma-analytics
AWS_S3_REGION=us-east-1

# Monitoring
SENTRY_DSN=your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your-new-relic-key
```

### Configuration Management

```python
# config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/databases/")
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External Services
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 🔒 Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/private.key -out ssl/certificate.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=api.proforma-analytics.com"

# Configure SSL in nginx
# See nginx.conf above
```

### Firewall Configuration

```bash
# UFW Firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables (alternative)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### Database Security

```sql
-- PostgreSQL security
CREATE USER proforma_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE proforma TO proforma_user;
GRANT USAGE ON SCHEMA public TO proforma_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO proforma_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO proforma_user;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/cert.pem';
ALTER SYSTEM SET ssl_key_file = '/path/to/key.pem';
```

## 📊 Monitoring and Logging

### Application Monitoring

```python
# monitoring.py
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request

# Sentry configuration
sentry_sdk.init(
    dsn=settings.sentry_dsn,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Middleware for monitoring
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Configuration

```python
# logging_config.py
import logging
import logging.handlers
import os

def setup_logging():
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'logs/app.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
```

### Health Checks

```python
# health.py
from fastapi import APIRouter
import psutil
import sqlite3

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # System checks
    checks["checks"]["system"] = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }
    
    # Database checks
    try:
        with sqlite3.connect('data/databases/market_data.db') as conn:
            conn.execute("SELECT 1")
        checks["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        checks["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        checks["status"] = "unhealthy"
    
    # Redis checks
    try:
        redis_client.ping()
        checks["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        checks["status"] = "unhealthy"
    
    return checks
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest tests/
      - name: Run linting
        run: |
          flake8 src/
          black --check src/
          isort --check-only src/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t proforma-analytics:${{ github.sha }} .
      - name: Deploy to AWS ECS
        run: |
          aws ecs update-service --cluster proforma-cluster --service proforma-service --force-new-deployment
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
    - pytest tests/
    - flake8 src/
    - black --check src/

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - kubectl set image deployment/proforma-analytics app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/proforma-analytics
```

## 🚨 Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh

# PostgreSQL backup
pg_dump -h localhost -U postgres proforma > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite backup
cp data/databases/*.db backups/

# Upload to S3
aws s3 sync backups/ s3://proforma-backups/$(date +%Y%m%d)/
```

### Recovery Procedures

```bash
#!/bin/bash
# restore.sh

# PostgreSQL restore
psql -h localhost -U postgres proforma < backup_file.sql

# SQLite restore
cp backups/*.db data/databases/

# Verify data integrity
python -c "
import sqlite3
conn = sqlite3.connect('data/databases/market_data.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM interest_rates')
print(f'Records: {cursor.fetchone()[0]}')
"
```

## 📈 Performance Optimization

### Application Optimization

```python
# performance.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

### Server Optimization

```bash
# System tuning
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
sysctl -p

# Nginx optimization
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 10M;
```

## 🔍 Troubleshooting

### Common Deployment Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :8000
   
   # Kill the process
   sudo kill -9 <PID>
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   python -c "
   import sqlite3
   conn = sqlite3.connect('data/databases/market_data.db')
   print('Database connection successful')
   "
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Check swap
   swapon --show
   ```

4. **SSL Certificate Issues**
   ```bash
   # Test SSL certificate
   openssl s_client -connect api.proforma-analytics.com:443 -servername api.proforma-analytics.com
   ```

### Log Analysis

```bash
# View application logs
tail -f logs/app.log

# Search for errors
grep -i error logs/app.log

# Monitor real-time requests
tail -f /var/log/nginx/access.log | grep proforma
```

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [SSL/TLS Configuration](https://ssl-config.mozilla.org/)