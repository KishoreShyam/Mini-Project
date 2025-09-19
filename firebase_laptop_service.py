"""
Firebase Laptop Service - Listens for remote commands from mobile app
This service runs on the laptop and executes commands received via Firebase Realtime Database
"""

import firebase_admin
from firebase_admin import credentials, db
import os
import subprocess
import time
import threading
import json
from datetime import datetime
import sys

class FirebaseLaptopService:
    def __init__(self):
        self.device_id = f"laptop_{int(time.time())}"
        self.is_running = True
        self.commands_ref = None
        self.status_ref = None
        
    def initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # For now, we'll use a simple approach without service account
                # In production, you should use proper service account credentials
                print("⚠️  Using Firebase without service account (demo mode)")
                print("📋 For production, add your service account key file")
                
                # Initialize with default credentials (requires Firebase CLI setup)
                try:
                    firebase_admin.initialize_app({
                        'databaseURL': 'https://your-project-default-rtdb.firebaseio.com/'
                    })
                except Exception as e:
                    print(f"❌ Firebase initialization failed: {e}")
                    print("📋 Please set up Firebase project and update database URL")
                    return False
            
            # Get database references
            self.commands_ref = db.reference('commands')
            self.status_ref = db.reference('laptop_status')
            self.responses_ref = db.reference('command_responses')
            
            print(f"🔥 Firebase initialized for device: {self.device_id}")
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            return False
    
    def update_laptop_status(self):
        """Update laptop status in Firebase"""
        try:
            if self.status_ref:
                self.status_ref.set({
                    'status': 'online',
                    'last_seen': int(time.time() * 1000),  # Milliseconds
                    'device_id': self.device_id,
                    'os': 'Windows',
                    'version': '1.0.0'
                })
        except Exception as e:
            print(f"❌ Error updating status: {e}")
    
    def execute_command(self, command_data):
        """Execute received command"""
        try:
            command = command_data.get('command', '')
            data = command_data.get('data', {})
            command_id = command_data.get('device_id', 'unknown')
            
            print(f"🔧 Executing command: {command}")
            
            response = {
                'command_id': command_id,
                'timestamp': int(time.time() * 1000),
                'status': 'executed',
                'result': ''
            }
            
            if command == 'shutdown':
                print("🚨 EMERGENCY SHUTDOWN INITIATED")
                delay = data.get('delay', 10)
                force = data.get('force', True)
                
                if force:
                    # Immediate forced shutdown
                    subprocess.run(['shutdown', '/s', '/f', '/t', str(delay)], shell=True)
                    response['result'] = f'Shutdown initiated with {delay}s delay'
                else:
                    # Regular shutdown
                    subprocess.run(['shutdown', '/s', '/t', str(delay)], shell=True)
                    response['result'] = f'Shutdown scheduled in {delay}s'
                    
            elif command == 'lock':
                print("🔒 LOCKING SYSTEM")
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
                response['result'] = 'System locked successfully'
                
            elif command == 'status':
                print("📊 GETTING SYSTEM STATUS")
                # Get system information
                import platform
                import psutil
                
                status_info = {
                    'os': platform.system(),
                    'os_version': platform.version(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('C:').percent if os.name == 'nt' else psutil.disk_usage('/').percent
                }
                response['result'] = status_info
                
            elif command == 'test_alert':
                print("🧪 TEST ALERT RECEIVED")
                # Show a notification or log
                response['result'] = 'Test alert received successfully'
                
            else:
                print(f"❓ Unknown command: {command}")
                response['status'] = 'error'
                response['result'] = f'Unknown command: {command}'
            
            # Send response back to Firebase
            if self.responses_ref:
                self.responses_ref.child(command_id).set(response)
                
            return True
            
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return False
    
    def listen_for_commands(self):
        """Listen for new commands from Firebase"""
        def command_callback(event):
            try:
                if event.data:
                    # Process new command
                    command_data = event.data
                    if isinstance(command_data, dict) and command_data.get('status') == 'pending':
                        print(f"📨 New command received: {command_data.get('command')}")
                        
                        # Execute the command
                        success = self.execute_command(command_data)
                        
                        # Mark command as processed
                        if event.path and self.commands_ref:
                            command_key = event.path.split('/')[-1]
                            self.commands_ref.child(command_key).update({'status': 'processed'})
                            
            except Exception as e:
                print(f"❌ Error processing command: {e}")
        
        # Listen for new commands
        if self.commands_ref:
            self.commands_ref.listen(command_callback)
            print("👂 Listening for commands from mobile app...")
        else:
            print("❌ Commands reference not initialized")
    
    def start_heartbeat(self):
        """Start heartbeat thread to update status regularly"""
        def heartbeat():
            while self.is_running:
                self.update_laptop_status()
                time.sleep(30)  # Update every 30 seconds
        
        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()
        print("💓 Heartbeat started")
    
    def run(self):
        """Main service loop"""
        print("🚀 FIREBASE LAPTOP SERVICE")
        print("=" * 40)
        
        # Initialize Firebase
        if not self.initialize_firebase():
            print("❌ Failed to initialize Firebase. Exiting.")
            return
        
        # Start heartbeat
        self.start_heartbeat()
        
        # Start listening for commands
        self.listen_for_commands()
        
        print("✅ Service started successfully!")
        print("📱 Mobile app can now send commands")
        print("🔥 Firebase connection established")
        print("💡 Press Ctrl+C to stop the service")
        print("=" * 40)
        
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
        # Install required packages if not present
        try:
            import firebase_admin
            import psutil
        except ImportError as e:
            print(f"❌ Missing required package: {e}")
            print("📦 Installing required packages...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'firebase-admin', 'psutil'])
            print("✅ Packages installed successfully!")
            
        # Start the service
        service = FirebaseLaptopService()
        service.run()
        
    except Exception as e:
        print(f"❌ Service error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
