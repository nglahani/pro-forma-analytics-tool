#!/bin/bash
# Cross-platform Development Environment Setup Script
# For Pro-Forma Analytics Tool

set -e  # Exit on any error

echo "========================================"
echo "Pro-Forma Analytics Development Setup"
echo "========================================"

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo "ERROR: Docker is not running"
    echo "Please start Docker and run this script again"
    exit 1
fi

echo "Docker is running ✓"

# Navigate to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "Building development containers..."
docker-compose build

echo "Containers built successfully ✓"

echo "Starting development environment..."
docker-compose up -d

echo ""
echo "========================================"
echo "Development Environment Ready! 🎉"
echo "========================================"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:      docker-compose down"
echo ""