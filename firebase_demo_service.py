"""
Firebase Demo Service - Simplified version for college demo
This version uses a public demo Firebase database for testing
"""

import time
import threading
import json
import os
import subprocess
import sys
from datetime import datetime

# Try to import Firebase, install if needed
try:
    import firebase_admin
    from firebase_admin import credentials, db
except ImportError:
    print("📦 Installing Firebase Admin...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'firebase-admin'])
    import firebase_admin
    from firebase_admin import credentials, db

try:
    import psutil
except ImportError:
    print("📦 Installing psutil...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
    import psutil

class FirebaseDemoService:
    def __init__(self):
        self.device_id = f"laptop_{int(time.time())}"
        self.is_running = True
        self.database_url = "https://security-control-demo-default-rtdb.firebaseio.com/"  # Your actual Firebase URL
        
    def initialize_firebase(self):
        """Initialize Firebase with demo configuration"""
        try:
            if not firebase_admin._apps:
                # Initialize with demo database URL
                firebase_admin.initialize_app({
                    'databaseURL': self.database_url
                })
            
            print(f"🔥 Firebase initialized for device: {self.device_id}")
            print(f"🌐 Database URL: {self.database_url}")
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            print("📋 Please create a Firebase project and update the database URL")
            print("📋 Follow the instructions in QUICK_FIREBASE_SETUP.md")
            return False
    
    def update_laptop_status(self):
        """Update laptop status in Firebase"""
        try:
            ref = db.reference('laptop_status')
            ref.set({
                'status': 'online',
                'last_seen': int(time.time() * 1000),
                'device_id': self.device_id,
                'os': 'Windows',
                'version': '1.0.0',
                'ip_address': self.get_local_ip()
            })
            print(f"💓 Status updated at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Error updating status: {e}")
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"
    
    def execute_command(self, command_data, command_key):
        """Execute received command"""
        try:
            command = command_data.get('command', '')
            data = command_data.get('data', {})
            source = command_data.get('source', 'unknown')
            
            print(f"🔧 Executing command: {command} from {source}")
            
            response = {
                'command_key': command_key,
                'timestamp': int(time.time() * 1000),
                'status': 'executed',
                'result': '',
                'device_id': self.device_id
            }
            
            if command == 'shutdown':
                print("🚨 EMERGENCY SHUTDOWN INITIATED!")
                delay = data.get('delay', 10)
                print(f"⏰ Shutting down in {delay} seconds...")
                
                # Show countdown
                for i in range(delay, 0, -1):
                    print(f"🔴 Shutdown in {i} seconds... (Press Ctrl+C to cancel)")
                    time.sleep(1)
                
                # Execute shutdown
                subprocess.run(['shutdown', '/s', '/f', '/t', '0'], shell=True)
                response['result'] = f'Shutdown executed after {delay}s delay'
                    
            elif command == 'lock':
                print("🔒 LOCKING SYSTEM")
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
                response['result'] = 'System locked successfully'
                
            elif command == 'status':
                print("📊 GETTING SYSTEM STATUS")
                status_info = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('C:').percent,
                    'uptime': time.time()
                }
                response['result'] = status_info
                print(f"📊 System Status: CPU {status_info['cpu_percent']}%, RAM {status_info['memory_percent']}%")
                
            elif command == 'test_alert':
                print("🧪 TEST ALERT RECEIVED")
                message = data.get('message', 'Test alert')
                print(f"📨 Alert message: {message}")
                response['result'] = 'Test alert received and processed'
                
            else:
                print(f"❓ Unknown command: {command}")
                response['status'] = 'error'
                response['result'] = f'Unknown command: {command}'
            
            # Send response back to Firebase
            responses_ref = db.reference('command_responses')
            responses_ref.child(command_key).set(response)
            
            # Mark command as processed
            commands_ref = db.reference('commands')
            commands_ref.child(command_key).update({'status': 'processed'})
            
            return True
            
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return False
    
    def listen_for_commands(self):
        """Listen for new commands from Firebase"""
        try:
            commands_ref = db.reference('commands')
            
            def command_listener(event):
                try:
                    # Get all commands
                    snapshot = commands_ref.get()
                    if snapshot:
                        for command_key, command_data in snapshot.items():
                            if isinstance(command_data, dict) and command_data.get('status') == 'pending':
                                print(f"📨 New command received: {command_data.get('command')}")
                                self.execute_command(command_data, command_key)
                except Exception as e:
                    print(f"❌ Error in command listener: {e}")
            
            # Check for commands every 5 seconds
            def periodic_check():
                while self.is_running:
                    try:
                        command_listener(None)
                        time.sleep(5)
                    except Exception as e:
                        print(f"❌ Error in periodic check: {e}")
                        time.sleep(10)
            
            # Start periodic checking in a separate thread
            check_thread = threading.Thread(target=periodic_check, daemon=True)
            check_thread.start()
            
            print("👂 Listening for commands from mobile app...")
            
        except Exception as e:
            print(f"❌ Error setting up command listener: {e}")
    
    def start_heartbeat(self):
        """Start heartbeat thread to update status regularly"""
        def heartbeat():
            while self.is_running:
                try:
                    self.update_laptop_status()
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    print(f"❌ Heartbeat error: {e}")
                    time.sleep(60)
        
        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()
        print("💓 Heartbeat started (30s interval)")
    
    def run(self):
        """Main service loop"""
        print("🚀 FIREBASE DEMO SERVICE")
        print("=" * 50)
        print(f"🔗 Database URL: {self.database_url}")
        print("📋 To set up your own Firebase project:")
        print("   1. Go to https://console.firebase.google.com/")
        print("   2. Create a project")
        print("   3. Enable Realtime Database")
        print("   4. Update the database_url in this file")
        print("=" * 50)
        
        # Initialize Firebase
        if not self.initialize_firebase():
            print("❌ Failed to initialize Firebase.")
            print("📋 Please follow QUICK_FIREBASE_SETUP.md")
            input("Press Enter to exit...")
            return
        
        # Start heartbeat
        self.start_heartbeat()
        
        # Start listening for commands
        self.listen_for_commands()
        
        print("✅ Service started successfully!")
        print("📱 Mobile app should now show 'Laptop Connected (Firebase)'")
        print("🔥 Firebase connection established")
        print("💡 Press Ctrl+C to stop the service")
        print("=" * 50)
        
        try:
            # Keep the service running
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Service stopped by user")
            self.is_running = False

def main():
    """Main entry point"""
    try:
        service = FirebaseDemoService()
        service.run()
    except Exception as e:
        print(f"❌ Service error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
