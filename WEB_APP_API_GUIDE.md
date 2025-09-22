# 🌐 Security Web App API Guide

## 🚀 Complete Flask Web Application

Your security system now includes a professional web application with:

### 🔥 **Key Features:**
- **🔐 Token-based Authentication** - Secure API access
- **🔴 Remote Shutdown** - Emergency laptop shutdown via web/mobile
- **🔒 System Lock** - Remote screen lock capability
- **📊 Real-time Monitoring** - Live system status and logs
- **🔥 Firebase Integration** - Cross-network communication
- **📱 Mobile Compatibility** - Works with your mobile app

## 🛠️ Quick Start

### **1. Start the Web App:**
```bash
# Run the launcher
start_web_app.bat

# Or manually
python security_web_app.py
```

### **2. Access Web Interface:**
- **URL**: http://localhost:5000
- **Login**: admin / security123
- **Emergency Phone**: 8015339335

## 🔐 Authentication System

### **Login & Token Generation:**
```
POST /login
- Username: admin
- Password: security123
- Returns: Secure 30-minute token
```

### **API Token Generation:**
```
POST /api/generate_token
Content-Type: application/json

{
  "username": "admin",
  "password": "security123"
}

Response:
{
  "status": "success",
  "token": "secure_token_here",
  "expires_in": "30 minutes"
}
```

## 🚨 Emergency API Endpoints

### **1. 🔴 Emergency Shutdown**
```
GET /api/shutdown?token=YOUR_TOKEN

Response:
{
  "status": "success",
  "message": "✅ Laptop is shutting down in 10 seconds...",
  "timestamp": "2024-01-01T12:00:00"
}
```

### **2. 🔒 Lock System**
```
GET /api/lock?token=YOUR_TOKEN

Response:
{
  "status": "success",
  "message": "✅ Laptop locked successfully",
  "timestamp": "2024-01-01T12:00:00"
}
```

### **3. 📊 Get System Status**
```
GET /api/status?token=YOUR_TOKEN

Response:
{
  "status": "success",
  "data": {
    "status": "online",
    "timestamp": "2024-01-01T12:00:00",
    "failed_attempts": 0,
    "active_tokens": 1,
    "system_info": {
      "platform": "nt",
      "user": "YourUsername"
    }
  }
}
```

### **4. 📋 Get Security Logs**
```
GET /api/logs?token=YOUR_TOKEN

Response:
{
  "status": "success",
  "logs": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "event_type": "login_success",
      "message": "User admin logged in",
      "severity": "info",
      "ip_address": "127.0.0.1"
    }
  ]
}
```

## 📱 Mobile App Integration

### **Emergency Command API:**
```
POST /api/emergency_command
Content-Type: application/json

{
  "command": "SHUTDOWN",
  "phone": "8015339335",
  "emergency_key": "generated_emergency_key"
}

Commands:
- SHUTDOWN: Emergency laptop shutdown
- LOCK: Lock laptop screen
```

## 🔥 Firebase Integration

### **Real-time Communication:**
- **Database URL**: https://security-control-demo-default-rtdb.firebaseio.com
- **Emergency Commands**: `/emergency_commands`
- **System Status**: `/laptop_status`
- **Security Alerts**: `/security_alerts`

### **Background Monitoring:**
- Checks Firebase every 10 seconds
- Processes emergency commands automatically
- Updates system status in real-time
- Sends alerts to mobile app

## 🎯 Usage Examples

### **Web Dashboard:**
1. **Open**: http://localhost:5000
2. **Login**: admin / security123
3. **Get Token**: Copy secure authentication token
4. **Emergency Controls**: Use token for shutdown/lock

### **Mobile App Integration:**
1. **Generate Token**: Via web login or API
2. **Configure Mobile**: Enter token in mobile app settings
3. **Emergency Use**: Mobile app sends commands via Firebase
4. **Cross-Network**: Works when laptop/mobile on different networks

### **Direct API Calls:**
```bash
# Get token
curl -X POST http://localhost:5000/api/generate_token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"security123"}'

# Emergency shutdown
curl "http://localhost:5000/api/shutdown?token=YOUR_TOKEN"

# Lock system
curl "http://localhost:5000/api/lock?token=YOUR_TOKEN"

# Get status
curl "http://localhost:5000/api/status?token=YOUR_TOKEN"
```

## 🔒 Security Features

### **Token Security:**
- **32-byte secure tokens** using `secrets.token_urlsafe()`
- **30-minute expiration** for security
- **Firebase storage** for cross-device access
- **Permission-based** access control

### **Request Logging:**
- **All API calls logged** with timestamps
- **IP address tracking** for security audits
- **Failed attempt monitoring** with breach detection
- **Real-time alerts** for suspicious activity

### **Emergency Response:**
- **Immediate shutdown** capability (10-second countdown)
- **Cross-network commands** via Firebase
- **Mobile app integration** for remote control
- **Phone alerts** to 8015339335

## 🎓 Perfect for College Demo

### **Demo Scenario:**
1. **Setup**: Laptop on college WiFi, mobile on data
2. **Web Login**: Show professional web interface
3. **Token Generation**: Demonstrate secure authentication
4. **Mobile Integration**: Show cross-network communication
5. **Emergency Shutdown**: Execute remote shutdown via mobile
6. **Real-time Monitoring**: Show live logs and status
7. **Audience Amazed**: Professional cybersecurity system! 🎉

### **Technical Highlights:**
- **Professional Web Interface** with modern UI
- **RESTful API Design** with proper HTTP methods
- **Token-based Authentication** for security
- **Cross-platform Compatibility** (web, mobile, API)
- **Real-time Communication** via Firebase
- **Emergency Response System** with multiple triggers

## 🌐 Web Interface Features

### **Dashboard:**
- **Real-time Status** monitoring
- **Security Alerts** display
- **Activity Logs** with filtering
- **Emergency Controls** with confirmation

### **Authentication:**
- **Secure Login** with demo credentials
- **Token Display** with usage examples
- **API Documentation** built-in
- **Mobile Integration** instructions

### **Emergency Controls:**
- **One-click Shutdown** with confirmation
- **System Lock** capability
- **Status Monitoring** in real-time
- **Log Viewing** with refresh

## 📞 Emergency Integration

**Your Phone**: 8015339335
- **Web App Alerts**: Automatic notifications
- **Firebase Commands**: Cross-network control
- **Mobile App**: Direct integration
- **API Access**: Token-based security

---

**🚀 You now have a complete, professional-grade security web application that integrates with your mobile app and Firebase for comprehensive remote control capabilities!**

**Perfect for demonstrating advanced web development, API design, security implementation, and cross-platform integration skills!** 🎉
