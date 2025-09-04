@echo off
echo ===============================================
echo    Pro-Forma Analytics Application Startup
echo ===============================================
echo.

cd /d "%~dp0"

echo Starting Backend API Server...
echo Backend will be available at: http://localhost:8000
echo.
start "Backend API" cmd /k "python -m uvicorn src.presentation.api.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Development Server...
echo Frontend will be available at: http://localhost:3000 (or next available port)
echo.
start "Frontend Dev Server" cmd /k "cd frontend && set DISABLE_SWC=1 && set TURBOPACK=0 && set NEXT_TELEMETRY_DISABLED=1 && npm run dev"

echo.
echo ===============================================
echo    Application Started Successfully!
echo ===============================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:3000
echo.
echo Both servers are running in separate windows.
echo Close those windows or press Ctrl+C in them to stop the servers.
echo.
echo This window can be closed safely.
echo.
pause