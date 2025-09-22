@echo off
echo.
echo ========================================
echo 🔒 COMPLETE SECURITY SYSTEM LAUNCHER
echo ========================================
echo.

echo 🎯 Available Security Applications:
echo.
echo 1. 🖥️  Desktop Security App (Main System)
echo 2. 📱 Mobile Alert Simulator  
echo 3. 🌐 Web Security Interface
echo 4. 🔥 Firebase Service Monitor
echo 5. 🎓 Basic Security System (Training)
echo 6. 🚀 Launch ALL Systems
echo.

set /p choice="Select option (1-6): "

if "%choice%"=="1" (
    echo 🖥️ Starting Desktop Security Application...
    echo.
    echo 📋 Features:
    echo    • Modern GUI interface
    echo    • Keystroke biometric authentication  
    echo    • Camera capture on failed attempts
    echo    • Mobile alert integration
    echo    • Emergency shutdown capability
    echo.
    python security_desktop_app.py
    
) else if "%choice%"=="2" (
    echo 📱 Starting Mobile Alert Simulator...
    echo.
    echo 📋 Features:
    echo    • Simulates mobile app alerts
    echo    • Emergency shutdown controls
    echo    • Real-time Firebase monitoring
    echo    • Cross-network communication
    echo.
    python mobile_alert_simulator.py
    
) else if "%choice%"=="3" (
    echo 🌐 Starting Web Security Interface...
    echo.
    echo 📋 Features:
    echo    • Professional web dashboard
    echo    • Token-based authentication
    echo    • API endpoints for mobile
    echo    • Real-time monitoring
    echo.
    python simple_web_server.py
    
) else if "%choice%"=="4" (
    echo 🔥 Starting Firebase Service Monitor...
    echo.
    echo 📋 Features:
    echo    • Background Firebase monitoring
    echo    • Cross-network command processing
    echo    • Real-time status updates
    echo    • Emergency command execution
    echo.
    python firebase_security_service.py
    
) else if "%choice%"=="5" (
    echo 🎓 Starting Basic Security System...
    echo.
    echo 📋 Features:
    echo    • Keystroke pattern training
    echo    • Authentication testing
    echo    • Security event logging
    echo    • Emergency alert simulation
    echo.
    python basic_security_system.py
    
) else if "%choice%"=="6" (
    echo 🚀 Launching ALL Security Systems...
    echo.
    echo ⚠️ This will open multiple windows:
    echo    • Desktop Security App
    echo    • Mobile Alert Simulator  
    echo    • Web Interface
    echo    • Firebase Monitor
    echo.
    
    set /p confirm="Continue? (y/n): "
    if /i "%confirm%"=="y" (
        echo 🖥️ Starting Desktop Security App...
        start "Desktop Security" python security_desktop_app.py
        timeout /t 2 /nobreak >nul
        
        echo 📱 Starting Mobile Alert Simulator...
        start "Mobile Simulator" python mobile_alert_simulator.py
        timeout /t 2 /nobreak >nul
        
        echo 🌐 Starting Web Interface...
        start "Web Interface" python simple_web_server.py
        timeout /t 2 /nobreak >nul
        
        echo 🔥 Starting Firebase Monitor...
        start "Firebase Monitor" python firebase_security_service.py
        
        echo.
        echo ✅ All systems launched successfully!
        echo 📋 Access points:
        echo    • Desktop App: Main security interface
        echo    • Mobile Sim: http://localhost (mobile alerts)
        echo    • Web Interface: http://localhost:5000
        echo    • Firebase: Background monitoring
        echo.
        echo 🎓 Perfect for college demonstration!
    ) else (
        echo ❌ Launch cancelled
    )
    
) else (
    echo ❌ Invalid choice!
)

echo.
echo 📞 Emergency Contact: 8015339335
echo 🔥 Firebase URL: https://security-control-demo-default-rtdb.firebaseio.com
echo.
pause
