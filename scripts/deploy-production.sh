#!/bin/bash
# Production Deployment Script for Pro-Forma Analytics Tool

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="pro-forma-analytics"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"
BACKUP_DIR="/opt/backups/proforma"
LOG_DIR="/var/log/proforma"

echo -e "${GREEN}🚀 Pro-Forma Analytics Tool - Production Deployment${NC}"
echo -e "${BLUE}=================================================${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check if running as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}❌ This script must be run as root or with sudo${NC}"
        exit 1
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "curl" "openssl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo -e "${RED}❌ Required command not found: $cmd${NC}"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Environment validation
validate_environment() {
    echo -e "${YELLOW}🔍 Validating environment configuration...${NC}"
    
    # Check for required environment file
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            echo -e "${YELLOW}⚠️ .env file not found. Copying from .env.example${NC}"
            cp .env.example .env
            echo -e "${RED}❌ Please edit .env file with your production values${NC}"
            exit 1
        else
            echo -e "${RED}❌ .env file not found and no .env.example available${NC}"
            exit 1
        fi
    fi
    
    # Source environment variables
    source .env
    
    # Check critical environment variables
    local required_vars=("SECRET_KEY" "PRO_FORMA_ENV")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo -e "${RED}❌ Required environment variable not set: $var${NC}"
            exit 1
        fi
    done
    
    # Validate SECRET_KEY strength
    if [[ ${#SECRET_KEY} -lt 32 ]]; then
        echo -e "${RED}❌ SECRET_KEY must be at least 32 characters long${NC}"
        exit 1
    fi
    
    # Check environment setting
    if [[ "$PRO_FORMA_ENV" != "production" ]]; then
        echo -e "${YELLOW}⚠️ Environment is set to: $PRO_FORMA_ENV (expected: production)${NC}"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Environment validation passed${NC}"
}

# SSL certificate setup
setup_ssl() {
    echo -e "${YELLOW}🔒 Setting up SSL certificates...${NC}"
    
    mkdir -p ssl
    
    if [[ ! -f "ssl/cert.pem" ]] || [[ ! -f "ssl/key.pem" ]]; then
        echo -e "${YELLOW}📜 SSL certificates not found. Generating self-signed certificates...${NC}"
        echo -e "${RED}⚠️ For production, replace with valid certificates from a CA${NC}"
        
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=proforma.local" \
            -addext "subjectAltName=DNS:proforma.local,DNS:localhost,IP:127.0.0.1"
        
        chmod 600 ssl/key.pem
        chmod 644 ssl/cert.pem
    fi
    
    echo -e "${GREEN}✅ SSL certificates configured${NC}"
}

# Create required directories
setup_directories() {
    echo -e "${YELLOW}📁 Creating required directories...${NC}"
    
    local directories=(
        "data/databases"
        "logs"
        "backups"
        "cache"
        "monitoring/grafana/provisioning/datasources"
        "monitoring/grafana/provisioning/dashboards"
        "monitoring/grafana/dashboards"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo -e "${BLUE}   Created: $dir${NC}"
    done
    
    # Set proper permissions
    chown -R 1000:1000 data/ logs/ backups/ cache/
    
    echo -e "${GREEN}✅ Directories setup completed${NC}"
}

# Database initialization
initialize_databases() {
    echo -e "${YELLOW}🗄️ Initializing databases...${NC}"
    
    if [[ ! -f "data/databases/market_data.db" ]]; then
        echo -e "${BLUE}   Running database initialization...${NC}"
        
        # Run database setup using Python
        docker run --rm \
            -v "$(pwd)/data:/app/data" \
            -v "$(pwd):/app" \
            -w /app \
            python:3.11-slim \
            /bin/bash -c "
                pip install -q -r requirements.txt
                python data_manager.py setup --environment=production
            "
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ Database initialization completed${NC}"
        else
            echo -e "${RED}❌ Database initialization failed${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Databases already initialized${NC}"
    fi
}

# Build and start services
deploy_services() {
    echo -e "${YELLOW}🏗️ Building and deploying services...${NC}"
    
    # Build images
    echo -e "${BLUE}   Building Docker images...${NC}"
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # Stop existing services
    echo -e "${BLUE}   Stopping existing services...${NC}"
    docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
    
    # Start core services
    echo -e "${BLUE}   Starting core services...${NC}"
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d redis prometheus
    
    # Wait for dependencies
    echo -e "${BLUE}   Waiting for dependencies to be ready...${NC}"
    sleep 30
    
    # Start main API
    echo -e "${BLUE}   Starting Pro-Forma API...${NC}"
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d proforma-api
    
    # Wait for API to be ready
    echo -e "${BLUE}   Waiting for API to be ready...${NC}"
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T proforma-api \
           python -c "import requests; requests.get('http://localhost:8000/api/v1/health').raise_for_status()" 2>/dev/null; then
            echo -e "${GREEN}✅ API is ready${NC}"
            break
        fi
        
        echo -e "${BLUE}   Attempt $attempt/$max_attempts - API not ready yet...${NC}"
        ((attempt++))
        sleep 10
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        echo -e "${RED}❌ API failed to start within timeout${NC}"
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs proforma-api
        exit 1
    fi
    
    # Start remaining services
    echo -e "${BLUE}   Starting remaining services...${NC}"
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    echo -e "${GREEN}✅ Services deployment completed${NC}"
}

# Health checks
run_health_checks() {
    echo -e "${YELLOW}🏥 Running health checks...${NC}"
    
    local services=("proforma-api" "redis" "prometheus" "grafana" "nginx")
    
    for service in "${services[@]}"; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            echo -e "${GREEN}✅ $service is running${NC}"
        else
            echo -e "${RED}❌ $service is not running${NC}"
            docker-compose -f "$DOCKER_COMPOSE_FILE" logs "$service"
        fi
    done
    
    # API health check
    echo -e "${BLUE}   Testing API health endpoint...${NC}"
    if curl -f -s "http://localhost:8000/api/v1/health" > /dev/null; then
        echo -e "${GREEN}✅ API health check passed${NC}"
    else
        echo -e "${RED}❌ API health check failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Health checks completed${NC}"
}

# Performance verification
verify_performance() {
    echo -e "${YELLOW}⚡ Running performance verification...${NC}"
    
    # Run basic performance test
    echo -e "${BLUE}   Testing DCF analysis performance...${NC}"
    
    local test_response=$(curl -s -w "%{http_code}:%{time_total}" -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "property_name": "Performance Test Property",
            "residential_units": 24,
            "renovation_time_months": 6,
            "commercial_units": 0,
            "investor_equity_share_pct": 75.0,
            "residential_rent_per_unit": 2800,
            "commercial_rent_per_unit": 0,
            "self_cash_percentage": 30.0,
            "city": "Chicago",
            "state": "IL",
            "purchase_price": 3500000
        }' \
        "http://localhost:8000/api/v1/analysis/dcf")
    
    local http_code=$(echo "$test_response" | cut -d: -f1)
    local response_time=$(echo "$test_response" | cut -d: -f2)
    
    if [[ "$http_code" == "200" ]]; then
        echo -e "${GREEN}✅ DCF analysis test passed (${response_time}s)${NC}"
        
        if (( $(echo "$response_time < 30.0" | bc -l) )); then
            echo -e "${GREEN}✅ Response time within acceptable limits${NC}"
        else
            echo -e "${YELLOW}⚠️ Response time slower than expected: ${response_time}s${NC}"
        fi
    else
        echo -e "${RED}❌ DCF analysis test failed (HTTP $http_code)${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Performance verification completed${NC}"
}

# Setup monitoring
setup_monitoring() {
    echo -e "${YELLOW}📊 Setting up monitoring and alerting...${NC}"
    
    # Create Grafana datasource configuration
    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
EOF
    
    # Create dashboard configuration
    cat > monitoring/grafana/provisioning/dashboards/dashboards.yml << EOF
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
EOF
    
    echo -e "${GREEN}✅ Monitoring setup completed${NC}"
}

# Create maintenance scripts
create_maintenance_scripts() {
    echo -e "${YELLOW}🔧 Creating maintenance scripts...${NC}"
    
    # Backup script
    cat > scripts/backup.sh << 'EOF'
#!/bin/bash
# Database backup script
BACKUP_DIR="/opt/backups/proforma/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Backup databases
docker-compose -f docker-compose.production.yml exec -T proforma-api \
    tar czf - data/databases/ | cat > "$BACKUP_DIR/databases.tar.gz"

# Backup logs (last 7 days)
find logs/ -name "*.log" -mtime -7 -exec tar czf "$BACKUP_DIR/logs.tar.gz" {} +

# Cleanup old backups (keep last 30 days)
find /opt/backups/proforma/ -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR"
EOF
    
    # Status check script
    cat > scripts/status.sh << 'EOF'
#!/bin/bash
# System status check
echo "=== Pro-Forma Analytics Status ==="
echo "Date: $(date)"
echo

echo "=== Docker Services ==="
docker-compose -f docker-compose.production.yml ps

echo
echo "=== API Health ==="
curl -s http://localhost:8000/api/v1/health | jq '.'

echo
echo "=== System Resources ==="
echo "Memory Usage:"
free -h
echo
echo "Disk Usage:"
df -h | grep -E "(data|logs|backups)"

echo
echo "=== Recent Logs ==="
docker-compose -f docker-compose.production.yml logs --tail=10 proforma-api
EOF
    
    chmod +x scripts/backup.sh scripts/status.sh
    
    echo -e "${GREEN}✅ Maintenance scripts created${NC}"
}

# Final verification and summary
deployment_summary() {
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo
    echo -e "${YELLOW}🌐 Service URLs:${NC}"
    echo -e "${BLUE}   API:          https://localhost/api/v1/health${NC}"
    echo -e "${BLUE}   Documentation: https://localhost/docs${NC}"
    echo -e "${BLUE}   Metrics:      http://localhost:9090 (Prometheus)${NC}"
    echo -e "${BLUE}   Dashboards:   http://localhost:3001 (Grafana)${NC}"
    echo
    echo -e "${YELLOW}📊 Default Credentials:${NC}"
    echo -e "${BLUE}   Grafana: admin / ${GRAFANA_ADMIN_PASSWORD:-admin123}${NC}"
    echo
    echo -e "${YELLOW}🔧 Management Commands:${NC}"
    echo -e "${BLUE}   Status:  ./scripts/status.sh${NC}"
    echo -e "${BLUE}   Backup:  ./scripts/backup.sh${NC}"
    echo -e "${BLUE}   Logs:    docker-compose -f $DOCKER_COMPOSE_FILE logs -f${NC}"
    echo -e "${BLUE}   Stop:    docker-compose -f $DOCKER_COMPOSE_FILE down${NC}"
    echo
    echo -e "${GREEN}✅ Pro-Forma Analytics Tool is now running in production mode${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting deployment process...${NC}"
    echo
    
    check_prerequisites
    validate_environment
    setup_ssl
    setup_directories
    initialize_databases
    setup_monitoring
    deploy_services
    run_health_checks
    verify_performance
    create_maintenance_scripts
    deployment_summary
}

# Handle script interruption
trap 'echo -e "\n${RED}❌ Deployment interrupted${NC}"; exit 1' INT TERM

# Run main function
main "$@"