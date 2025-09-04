@echo off
echo Starting Pro-Forma Analytics Frontend with OneDrive-safe settings...
echo.

cd /d "%~dp0frontend"

echo Setting OneDrive-safe environment variables...
set DISABLE_SWC=1
set TURBOPACK=0 
set NEXT_TELEMETRY_DISABLED=1
set WATCHPACK_POLLING=true
set CHOKIDAR_USEPOLLING=true
set NEXT_WEBPACK_USEPOLLING=1

echo.
echo Cleaning any locked files...
if exist .next (
    echo Attempting to remove .next directory...
    timeout /t 2 /nobreak >nul
    rd /s /q .next 2>nul
    if exist .next (
        echo Warning: Some .next files may be locked by OneDrive
        echo The application will still start but may have slower builds
    ) else (
        echo .next directory cleaned successfully
    )
)

echo.
echo Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000 (or next available port)
echo.
echo To stop the server, press Ctrl+C
echo.

npm run dev

echo.
echo Frontend server stopped.
pause