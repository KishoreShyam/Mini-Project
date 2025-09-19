@echo off
echo 📱 FLUTTER INSTALLATION HELPER
echo ===============================

echo This script will help you install Flutter for building the mobile app.
echo.

:: Check if Flutter is already installed
flutter --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Flutter is already installed!
    flutter --version
    echo.
    echo You can now run: build_mobile_app.bat
    pause
    exit /b 0
)

echo ❌ Flutter not found. Let's install it!
echo.

echo 📋 INSTALLATION STEPS:
echo.
echo 1. 📥 Download Flutter SDK:
echo    https://docs.flutter.dev/get-started/install/windows
echo.
echo 2. 📂 Extract to C:\flutter (recommended)
echo.
echo 3. 🔧 Add to PATH:
echo    - Open System Properties ^> Environment Variables
echo    - Add C:\flutter\bin to PATH
echo.
echo 4. 📱 Install Android Studio:
echo    https://developer.android.com/studio
echo.
echo 5. ✅ Verify installation:
echo    Open new Command Prompt and run: flutter doctor
echo.

set /p choice="Would you like to open the Flutter download page? (y/n): "
if /i "%choice%"=="y" (
    start https://docs.flutter.dev/get-started/install/windows
)

echo.
echo 📝 Quick Setup Summary:
echo 1. Download Flutter SDK
echo 2. Extract to C:\flutter
echo 3. Add C:\flutter\bin to PATH
echo 4. Install Android Studio
echo 5. Run: flutter doctor
echo 6. Run: build_mobile_app.bat
echo.

pause
