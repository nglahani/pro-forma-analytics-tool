#!/bin/bash
# Production Entrypoint Script for Pro-Forma Analytics Tool

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Pro-Forma Analytics Tool (Production)${NC}"

# Environment variables with defaults
export PRO_FORMA_ENV=${PRO_FORMA_ENV:-production}
export API_HOST=${API_HOST:-0.0.0.0}
export API_PORT=${API_PORT:-8000}
export API_WORKERS=${API_WORKERS:-4}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo -e "${YELLOW}Environment: ${PRO_FORMA_ENV}${NC}"
echo -e "${YELLOW}API Host: ${API_HOST}:${API_PORT}${NC}"
echo -e "${YELLOW}Workers: ${API_WORKERS}${NC}"
echo -e "${YELLOW}Log Level: ${LOG_LEVEL}${NC}"

# Ensure required directories exist
echo -e "${YELLOW}📁 Creating required directories...${NC}"
mkdir -p data/databases logs backups cache

# Validate required environment variables
echo -e "${YELLOW}🔍 Validating environment configuration...${NC}"

if [[ -z "$SECRET_KEY" ]]; then
    echo -e "${RED}❌ ERROR: SECRET_KEY environment variable is required${NC}"
    exit 1
fi

if [[ ${#SECRET_KEY} -lt 32 ]]; then
    echo -e "${RED}❌ ERROR: SECRET_KEY must be at least 32 characters long${NC}"
    exit 1
fi

# Database initialization check
echo -e "${YELLOW}🗄️ Checking database initialization...${NC}"
if [[ ! -f "data/databases/market_data.db" ]]; then
    echo -e "${YELLOW}Initializing databases for production...${NC}"
    python data_manager.py setup --environment=production
fi

# Run database integrity check
echo -e "${YELLOW}🔍 Running database integrity check...${NC}"
python -c "
import sqlite3
import sys
from pathlib import Path

databases = ['market_data.db', 'property_data.db', 'economic_data.db', 'forecast_cache.db']
base_path = Path('data/databases')

for db_name in databases:
    db_path = base_path / db_name
    if not db_path.exists():
        print(f'❌ Database {db_name} not found')
        sys.exit(1)
    
    try:
        with sqlite3.connect(str(db_path), timeout=5.0) as conn:
            cursor = conn.execute(\"SELECT COUNT(*) FROM sqlite_master WHERE type='table'\")
            table_count = cursor.fetchone()[0]
            if table_count == 0:
                print(f'❌ Database {db_name} has no tables')
                sys.exit(1)
            print(f'✅ Database {db_name} OK ({table_count} tables)')
    except Exception as e:
        print(f'❌ Database {db_name} error: {e}')
        sys.exit(1)

print('✅ All databases validated successfully')
"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Database validation failed${NC}"
    exit 1
fi

# Pre-flight health check
echo -e "${YELLOW}🏥 Running pre-flight health check...${NC}"
python -c "
try:
    from src.presentation.api.main import app
    print('✅ Application imports successful')
    
    # Test core services
    from src.application.factories.service_factory import ServiceFactory
    factory = ServiceFactory()
    print('✅ Service factory initialization successful')
    
except Exception as e:
    print(f'❌ Pre-flight check failed: {e}')
    import sys
    sys.exit(1)
"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Pre-flight health check failed${NC}"
    exit 1
fi

# Set up monitoring directory
echo -e "${YELLOW}📊 Setting up monitoring...${NC}"
mkdir -p logs/metrics
touch logs/api.log logs/metrics/performance.log

# Log startup information
echo -e "${GREEN}✅ Pre-flight checks completed successfully${NC}"
echo -e "${GREEN}🌟 Starting API server...${NC}"

# Log environment info for monitoring
python -c "
import json
import os
from datetime import datetime

startup_info = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'environment': os.getenv('PRO_FORMA_ENV', 'unknown'),
    'version': '2.0.0',
    'workers': int(os.getenv('API_WORKERS', 4)),
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', 8000)),
    'log_level': os.getenv('LOG_LEVEL', 'INFO')
}

with open('logs/startup.json', 'w') as f:
    json.dump(startup_info, f, indent=2)

print('📝 Startup information logged')
"

# Handle different command types
if [[ "$1" == "uvicorn" ]]; then
    # Production API server
    echo -e "${GREEN}🌐 Starting production API server...${NC}"
    exec "$@" --log-config=config/logging.json
elif [[ "$1" == "worker" ]]; then
    # Background worker process
    echo -e "${GREEN}⚙️ Starting background worker...${NC}"
    exec python scripts/background_worker.py
elif [[ "$1" == "migrate" ]]; then
    # Database migration
    echo -e "${GREEN}🗄️ Running database migrations...${NC}"
    python data_manager.py migrate
elif [[ "$1" == "backup" ]]; then
    # Database backup
    echo -e "${GREEN}💾 Running database backup...${NC}"
    exec python scripts/backup_databases.py
elif [[ "$1" == "health-check" ]]; then
    # Health check
    echo -e "${GREEN}🏥 Running health check...${NC}"
    exec python scripts/health_check.py
elif [[ "$1" == "shell" ]]; then
    # Interactive shell
    echo -e "${GREEN}🐚 Starting interactive shell...${NC}"
    exec python -i -c "
from src.application.factories.service_factory import ServiceFactory
from src.domain.entities.property_data import SimplifiedPropertyInput
from datetime import date

print('Pro-Forma Analytics Shell')
print('Available objects:')
print('  - ServiceFactory')
print('  - SimplifiedPropertyInput')
print('Example: factory = ServiceFactory()')

factory = ServiceFactory()
"
else
    # Custom command or default
    echo -e "${GREEN}🔧 Executing custom command: $@${NC}"
    exec "$@"
fi