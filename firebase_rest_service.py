"""
Firebase REST Service - Uses Firebase REST API instead of Admin SDK
This works without service account credentials for demo purposes
"""

import time
import threading
import json
import os
import subprocess
import sys
import requests
from datetime import datetime

try:
    import psutil
except ImportError:
    print("📦 Installing psutil...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
    import psutil

class FirebaseRestService:
    def __init__(self):
        self.device_id = f"laptop_{int(time.time())}"
        self.is_running = True
        self.base_url = "https://security-control-demo-default-rtdb.firebaseio.com"
        self.last_command_check = 0
        
    def test_connection(self):
        """Test Firebase connection"""
        try:
            response = requests.get(f"{self.base_url}/.json", timeout=10)
            if response.status_code == 200:
                print(f"🔥 Firebase connection successful!")
                print(f"🌐 Database URL: {self.base_url}")
                return True
            else:
                print(f"❌ Firebase connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Firebase connection error: {e}")
            return False
    
    def update_laptop_status(self):
        """Update laptop status in Firebase"""
        try:
            status_data = {
                'status': 'online',
                'last_seen': int(time.time() * 1000),
                'device_id': self.device_id,
                'os': 'Windows',
                'version': '1.0.0',
                'ip_address': self.get_local_ip()
            }
            
            response = requests.put(
                f"{self.base_url}/laptop_status.json",
                json=status_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"💓 Status updated at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"❌ Status update failed: {response.status_code}")
                
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
            
            response_data = {
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
                for i in range(min(delay, 10), 0, -1):
                    print(f"🔴 Shutdown in {i} seconds... (Press Ctrl+C to cancel)")
                    time.sleep(1)
                
                # Execute shutdown
                subprocess.run(['shutdown', '/s', '/f', '/t', '0'], shell=True)
                response_data['result'] = f'Shutdown executed after {delay}s delay'
                    
            elif command == 'lock':
                print("🔒 LOCKING SYSTEM")
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
                response_data['result'] = 'System locked successfully'
                
            elif command == 'status':
                print("📊 GETTING SYSTEM STATUS")
                status_info = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('C:').percent,
                    'uptime': time.time()
                }
                response_data['result'] = status_info
                print(f"📊 System Status: CPU {status_info['cpu_percent']}%, RAM {status_info['memory_percent']}%")
                
            elif command == 'test_alert':
                print("🧪 TEST ALERT RECEIVED")
                message = data.get('message', 'Test alert')
                print(f"📨 Alert message: {message}")
                response_data['result'] = 'Test alert received and processed'
                
            else:
                print(f"❓ Unknown command: {command}")
                response_data['status'] = 'error'
                response_data['result'] = f'Unknown command: {command}'
            
            # Send response back to Firebase
            requests.put(
                f"{self.base_url}/command_responses/{command_key}.json",
                json=response_data,
                timeout=10
            )
            
            # Mark command as processed
            requests.patch(
                f"{self.base_url}/commands/{command_key}.json",
                json={'status': 'processed'},
                timeout=10
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return False
    
    def check_for_commands(self):
        """Check for new commands from Firebase"""
        try:
            response = requests.get(f"{self.base_url}/commands.json", timeout=10)
            if response.status_code == 200 and response.json():
                commands = response.json()
                
                for command_key, command_data in commands.items():
                    if isinstance(command_data, dict) and command_data.get('status') == 'pending':
                        # Check if this is a new command
                        command_timestamp = command_data.get('timestamp', 0)
                        if command_timestamp > self.last_command_check:
                            print(f"📨 New command received: {command_data.get('command')}")
                            self.execute_command(command_data, command_key)
                
                # Update last check timestamp
                self.last_command_check = int(time.time() * 1000)
                
        except Exception as e:
            print(f"❌ Error checking commands: {e}")
    
    def start_monitoring(self):
        """Start monitoring for commands and updating status"""
        def monitor_loop():
            while self.is_running:
                try:
                    # Update status every 30 seconds
                    self.update_laptop_status()
                    
                    # Check for commands every 5 seconds
                    for _ in range(6):  # 6 * 5 = 30 seconds
                        if not self.is_running:
                            break
                        self.check_for_commands()
                        time.sleep(5)
                        
                except Exception as e:
                    print(f"❌ Monitor loop error: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        print("👂 Started monitoring for commands (5s interval)")
        print("💓 Started status updates (30s interval)")
    
    def run(self):
        """Main service loop"""
        print("🚀 FIREBASE REST SERVICE")
        print("=" * 50)
        print(f"🔗 Database URL: {self.base_url}")
        print("📋 Using Firebase REST API (no credentials needed)")
        print("=" * 50)
        
        # Test Firebase connection
        if not self.test_connection():
            print("❌ Failed to connect to Firebase.")
            print("📋 Please check:")
            print("   1. Internet connection")
            print("   2. Firebase project exists")
            print("   3. Realtime Database is enabled")
            input("Press Enter to exit...")
            return
        
        # Start monitoring
        self.start_monitoring()
        
        print("✅ Service started successfully!")
        print("📱 Mobile app should now show 'Laptop Connected (Firebase)'")
        print("🔥 Firebase REST connection established")
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
        service = FirebaseRestService()
        service.run()
    except Exception as e:
        print(f"❌ Service error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
