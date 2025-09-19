@echo off
echo.
echo ========================================
echo 📱 SECURITY MOBILE APP INSTALLER
echo ========================================
echo.
echo 🔧 Building latest APK...
cd /d "E:\Mini Project\mobile_app"
flutter build apk --release

echo.
echo ✅ APK built successfully!
echo.
echo 📍 APK Location:
echo    E:\Mini Project\mobile_app\build\app\outputs\flutter-apk\app-release.apk
echo.
echo 📱 INSTALLATION STEPS:
echo    1. Copy app-release.apk to your phone
echo    2. Uninstall old "Security Control" app first
echo    3. Install the new APK
echo    4. The app will have the settings gear icon ⚙️
echo.
echo 🚀 Features in new version:
echo    • Fixed IP address (192.168.29.43)
echo    • Settings screen to change IP
echo    • Better connection handling
echo.
pause
