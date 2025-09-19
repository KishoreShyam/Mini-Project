"""
Unified Laptop Service for Mobile App Connection
Supports both direct IP connection and Firebase cloud connection
"""

import time
import threading
import json
import os
import subprocess
import sys
import platform
from datetime import datetime
import socket
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Try to import Firebase, install if needed
try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    print("📦 Firebase not available - using direct connection mode")
    FIREBASE_AVAILABLE = False

try:
    import psutil
except ImportError:
    print("📦 Installing psutil...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
    import psutil

class UnifiedLaptopService:
    def __init__(self):
        self.device_id = f"laptop_{int(time.time())}"
        self.is_running = True
        self.firebase_enabled = False
        self.web_server_enabled = True
        
        # Firebase configuration
        self.firebase_url = "https://security-control-demo-default-rtdb.firebaseio.com/"
        
        # Flask app for direct connection
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_web_routes()
        
        # Get local IP
        self.local_ip = self.get_local_ip()
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def setup_web_routes(self):
        """Setup Flask routes for direct mobile app connection"""
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            return jsonify({
                "status": "online",
                "device_id": self.device_id,
                "timestamp": int(time.time() * 1000),
                "ip_address": self.local_ip,
                "os": platform.system(),
                "version": "2.0.0"
            })
        
        @self.app.route('/command', methods=['POST'])
        def execute_command():
            try:
                data = request.get_json()
                command = data.get('command')
                command_data = data.get('data', {})
                
                print(f"🔧 Received command: {command}")
                
                if command == 'shutdown':
                    return self.handle_shutdown(command_data)
                elif command == 'lock':
                    return self.handle_lock(command_data)
                elif command == 'status':
                    return self.handle_status_request(command_data)
                elif command == 'test_alert':
                    return self.handle_test_alert(command_data)
                else:
                    return jsonify({"success": False, "error": "Unknown command"})
                    
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        @self.app.route('/mobile.html')
        def serve_mobile_app():
            """Serve mobile web app"""
            return send_from_directory('web_app', 'mobile.html')
    
    def handle_shutdown(self, data):
        """Handle shutdown command"""
        try:
            delay = data.get('delay', 10)
            print(f"🚨 SHUTDOWN COMMAND RECEIVED - Delay: {delay}s")
            
            def execute_shutdown():
                time.sleep(2)  # Allow response to be sent
                try:
                    system = platform.system().lower()
                    if system == "windows":
                        subprocess.run(['shutdown', '/s', '/f', '/t', str(delay)], check=True)
                    elif system == "darwin":  # macOS
                        subprocess.run(['sudo', 'shutdown', '-h', f'+{delay//60 or 1}'], check=True)
                    elif system == "linux":
                        subprocess.run(['sudo', 'shutdown', '-h', f'+{delay//60 or 1}'], check=True)
                except Exception as e:
                    print(f"❌ Shutdown failed: {e}")
            
            # Execute in background
            shutdown_thread = threading.Thread(target=execute_shutdown, daemon=True)
            shutdown_thread.start()
            
            return jsonify({
                "success": True,
                "message": f"Shutdown initiated - {delay}s delay",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    def handle_lock(self, data):
        """Handle lock command"""
        try:
            print("🔒 LOCK COMMAND RECEIVED")
            
            def execute_lock():
                time.sleep(1)
                try:
                    system = platform.system().lower()
                    if system == "windows":
                        subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
                    elif system == "darwin":
                        subprocess.run(['pmset', 'displaysleepnow'], check=True)
                    elif system == "linux":
                        subprocess.run(['xdg-screensaver', 'lock'], check=True)
                except Exception as e:
                    print(f"❌ Lock failed: {e}")
            
            lock_thread = threading.Thread(target=execute_lock, daemon=True)
            lock_thread.start()
            
            return jsonify({
                "success": True,
                "message": "System lock initiated",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    def handle_status_request(self, data):
        """Handle status request"""
        try:
            status_info = {
                "device_id": self.device_id,
                "hostname": platform.node(),
                "platform": platform.system(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('C:' if os.name == 'nt' else '/').percent,
                "uptime": time.time(),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"📊 Status requested: CPU {status_info['cpu_percent']}%, RAM {status_info['memory_percent']}%")
            
            return jsonify({
                "success": True,
                "status": status_info,
                "message": "Status retrieved successfully"
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    def handle_test_alert(self, data):
        """Handle test alert"""
        message = data.get('message', 'Test alert from mobile app')
        print(f"🧪 TEST ALERT: {message}")
        
        return jsonify({
            "success": True,
            "message": "Test alert received and processed",
            "timestamp": datetime.now().isoformat()
        })
    
    def initialize_firebase(self):
        """Initialize Firebase if available"""
        if not FIREBASE_AVAILABLE:
            return False
            
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app({
                    'databaseURL': self.firebase_url
                })
            
            print(f"🔥 Firebase initialized: {self.firebase_url}")
            self.firebase_enabled = True
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            return False
    
    def update_firebase_status(self):
        """Update status in Firebase"""
        if not self.firebase_enabled:
            return
            
        try:
            ref = db.reference('laptop_status')
            ref.set({
                'status': 'online',
                'last_seen': int(time.time() * 1000),
                'device_id': self.device_id,
                'os': platform.system(),
                'version': '2.0.0',
                'ip_address': self.local_ip
            })
        except Exception as e:
            print(f"❌ Firebase status update failed: {e}")
    
    def start_firebase_monitoring(self):
        """Start Firebase command monitoring"""
        if not self.firebase_enabled:
            return
            
        def firebase_monitor():
            while self.is_running:
                try:
                    # Update status every 30 seconds
                    self.update_firebase_status()
                    time.sleep(30)
                except Exception as e:
                    print(f"❌ Firebase monitor error: {e}")
                    time.sleep(60)
        
        firebase_thread = threading.Thread(target=firebase_monitor, daemon=True)
        firebase_thread.start()
        print("🔥 Firebase monitoring started")
    
    def start_web_server(self):
        """Start Flask web server for direct connection"""
        def run_server():
            try:
                self.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
            except Exception as e:
                print(f"❌ Web server error: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        print(f"🌐 Web server started on {self.local_ip}:8080")
    
    def run(self):
        """Main service loop"""
        print("🚀 UNIFIED LAPTOP SERVICE")
        print("=" * 50)
        print(f"💻 Device ID: {self.device_id}")
        print(f"🌐 Local IP: {self.local_ip}")
        print(f"📱 Mobile can connect via:")
        print(f"   • Direct IP: http://{self.local_ip}:8080")
        print(f"   • Web App: http://{self.local_ip}:8080/mobile.html")
        
        # Try to initialize Firebase
        if self.initialize_firebase():
            print(f"   • Firebase: {self.firebase_url}")
            self.start_firebase_monitoring()
        else:
            print("   • Firebase: Not available (using direct connection)")
        
        # Start web server
        self.start_web_server()
        
        print("=" * 50)
        print("✅ Service started successfully!")
        print("📱 Mobile app should now show 'Laptop Connected'")
        print("💡 Press Ctrl+C to stop the service")
        print("=" * 50)
        
        try:
            # Keep service running
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Service stopped by user")
            self.is_running = False

def main():
    """Main entry point"""
    try:
        service = UnifiedLaptopService()
        service.run()
    except Exception as e:
        print(f"❌ Service error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()