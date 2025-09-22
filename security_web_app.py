"""
Security Web App - Flask Application with Firebase Integration
Features:
- Token-based authentication
- Remote shutdown and lock
- Security monitoring
- Keystroke authentication API
- Real-time alerts
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os
import time
import subprocess
import threading
from datetime import datetime, timedelta
import hashlib
import secrets
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
FIREBASE_URL = "https://security-control-demo-default-rtdb.firebaseio.com"
USER_PHONE = "8015339335"
SECRET_KEY = "security_system_2024"

# In-memory storage for demo (in production, use Firebase)
active_tokens = {}
security_logs = []
failed_attempts = 0
max_attempts = 3

def generate_secure_token():
    """Generate a secure token for authentication"""
    return secrets.token_urlsafe(32)

def create_token(user_id, expires_in_minutes=30):
    """Create a new authentication token"""
    token = generate_secure_token()
    expires_at = int((datetime.now() + timedelta(minutes=expires_in_minutes)).timestamp() * 1000)
    
    token_data = {
        'user_id': user_id,
        'created_at': int(time.time() * 1000),
        'expires_at': expires_at,
        'permissions': ['shutdown', 'lock', 'status']
    }
    
    # Store in memory (in production, store in Firebase)
    active_tokens[token] = token_data
    
    # Also store in Firebase for mobile app access
    try:
        response = requests.put(
            f"{FIREBASE_URL}/tokens/{token}.json",
            json=token_data,
            timeout=10
        )
        if response.status_code == 200:
            log_security_event("token_created", f"Token created for user: {user_id}")
    except Exception as e:
        print(f"Error storing token in Firebase: {e}")
    
    return token

def verify_token(token):
    """Verify if token is valid and not expired"""
    if not token:
        return False, "No token provided"
    
    # Check local storage first
    if token in active_tokens:
        token_data = active_tokens[token]
        if token_data['expires_at'] > int(time.time() * 1000):
            return True, token_data
        else:
            # Token expired, remove it
            del active_tokens[token]
            return False, "Token expired"
    
    # Check Firebase as fallback
    try:
        response = requests.get(f"{FIREBASE_URL}/tokens/{token}.json", timeout=5)
        if response.status_code == 200 and response.json():
            token_data = response.json()
            if token_data.get('expires_at', 0) > int(time.time() * 1000):
                active_tokens[token] = token_data  # Cache locally
                return True, token_data
            else:
                return False, "Token expired"
    except Exception as e:
        print(f"Error verifying token: {e}")
    
    return False, "Invalid token"

def log_security_event(event_type, message, severity="info"):
    """Log security events"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'message': message,
        'severity': severity,
        'ip_address': request.remote_addr if request else 'system'
    }
    
    security_logs.append(log_entry)
    
    # Keep only last 100 logs in memory
    if len(security_logs) > 100:
        security_logs.pop(0)
    
    # Also send to Firebase
    try:
        requests.post(
            f"{FIREBASE_URL}/security_logs.json",
            json=log_entry,
            timeout=5
        )
    except Exception as e:
        print(f"Error logging to Firebase: {e}")

def send_security_alert(alert_type, message, severity="high"):
    """Send security alert to Firebase and mobile"""
    alert_data = {
        'type': alert_type,
        'message': message,
        'severity': severity,
        'timestamp': int(time.time() * 1000),
        'phone': USER_PHONE,
        'source': 'web_app',
        'action_required': True
    }
    
    try:
        response = requests.post(
            f"{FIREBASE_URL}/security_alerts.json",
            json=alert_data,
            timeout=10
        )
        
        if response.status_code == 200:
            log_security_event("alert_sent", f"{alert_type}: {message}", "critical")
            return True
    except Exception as e:
        print(f"Error sending alert: {e}")
    
    return False

# Web Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('security_dashboard.html', 
                         logs=security_logs[-10:], 
                         failed_attempts=failed_attempts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with token generation"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (in production, use proper auth)
        if username == "admin" and password == "security123":
            token = create_token(username)
            log_security_event("login_success", f"User {username} logged in")
            return render_template('token_display.html', token=token)
        else:
            global failed_attempts
            failed_attempts += 1
            log_security_event("login_failed", f"Failed login attempt for {username}", "warning")
            
            if failed_attempts >= max_attempts:
                send_security_alert("security_breach", 
                                  f"Multiple failed login attempts from {request.remote_addr}")
            
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

