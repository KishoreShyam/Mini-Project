@echo off
echo.
echo ========================================
echo 📱 INSTALL NEW FIREBASE-ENABLED APK
echo ========================================
echo.

echo 🔍 Checking if new APK exists...
if exist "mobile_app\build\app\outputs\flutter-apk\app-release.apk" (
    echo ✅ New APK found!
    echo.
    echo 📍 APK Location:
    echo    %CD%\mobile_app\build\app\outputs\flutter-apk\app-release.apk
    echo.
    echo 📱 INSTALLATION STEPS:
    echo    1. UNINSTALL old "Security Control" app from phone first
    echo    2. Copy app-release.apk to your phone
    echo    3. Install the new APK
    echo    4. Open app - should show Firebase connection
    echo.
    echo 🎯 Expected Result:
    echo    • "🔥 Firebase Connected" (blue status)
    echo    • "✅ Laptop Connected (Firebase)" (green status)
    echo    • Activity log shows Firebase initialization
    echo.
    echo 📂 Opening APK folder...
    explorer "mobile_app\build\app\outputs\flutter-apk\"
) else (
    echo ❌ APK not found. Build may still be in progress.
    echo 📋 Run: flutter build apk --release
    echo    in the mobile_app directory
)

echo.
pause
