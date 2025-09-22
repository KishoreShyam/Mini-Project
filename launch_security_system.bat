@echo off
echo.
echo ========================================
echo 🔒 ADVANCED SECURITY SYSTEM LAUNCHER
echo ========================================
echo.

echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

echo 📦 Installing security dependencies...
pip install -r security_requirements.txt

echo.
echo 🚀 SECURITY SYSTEM OPTIONS:
echo.
echo 1. 🔐 Advanced Security System (Keystroke + Camera + Alerts)
echo 2. 🔥 Firebase Security Service (Background monitoring)
echo 3. 📱 SMS Command Handler (Emergency commands)
echo 4. 🌐 Web Interface (Browser control)
echo 5. 📱 Mobile App Builder (Flutter build)
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo 🔐 Starting Advanced Security System...
    python advanced_security_system.py
) else if "%choice%"=="2" (
    echo 🔥 Starting Firebase Security Service...
    python firebase_security_service.py
) else if "%choice%"=="3" (
    echo 📱 Starting SMS Command Handler...
    python sms_command_handler.py
) else if "%choice%"=="4" (
    echo 🌐 Starting Web Interface...
    python web_server.py
) else if "%choice%"=="5" (
    echo 📱 Building Mobile App...
    cd mobile_app
    flutter pub get
    flutter build apk --release
    echo ✅ APK built: build\app\outputs\flutter-apk\app-release.apk
    cd ..
) else (
    echo ❌ Invalid choice!
)

echo.
pause
