"""
Web Server for Keystroke Security System
Serves the modern web-based interface with mobile alert integration
"""

import http.server
import socketserver
import webbrowser
import os
import threading
import time
import json
import urllib.parse
from mobile_alert_backend import MobileAlertSystem
from keystroke_storage import KeystrokeStorage

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="web_app", **kwargs)
        if not hasattr(self.__class__, 'alert_system'):
            self.__class__.alert_system = MobileAlertSystem()
        if not hasattr(self.__class__, 'keystroke_storage'):
            self.__class__.keystroke_storage = KeystrokeStorage("main_user")
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('ETag', f'"{hash(str(time.time()))}"')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
        
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.end_headers()
        
    def do_POST(self):
        """Handle POST requests for API endpoints"""
        if self.path.startswith('/api/alert/'):
            self.handle_alert_api()
        else:
            super().do_POST()
            
    def handle_alert_api(self):
        """Handle mobile alert API requests"""
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            # Route API calls
            if self.path == '/api/alert/test':
                self.handle_test_alert(data)
            elif self.path == '/api/alert/breach':
                self.handle_security_breach(data)
            elif self.path == '/api/alert/status':
                self.handle_get_status()
            elif self.path == '/api/keystroke/save':
                self.handle_save_keystroke_session(data)
            elif self.path == '/api/keystroke/train':
                self.handle_train_model(data)
            elif self.path == '/api/keystroke/authenticate':
                self.handle_authenticate_typing(data)
            elif self.path == '/api/keystroke/stats':
                self.handle_get_keystroke_stats()
            elif self.path == '/api/remote/command':
                self.handle_remote_command(data)
            else:
                self.send_error(404, "API endpoint not found")
                
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def handle_test_alert(self, data):
        """Handle alert testing"""
        alert_type = data.get('type', 'all')
        
        try:
            if alert_type == 'alarm':
                # Test alarm in background
                def run_alarm():
                    self.alert_system.play_emergency_alarm(5)
                alarm_thread = threading.Thread(target=run_alarm)
                alarm_thread.daemon = True
                alarm_thread.start()
                response = {"success": True, "message": "🚨 Alarm test started (5 seconds)"}
                
            elif alert_type == 'sms':
                result = self.alert_system.send_sms_alert("🧪 Test SMS from security system")
                response = {"success": result, "message": "SMS test completed"}
                
            elif alert_type == 'email':
                result = self.alert_system.send_email_alert("🧪 Test Email", "This is a test email from your security system")
                response = {"success": result, "message": "Email test completed"}
                
            elif alert_type == 'call':
                result = self.alert_system.make_emergency_call()
                response = {"success": result, "message": "Emergency call test completed"}
                
            elif alert_type == 'camera':
                photo_path = self.alert_system.capture_intruder_photo()
                response = {"success": bool(photo_path), "photo_path": photo_path, "message": "Camera test completed"}
                
            else:  # Test all systems
                def run_full_test():
                    self.alert_system.test_alert_system()
                test_thread = threading.Thread(target=run_full_test)
                test_thread.daemon = True
                test_thread.start()
                response = {"success": True, "message": "Full system test started"}
                
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def handle_security_breach(self, data):
        """Handle security breach alert"""
        try:
            breach_details = data.get('details', {})
            
            def run_breach_alert():
                self.alert_system.trigger_security_breach_alert(breach_details)
                
            # Run in background
            breach_thread = threading.Thread(target=run_breach_alert)
            breach_thread.daemon = True
            breach_thread.start()
            
            response = {
                "success": True,
                "message": "🚨 Security breach alert triggered!",
                "mobile_number": self.alert_system.mobile_number,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def handle_get_status(self):
        """Get alert system status"""
        try:
            response = {
                "success": True,
                "status": {
                    "mobile_number": self.alert_system.mobile_number,
                    "pygame_available": self.alert_system.pygame_available,
                    "services_ready": {
                        "alarm": self.alert_system.pygame_available,
                        "camera": True,
                        "twilio": bool(self.alert_system.config["twilio"]["account_sid"]),
                        "sms": bool(self.alert_system.config["fast2sms"]["api_key"]),
                        "email": bool(self.alert_system.config["email"]["email"]),
                        "push": bool(self.alert_system.config["pushbullet"]["api_key"])
                    }
                }
            }
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def handle_save_keystroke_session(self, data):
        """Save keystroke training session"""
        try:
            session_id = self.keystroke_storage.save_keystroke_session(data)
            response = {
                "success": True,
                "message": f"Training session {session_id} saved successfully",
                "session_id": session_id,
                "total_sessions": len(self.keystroke_storage.load_all_sessions())
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def handle_train_model(self, data):
        """Train the typing pattern recognition model"""
        try:
            success = self.keystroke_storage.train_model()
            if success:
                stats = self.keystroke_storage.get_user_stats()
                response = {
                    "success": True,
                    "message": "Model trained successfully!",
                    "accuracy": stats["profile"]["model_accuracy"],
                    "is_trained": stats["profile"]["is_trained"]
                }
            else:
                response = {
                    "success": False,
                    "message": "Model training failed. Need at least 3 training sessions."
                }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def handle_authenticate_typing(self, data):
        """Authenticate user based on typing pattern"""
        try:
            is_authentic, confidence = self.keystroke_storage.authenticate_typing(data)
            response = {
                "success": True,
                "is_authentic": is_authentic,
                "confidence": confidence,
                "message": "Authentication completed"
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def handle_get_keystroke_stats(self):
        """Get keystroke statistics and user profile"""
        try:
            stats = self.keystroke_storage.get_user_stats()
            response = {
                "success": True,
                "stats": stats
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def handle_remote_command(self, data):
        """Handle remote commands from mobile app"""
        try:
            command = data.get("command")
            command_data = data.get("data", {})
            source = data.get("source", "unknown")
            
            print(f"🚨 Remote command received: {command} from {source}")
            
            if command == "shutdown":
                self._execute_remote_shutdown(command_data)
            elif command == "lock":
                self._execute_remote_lock(command_data)
            elif command == "status":
                self._send_remote_status(command_data)
            elif command == "alert":
                self._handle_remote_alert(command_data)
            else:
                self.send_json_response({"success": False, "error": "Unknown command"}, 400)
                return
                
            response = {
                "success": True,
                "message": f"Command '{command}' executed successfully",
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
            
    def _execute_remote_shutdown(self, data):
        """Execute remote shutdown command"""
        import subprocess
        import platform
        
        delay = data.get("delay", 10)
        reason = data.get("reason", "Remote shutdown")
        
        print(f"🔴 EXECUTING REMOTE SHUTDOWN - Delay: {delay}s")
        print(f"📝 Reason: {reason}")
        
        system = platform.system().lower()
        
        def shutdown_system():
            time.sleep(2)  # Brief delay for response
            try:
                if system == "windows":
                    subprocess.run(["shutdown", "/s", "/f", "/t", str(delay)], check=True)
                elif system == "darwin":  # macOS
                    subprocess.run(["sudo", "shutdown", "-h", f"+{delay//60 or 1}"], check=True)
                elif system == "linux":
                    subprocess.run(["sudo", "shutdown", "-h", f"+{delay//60 or 1}"], check=True)
            except Exception as e:
                print(f"❌ Shutdown failed: {e}")
                
        # Execute shutdown in background
        import threading
        shutdown_thread = threading.Thread(target=shutdown_system, daemon=True)
        shutdown_thread.start()
        
    def _execute_remote_lock(self, data):
        """Execute remote lock command"""
        import subprocess
        import platform
        
        reason = data.get("reason", "Remote lock")
        print(f"🔒 EXECUTING REMOTE LOCK")
        print(f"📝 Reason: {reason}")
        
        system = platform.system().lower()
        
        def lock_system():
            time.sleep(1)
            try:
                if system == "windows":
                    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
                elif system == "darwin":
                    subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"], check=True)
                elif system == "linux":
                    subprocess.run(["xdg-screensaver", "lock"], check=True)
            except Exception as e:
                print(f"❌ Lock failed: {e}")
                
        import threading
        lock_thread = threading.Thread(target=lock_system, daemon=True)
        lock_thread.start()
        
    def _send_remote_status(self, data):
        """Send system status"""
        import platform
        
        status_info = {
            "hostname": platform.node(),
            "platform": platform.system(),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "uptime": "System running"
        }
        print(f"📊 Status requested: {status_info}")
        
    def _handle_remote_alert(self, data):
        """Handle remote alert"""
        alert_message = data.get("alert_message", "Test alert")
        priority = data.get("priority", "normal")
        
        print(f"🚨 Remote alert: {alert_message} (Priority: {priority})")
        
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        response_data = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.end_headers()
        self.wfile.write(response_data)

def start_server():
    """Start the web server"""
    PORT = 8080
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("🚀 KEYSTROKE SECURITY WEB APP")
            print("=" * 40)
            print(f"🌐 Server running at: http://localhost:{PORT}")
            print(f"📱 Opening in your default browser...")
            print("=" * 40)
            print("✨ Features:")
            print("  • Beautiful animations and transitions")
            print("  • Modern glassmorphism design")
            print("  • Interactive training interface")
            print("  • Real-time typing statistics")
            print("  • Smooth hover effects")
            print("  • Floating particles background")
            print("=" * 40)
            print("Press Ctrl+C to stop the server")
            print()
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(1.5)
                webbrowser.open(f'http://localhost:{PORT}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print("Try stopping other web servers or use a different port.")
        else:
            print(f"❌ Error starting server: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        print("👋 Goodbye!")

if __name__ == "__main__":
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if web_app directory exists
    if not os.path.exists("web_app"):
        print("❌ web_app directory not found!")
        print("Please make sure the web_app folder exists with index.html")
        exit(1)
    
    start_server()
