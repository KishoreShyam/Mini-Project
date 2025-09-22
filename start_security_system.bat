@echo off
echo.
echo ========================================
echo 🔒 KEYSTROKE BIOMETRIC SECURITY SYSTEM
echo ========================================
echo.

echo 🎯 SECURITY SYSTEM FEATURES:
echo.
echo ✅ System provides training texts automatically
echo ✅ Learns your unique typing patterns (biometrics)  
echo ✅ Blocks ALL system access until authenticated
echo ✅ NO security controls visible until verified
echo ✅ Activates mobile alerts after 3 failed attempts
echo ✅ Professional security barrier interface
echo.

echo 📋 HOW IT WORKS:
echo.
echo 1. 🎓 TRAINING: System gives you 5 texts to type
echo 2. 🔐 LEARNING: Analyzes your keystroke timing patterns
echo 3. 🚫 BLOCKING: Blocks system access completely
echo 4. ⌨️  AUTHENTICATION: Type provided text with your style
echo 5. 🚨 SECURITY: 3 failed attempts = mobile alert + shutdown
echo.

echo 📞 Emergency Contact: 8015339335
echo 🔥 Firebase Integration: Ready
echo.

set /p confirm="Start Security System? (y/n): "
if /i "%confirm%"=="y" (
    echo.
    echo 🔒 Starting Keystroke Biometric Security System...
    echo 🚫 System will be LOCKED until authentication
    echo.
    python keystroke_security_system.py
) else (
    echo ❌ Security system not started
)

echo.
pause
