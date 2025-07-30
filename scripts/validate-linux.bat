@echo off
REM Windows batch script for Linux compatibility validation
REM Usage: scripts\validate-linux.bat

echo 🐧 Starting Linux compatibility validation...
echo.

REM Build the test container
echo 📦 Building Linux test container...
docker build -f Dockerfile.test -t proforma-linux-test . 

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker build failed!
    exit /b 1
)

echo.
echo ✅ Linux test container built successfully!
echo.
echo 🎯 All validation steps completed during build process.
echo    Your code is ready for Linux deployment!
echo.