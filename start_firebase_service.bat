@echo off
echo.
echo ========================================
echo 🔥 STARTING FIREBASE LAPTOP SERVICE
echo ========================================
echo.

echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

echo 🚀 Starting Firebase service...
echo 📋 Instructions:
echo    1. Create Firebase project at https://console.firebase.google.com/
echo    2. Enable Realtime Database in test mode
echo    3. Update database URL in firebase_demo_service.py
echo    4. Install updated mobile APK
echo.

python firebase_demo_service.py

pause