# API Routes
@app.route('/api/shutdown')
def api_shutdown():
    """Shutdown laptop with token authentication"""
    token = request.args.get('token')
    
    valid, token_data = verify_token(token)
    
    if valid:
        try:
            log_security_event("shutdown_initiated", f"Shutdown requested by user: {token_data['user_id']}", "critical")
            send_security_alert("emergency_shutdown", "Laptop shutdown initiated via web API")
            
            # Execute shutdown
            subprocess.run(['shutdown', '/s', '/f', '/t', '10'], shell=True)
            
            return jsonify({
                "status": "success",
                "message": "✅ Laptop is shutting down in 10 seconds...",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            log_security_event("shutdown_failed", f"Shutdown failed: {str(e)}", "error")
            return jsonify({
                "status": "error",
                "message": f"❌ Shutdown failed: {str(e)}"
            }), 500
    else:
        log_security_event("unauthorized_shutdown", f"Invalid token used for shutdown from {request.remote_addr}", "warning")
        return jsonify({
            "status": "error",
            "message": "❌ Invalid or expired token"
        }), 401

@app.route('/api/lock')
def api_lock():
    """Lock laptop with token authentication"""
    token = request.args.get('token')
    
    valid, token_data = verify_token(token)
    
    if valid:
        try:
            log_security_event("lock_initiated", f"Lock requested by user: {token_data['user_id']}")
            
            # Execute lock
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
            
            return jsonify({
                "status": "success",
                "message": "✅ Laptop locked successfully",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"❌ Lock failed: {str(e)}"
            }), 500
    else:
        return jsonify({
            "status": "error",
            "message": "❌ Invalid or expired token"
        }), 401

@app.route('/api/status')
def api_status():
    """Get system status"""
    token = request.args.get('token')
    
    valid, token_data = verify_token(token)
    
    if valid:
        status_data = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "failed_attempts": failed_attempts,
            "active_tokens": len(active_tokens),
            "recent_logs": len(security_logs),
            "system_info": {
                "platform": os.name,
                "user": os.getenv('USERNAME', 'unknown')
            }
        }
        
        return jsonify({
            "status": "success",
            "data": status_data
        })
    else:
        return jsonify({
            "status": "error",
            "message": "❌ Invalid or expired token"
        }), 401

@app.route('/api/generate_token', methods=['POST'])
def api_generate_token():
    """Generate new token via API"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Simple authentication
    if username == "admin" and password == "security123":
        token = create_token(username)
        return jsonify({
            "status": "success",
            "token": token,
            "expires_in": "30 minutes"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        }), 401

@app.route('/api/logs')
def api_logs():
    """Get security logs"""
    token = request.args.get('token')
    
    valid, token_data = verify_token(token)
    
    if valid:
        return jsonify({
            "status": "success",
            "logs": security_logs[-20:]  # Last 20 logs
        })
    else:
        return jsonify({
            "status": "error",
            "message": "❌ Invalid or expired token"
        }), 401

@app.route('/api/emergency_command', methods=['POST'])
def api_emergency_command():
    """Handle emergency commands from mobile app"""
    data = request.get_json()
    command = data.get('command')
    phone = data.get('phone')
    emergency_key = data.get('emergency_key')
    
    # Verify emergency key (simple check)
    expected_key = hashlib.sha256(f"{USER_PHONE}{SECRET_KEY}".encode()).hexdigest()[:16]
    
    if phone == USER_PHONE and emergency_key == expected_key:
        if command == 'SHUTDOWN':
            log_security_event("emergency_shutdown", f"Emergency shutdown from mobile: {phone}", "critical")
            subprocess.run(['shutdown', '/s', '/f', '/t', '5'], shell=True)
            return jsonify({"status": "success", "message": "Emergency shutdown initiated"})
        
        elif command == 'LOCK':
            log_security_event("emergency_lock", f"Emergency lock from mobile: {phone}")
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
            return jsonify({"status": "success", "message": "System locked"})
        
        else:
            return jsonify({"status": "error", "message": "Unknown command"}), 400
    else:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

# Background monitoring
def start_background_monitoring():
    """Start background monitoring for Firebase commands"""
    def monitor_firebase():
        while True:
            try:
                # Check for emergency commands
                response = requests.get(f"{FIREBASE_URL}/emergency_commands.json", timeout=5)
                
                if response.status_code == 200 and response.json():
                    commands = response.json()
                    
                    for cmd_id, cmd_data in commands.items():
                        if isinstance(cmd_data, dict):
                            command = cmd_data.get('command', '')
                            phone = cmd_data.get('phone', '')
                            status = cmd_data.get('status', '')
                            timestamp = cmd_data.get('timestamp', 0)
                            
                            # Check if command is recent and pending
                            if (phone == USER_PHONE and 
                                status == 'pending' and 
                                timestamp > (time.time() - 300) * 1000):  # 5 minutes
                                
                                if command == 'SHUTDOWN':
                                    log_security_event("firebase_shutdown", "Shutdown command from Firebase", "critical")
                                    subprocess.run(['shutdown', '/s', '/f', '/t', '10'], shell=True)
                                    
                                    # Mark as processed
                                    requests.patch(
                                        f"{FIREBASE_URL}/emergency_commands/{cmd_id}.json",
                                        json={'status': 'processed'},
                                        timeout=5
                                    )
                
                # Update system status
                status_data = {
                    'status': 'online',
                    'last_seen': int(time.time() * 1000),
                    'web_app_active': True,
                    'failed_attempts': failed_attempts
                }
                
                requests.put(
                    f"{FIREBASE_URL}/laptop_status.json",
                    json=status_data,
                    timeout=5
                )
                
            except Exception as e:
                print(f"Background monitoring error: {e}")
            
            time.sleep(10)  # Check every 10 seconds
    
    monitor_thread = threading.Thread(target=monitor_firebase, daemon=True)
    monitor_thread.start()

if __name__ == '__main__':
    print("🚀 SECURITY WEB APP STARTING")
    print("=" * 50)
    print(f"🌐 Web Interface: http://localhost:5000")
    print(f"📞 Emergency Phone: {USER_PHONE}")
    print(f"🔥 Firebase URL: {FIREBASE_URL}")
    print("=" * 50)
    
    # Start background monitoring
    start_background_monitoring()
    
    # Log startup
    log_security_event("web_app_started", "Security web app started")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
