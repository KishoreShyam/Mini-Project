"""
Simple Web Server for Security System
Uses built-in Python http.server - no external dependencies
"""

import http.server
import socketserver
import json
import urllib.parse
import subprocess
import time
import os
import secrets
import hashlib
from datetime import datetime, timedelta

# Configuration
PORT = 5000
USER_PHONE = "8015339335"
SECRET_KEY = "security_system_2024"

# Simple in-memory storage
active_tokens = {}
security_logs = []
failed_attempts = 0

def generate_token():
    """Generate a simple secure token"""
    return secrets.token_hex(16)

def log_event(event_type, message, severity="info"):
    """Log security events"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'message': message,
        'severity': severity
    }
    security_logs.append(log_entry)
    print(f"📝 {event_type}: {message}")

class SecurityHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/login':
            self.serve_login()
        elif path == '/api/shutdown':
            self.handle_shutdown(query)
        elif path == '/api/lock':
            self.handle_lock(query)
        elif path == '/api/status':
            self.handle_status(query)
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/login':
            self.handle_login_post()
        elif self.path == '/api/generate_token':
            self.handle_generate_token()
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
        """Serve main dashboard"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔒 Security Control Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; text-align: center; }}
        .card {{ background: white; padding: 25px; border-radius: 10px; margin: 20px 0; }}
        .btn {{ padding: 15px 25px; margin: 10px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-danger {{ background: #dc3545; color: white; }}
        .btn-warning {{ background: #ffc107; color: black; }}
        .status-online {{ color: #28a745; font-weight: bold; }}
        .status-warning {{ color: #ffc107; font-weight: bold; }}
        .status-critical {{ color: #dc3545; font-weight: bold; }}
        .token-display {{ background: #2c3e50; color: white; padding: 15px; border-radius: 5px; font-family: monospace; word-break: break-all; }}
        .log-entry {{ padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; background: #f8f9fa; }}
        .log-warning {{ border-left-color: #ffc107; }}
        .log-critical {{ border-left-color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security Control Dashboard</h1>
            <p>Advanced Security System - Real-time Monitoring & Control</p>
            <p><strong>📞 Emergency Contact:</strong> {USER_PHONE}</p>
        </div>
        
        <div class="card">
            <h2>🛡️ System Status</h2>
            <div class="status-online">✅ ONLINE & MONITORING</div>
            <p>Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Failed Attempts: <span class="{'status-critical' if failed_attempts >= 3 else 'status-warning' if failed_attempts > 0 else 'status-online'}">{failed_attempts}/3</span></p>
        </div>
        
        <div class="card">
            <h2>🔐 Authentication</h2>
            <p>Generate secure tokens for remote control</p>
            <button class="btn btn-primary" onclick="location.href='/login'">🔓 LOGIN & GET TOKEN</button>
            <button class="btn btn-primary" onclick="generateToken()">🎫 GENERATE API TOKEN</button>
            <div id="token-result"></div>
        </div>
        
        <div class="card">
            <h2>🚨 Emergency Controls</h2>
            <p>Use these controls for immediate security actions</p>
            <button class="btn btn-danger" onclick="emergencyAction('shutdown')">🔴 EMERGENCY SHUTDOWN</button>
            <button class="btn btn-warning" onclick="emergencyAction('lock')">🔒 LOCK SYSTEM</button>
            <button class="btn btn-primary" onclick="getStatus()">📊 GET STATUS</button>
        </div>
        
        <div class="card">
            <h2>📋 Recent Security Logs</h2>
            <div id="logs">
                {"".join([f'<div class="log-entry log-{log["severity"]}"><strong>{log["event_type"]}</strong>: {log["message"]}<br><small>{log["timestamp"][:19]}</small></div>' for log in security_logs[-5:]])}
            </div>
            <button class="btn btn-primary" onclick="location.reload()">🔄 REFRESH</button>
        </div>
    </div>
    
    <script>
        async function generateToken() {{
            const username = prompt('Enter username:');
            const password = prompt('Enter password:');
            
            if (!username || !password) return;
            
            try {{
                const response = await fetch('/api/generate_token', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ username, password }})
                }});
                
                const result = await response.json();
                
                if (result.status === 'success') {{
                    document.getElementById('token-result').innerHTML = `
                        <h3>✅ Token Generated</h3>
                        <div class="token-display">${{result.token}}</div>
                        <p><strong>Expires:</strong> ${{result.expires_in}}</p>
                    `;
                }} else {{
                    alert('❌ ' + result.message);
                }}
            }} catch (error) {{
                alert('❌ Error: ' + error.message);
            }}
        }}
        
        function emergencyAction(action) {{
            const token = prompt(`Enter your authentication token for ${{action.toUpperCase()}}:`);
            if (!token) return;
            
            if (action === 'shutdown') {{
                if (confirm('⚠️ Are you sure you want to SHUTDOWN the laptop?')) {{
                    executeAction(action, token);
                }}
            }} else {{
                executeAction(action, token);
            }}
        }}
        
        async function executeAction(action, token) {{
            try {{
                const response = await fetch(`/api/${{action}}?token=${{token}}`);
                const result = await response.json();
                
                if (result.status === 'success') {{
                    alert('✅ ' + result.message);
                    if (action === 'shutdown') {{
                        document.body.innerHTML = '<div style="text-align:center;padding:50px;font-size:24px;color:#dc3545;">🔴 LAPTOP SHUTTING DOWN...</div>';
                    }}
                }} else {{
                    alert('❌ ' + result.message);
                }}
            }} catch (error) {{
                alert('❌ Error: ' + error.message);
            }}
        }}
        
        async function getStatus() {{
            const token = prompt('Enter your authentication token:');
            if (!token) return;
            
            try {{
                const response = await fetch(`/api/status?token=${{token}}`);
                const result = await response.json();
                
                if (result.status === 'success') {{
                    const data = result.data;
                    alert(`📊 SYSTEM STATUS\\n\\nStatus: ${{data.status}}\\nTime: ${{data.timestamp}}\\nFailed Attempts: ${{data.failed_attempts}}\\nActive Tokens: ${{data.active_tokens}}`);
                }} else {{
                    alert('❌ ' + result.message);
                }}
            }} catch (error) {{
                alert('❌ Error: ' + error.message);
            }}
        }}
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_login(self):
        """Serve login page"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>🔐 Security System Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); width: 400px; text-align: center; }
        .form-group { margin: 20px 0; text-align: left; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: bold; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; }
        .btn { width: 100%; padding: 15px; background: #007bff; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        .demo-creds { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔐 Security System</h1>
        <p>Authentication Required</p>
        
        <div class="demo-creds">
            <h4>🧪 Demo Credentials</h4>
            <p><strong>Username:</strong> admin</p>
            <p><strong>Password:</strong> security123</p>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label>👤 Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>🔑 Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">🔓 LOGIN & GENERATE TOKEN</button>
        </form>
        
        <p><a href="/">← Back to Dashboard</a></p>
    </div>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_login_post(self):
        """Handle login form submission"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = urllib.parse.parse_qs(post_data)
        
        username = form_data.get('username', [''])[0]
        password = form_data.get('password', [''])[0]
        
        if username == 'admin' and password == 'security123':
            token = generate_token()
            expires_at = int((datetime.now() + timedelta(minutes=30)).timestamp())
            
            active_tokens[token] = {
                'user_id': username,
                'expires_at': expires_at,
                'permissions': ['shutdown', 'lock', 'status']
            }
            
            log_event("login_success", f"User {username} logged in")
            
            # Show token page
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🎫 Authentication Token</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; }}
        .token-display {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; font-family: monospace; word-break: break-all; margin: 20px 0; }}
        .btn {{ padding: 15px 25px; margin: 10px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; background: #007bff; color: white; }}
        .code-block {{ background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ Authentication Successful!</h1>
        <p>Your secure token has been generated</p>
        
        <h3>🎫 Your Authentication Token:</h3>
        <div class="token-display">{token}</div>
        <p><strong>⏰ Expires:</strong> 30 minutes from now</p>
        
        <h3>🔧 API Usage Examples:</h3>
        <h4>🔴 Emergency Shutdown:</h4>
        <div class="code-block">GET http://localhost:{PORT}/api/shutdown?token={token}</div>
        
        <h4>🔒 Lock System:</h4>
        <div class="code-block">GET http://localhost:{PORT}/api/lock?token={token}</div>
        
        <h4>📊 Get Status:</h4>
        <div class="code-block">GET http://localhost:{PORT}/api/status?token={token}</div>
        
        <button class="btn" onclick="navigator.clipboard.writeText('{token}').then(() => alert('✅ Token copied!'))">📋 COPY TOKEN</button>
        <button class="btn" onclick="location.href='/'">🏠 BACK TO DASHBOARD</button>
    </div>
</body>
</html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            global failed_attempts
            failed_attempts += 1
            log_event("login_failed", f"Failed login attempt for {username}", "warning")
            
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
    
    def handle_generate_token(self):
        """Handle API token generation"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)
        
        username = data.get('username')
        password = data.get('password')
        
        if username == 'admin' and password == 'security123':
            token = generate_token()
            expires_at = int((datetime.now() + timedelta(minutes=30)).timestamp())
            
            active_tokens[token] = {
                'user_id': username,
                'expires_at': expires_at,
                'permissions': ['shutdown', 'lock', 'status']
            }
            
            response = {
                "status": "success",
                "token": token,
                "expires_in": "30 minutes"
            }
        else:
            response = {
                "status": "error",
                "message": "Invalid credentials"
            }
        
        self.send_json_response(response)
    
    def verify_token(self, token):
        """Verify if token is valid"""
        if token in active_tokens:
            token_data = active_tokens[token]
            if token_data['expires_at'] > int(time.time()):
                return True, token_data
            else:
                del active_tokens[token]
                return False, "Token expired"
        return False, "Invalid token"
    
    def handle_shutdown(self, query):
        """Handle shutdown request"""
        token = query.get('token', [''])[0]
        valid, token_data = self.verify_token(token)
        
        if valid:
            try:
                log_event("shutdown_initiated", f"Shutdown requested by user: {token_data['user_id']}", "critical")
                subprocess.run(['shutdown', '/s', '/f', '/t', '10'], shell=True)
                
                response = {
                    "status": "success",
                    "message": "✅ Laptop is shutting down in 10 seconds...",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                response = {
                    "status": "error",
                    "message": f"❌ Shutdown failed: {str(e)}"
                }
        else:
            response = {
                "status": "error",
                "message": "❌ Invalid or expired token"
            }
        
        self.send_json_response(response)
    
    def handle_lock(self, query):
        """Handle lock request"""
        token = query.get('token', [''])[0]
        valid, token_data = self.verify_token(token)
        
        if valid:
            try:
                log_event("lock_initiated", f"Lock requested by user: {token_data['user_id']}")
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
                
                response = {
                    "status": "success",
                    "message": "✅ Laptop locked successfully",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                response = {
                    "status": "error",
                    "message": f"❌ Lock failed: {str(e)}"
                }
        else:
            response = {
                "status": "error",
                "message": "❌ Invalid or expired token"
            }
        
        self.send_json_response(response)
    
    def handle_status(self, query):
        """Handle status request"""
        token = query.get('token', [''])[0]
        valid, token_data = self.verify_token(token)
        
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
            
            response = {
                "status": "success",
                "data": status_data
            }
        else:
            response = {
                "status": "error",
                "message": "❌ Invalid or expired token"
            }
        
        self.send_json_response(response)
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def main():
    """Start the simple web server"""
    print("🚀 SIMPLE SECURITY WEB SERVER")
    print("=" * 50)
    print(f"🌐 Web Interface: http://localhost:{PORT}")
    print(f"📞 Emergency Phone: {USER_PHONE}")
    print("🔐 Demo Login: admin / security123")
    print("=" * 50)
    
    log_event("web_server_started", "Simple security web server started")
    
    with socketserver.TCPServer(("", PORT), SecurityHandler) as httpd:
        print(f"✅ Server running on port {PORT}")
        print("💡 Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            log_event("web_server_stopped", "Web server stopped by user")

if __name__ == "__main__":
    main()
