#!/bin/bash
# Cron setup script for Pro Forma Data Updates (Linux/macOS)
# Run this script to setup automated data updates using cron

PROJECT_PATH="/path/to/pro-forma-analytics-tool"
PYTHON_PATH="/usr/bin/python3"
FRED_API_KEY=""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Cron jobs for Pro Forma Data Updates${NC}"

# Function to add cron job
add_cron_job() {
    local schedule="$1"
    local command="$2"
    local description="$3"
    
    echo -e "${YELLOW}Adding cron job: $description${NC}"
    
    # Check if job already exists
    if crontab -l 2>/dev/null | grep -q "$command"; then
        echo -e "${YELLOW}Job already exists, skipping${NC}"
        return
    fi
    
    # Add the job
    (crontab -l 2>/dev/null; echo "$schedule cd $PROJECT_PATH && $PYTHON_PATH $command") | crontab -
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Added: $description${NC}"
    else
        echo -e "${RED}✗ Failed to add: $description${NC}"
    fi
}

# Validate project path
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}Error: Project path does not exist: $PROJECT_PATH${NC}"
    echo "Please update PROJECT_PATH in this script"
    exit 1
fi

# Test Python installation
if ! command -v $PYTHON_PATH &> /dev/null; then
    echo -e "${RED}Error: Python not found at $PYTHON_PATH${NC}"
    echo "Please install Python or update PYTHON_PATH in this script"
    exit 1
fi

# Set FRED API key environment variable if provided
if [ ! -z "$FRED_API_KEY" ]; then
    echo -e "${YELLOW}Setting FRED_API_KEY environment variable${NC}"
    echo "export FRED_API_KEY=$FRED_API_KEY" >> ~/.bashrc
    export FRED_API_KEY=$FRED_API_KEY
fi

echo -e "${YELLOW}Creating cron jobs...${NC}"

# Weekly data updates (Mondays at 2:00 AM)
add_cron_job "0 2 * * 1" "scripts/manage_scheduler.py update --all" "Weekly data updates"

# Data health check (Daily at 1:00 AM)  
add_cron_job "0 1 * * *" "scripts/manage_scheduler.py freshness" "Daily health check"

# Monthly comprehensive update (First day of month at 3:00 AM)
add_cron_job "0 3 1 * *" "scripts/manage_scheduler.py update --all" "Monthly comprehensive update"

echo -e "${GREEN}Cron jobs setup complete!${NC}"

echo -e "${YELLOW}Current cron jobs:${NC}"
crontab -l

echo -e "${YELLOW}To manage cron jobs:${NC}"
echo "- View jobs: crontab -l"
echo "- Edit jobs: crontab -e"
echo "- Remove all jobs: crontab -r"

echo -e "${YELLOW}To test the setup:${NC}"
echo "cd $PROJECT_PATH"
echo "$PYTHON_PATH scripts/manage_scheduler.py status"

echo -e "${GREEN}Setup complete! Your data will now update automatically.${NC}"