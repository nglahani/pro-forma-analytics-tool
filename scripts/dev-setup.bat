@echo off
REM Windows Development Environment Setup Script
REM For Pro-Forma Analytics Tool

echo ========================================
echo Pro-Forma Analytics Development Setup
echo ========================================

REM Check if Docker Desktop is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is not running
    echo Please start Docker Desktop and run this script again
    pause
    exit /b 1
)

echo Docker Desktop is running ✓

REM Navigate to project directory
cd /d C:\Development\pro-forma-analytics-tool

echo Building development containers...
docker-compose build

if %errorlevel% neq 0 (
    echo ERROR: Failed to build containers
    pause
    exit /b 1
)

echo Containers built successfully ✓

echo Starting development environment...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start containers
    pause
    exit /b 1
)

echo.
echo ========================================
echo Development Environment Ready! 🎉
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.
pause