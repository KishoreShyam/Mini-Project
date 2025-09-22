@echo off
echo.
echo ========================================
echo 🌐 SECURITY WEB APP LAUNCHER
echo ========================================
echo.

echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

echo 📦 Installing web dependencies...
python -m pip install flask flask-cors requests

echo.
echo 🚀 Starting Security Web App...
echo.
echo 📋 Web App Features:
echo    • 🔐 Token-based authentication
echo    • 🔴 Remote shutdown capability
echo    • 🔒 System lock controls
echo    • 📊 Real-time status monitoring
echo    • 🔥 Firebase integration
echo    • 📱 Mobile app compatibility
echo.
echo 🌐 Access at: http://localhost:5000
echo 📞 Emergency Phone: 8015339335
echo.

python security_web_app.py

echo.
pause
