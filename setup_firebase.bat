@echo off
echo.
echo ========================================
echo 🔥 FIREBASE SETUP FOR LAPTOP SERVICE
echo ========================================
echo.

echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

echo 📦 Installing Firebase dependencies...
pip install firebase-admin psutil

echo.
echo ✅ Firebase dependencies installed!
echo.
echo 📋 NEXT STEPS:
echo    1. Set up Firebase project (see firebase_setup_instructions.md)
echo    2. Update database URL in firebase_laptop_service.py
echo    3. Run: python firebase_laptop_service.py
echo.
pause
