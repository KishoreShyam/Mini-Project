@echo off
echo 🔒 BUILDING SECURITY CONTROL MOBILE APP
echo ========================================

:: Check if Flutter is installed
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flutter is not installed or not in PATH
    echo 📥 Please install Flutter from: https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

echo ✅ Flutter detected
echo.

:: Navigate to mobile app directory
cd /d "e:\Mini Project\mobile_app"

echo 📦 Getting Flutter dependencies...
flutter pub get

if %errorlevel% neq 0 (
    echo ❌ Failed to get dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

echo 🔨 Building APK (Release)...
flutter build apk --release

if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo.
echo 🎉 BUILD SUCCESSFUL!
echo ========================================
echo 📱 APK Location: build\app\outputs\flutter-apk\app-release.apk
echo.
echo 📋 Installation Instructions:
echo 1. Transfer the APK to your Android phone
echo 2. Enable "Install from unknown sources" in phone settings
echo 3. Tap the APK file to install
echo 4. Open the "Security Control" app
echo 5. Configure your laptop's IP address in settings
echo.
echo 🔍 APK Size: 
for %%A in (build\app\outputs\flutter-apk\app-release.apk) do echo %%~zA bytes

echo.
echo ✅ Ready to install on your Android phone!
pause
