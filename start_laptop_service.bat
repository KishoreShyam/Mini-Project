@echo off
echo.
echo ========================================
echo 🚀 STARTING LAPTOP SERVICE FOR MOBILE
echo ========================================
echo.

echo 🔧 Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo 📦 Installing required packages...
pip install flask flask-cors psutil requests

echo.
echo 🚀 Starting unified laptop service...
echo 📋 This service provides:
echo    • Direct IP connection for mobile app
echo    • Firebase cloud connection (if configured)
echo    • Web interface at http://localhost:8080
echo    • Mobile web app at http://localhost:8080/mobile.html
echo.

python laptop_service.py

pause