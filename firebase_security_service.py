"""
Enhanced Firebase Security Service
Integrates with advanced security system for real-time alerts and commands
"""

import time
import threading
import json
import os
import subprocess
import sys
import requests
from datetime import datetime
import base64
import cv2

class FirebaseSecurityService:
    def __init__(self):
        self.device_id = f"security_laptop_{int(time.time())}"
        self.is_running = True
        self.base_url = 'https://security-control-demo-default-rtdb.firebaseio.com'
        self.user_phone = "8015339335"
        self.last_command_check = 0
        
    def test_connection(self):
        """Test Firebase connection"""
        try:
            response = requests.get(f"{self.base_url}/.json", timeout=10)
            if response.status_code == 200:
                print(f"🔥 Firebase Security Service connected!")
                print(f"🌐 Database URL: {self.base_url}")
                return True
            else:
                print(f"❌ Firebase connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Firebase connection error: {e}")
            return False
    
    def update_security_status(self, status, message="", alert_level="normal"):
        """Update security status in Firebase"""
        try:
            status_data = {
                'status': status,
                'message': message,
                'alert_level': alert_level,
                'last_seen': int(time.time() * 1000),
                'device_id': self.device_id,
                'phone': self.user_phone,
                'location': 'Laptop Security System',
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.put(
                f"{self.base_url}/security_status.json",
                json=status_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"🔒 Security status updated: {status}")
            else:
                print(f"❌ Status update failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error updating status: {e}")
    
    def send_security_alert(self, alert_type, message, photo_path=None, severity="high"):
        """Send security alert to Firebase"""
        try:
            alert_data = {
                'type': alert_type,
                'message': message,
                'severity': severity,
                'timestamp': int(time.time() * 1000),
                'phone': self.user_phone,
                'device_id': self.device_id,
                'location': 'Laptop Security System',
                'action_required': True,
                'alert_id': f"alert_{int(time.time())}"
            }
            
            # Add photo if available
            if photo_path and os.path.exists(photo_path):
                try:
                    with open(photo_path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode()
                        # Limit size for Firebase
                        if len(img_data) < 100000:  # 100KB limit
                            alert_data['photo'] = img_data
                            alert_data['photo_filename'] = os.path.basename(photo_path)
                except Exception as e:
                    print(f"⚠️ Could not attach photo: {e}")
            
            # Send alert to Firebase
            response = requests.post(
                f"{self.base_url}/security_alerts.json",
                json=alert_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"🚨 Security alert sent: {alert_type}")
                
                # Also update mobile notification
                self.send_mobile_notification(alert_type, message)
                return True
            else:
                print(f"❌ Alert failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending alert: {e}")
            return False
    
    def send_mobile_notification(self, title, message):
        """Send immediate notification to mobile app"""
        try:
            notification_data = {
                'title': title,
                'message': message,
                'timestamp': int(time.time() * 1000),
                'phone': self.user_phone,
                'priority': 'high',
                'sound': True,
                'vibrate': True
            }
            
            response = requests.post(
                f"{self.base_url}/mobile_notifications.json",
                json=notification_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"📱 Mobile notification sent")
            
        except Exception as e:
            print(f"❌ Mobile notification error: {e}")
    
    def check_emergency_commands(self):
        """Check for emergency commands from mobile/SMS"""
        try:
            response = requests.get(f"{self.base_url}/emergency_commands.json", timeout=10)
            
            if response.status_code == 200 and response.json():
                commands = response.json()
                
                for command_key, command_data in commands.items():
                    if isinstance(command_data, dict):
                        command = command_data.get('command', '')
                        phone = command_data.get('phone', '')
                        status = command_data.get('status', '')
                        timestamp = command_data.get('timestamp', 0)
                        
                        # Check if command is for this phone and is pending
                        if (phone == self.user_phone and 
                            status == 'pending' and 
                            timestamp > self.last_command_check):
                            
                            print(f"📨 Emergency command received: {command}")
                            
                            # Execute command
                            success = self.execute_emergency_command(command, command_key)
                            
                            # Mark as processed
                            if success:
                                self.mark_command_processed(command_key)
                
                # Update last check timestamp
                self.last_command_check = int(time.time() * 1000)
                
        except Exception as e:
            print(f"❌ Error checking commands: {e}")
    
    def execute_emergency_command(self, command, command_key):
        """Execute emergency command"""
        try:
            if command == 'SHUTDOWN':
                print("🚨 EMERGENCY SHUTDOWN COMMAND RECEIVED!")
                self.update_security_status("shutdown_initiated", "Emergency shutdown in progress", "critical")
                
                # Countdown
                for i in range(10, 0, -1):
                    print(f"🔴 Emergency shutdown in {i} seconds...")
                    time.sleep(1)
                
                # Execute shutdown
                subprocess.run(['shutdown', '/s', '/f', '/t', '0'], shell=True)
                return True
                
            elif command == 'LOCK':
                print("🔒 EMERGENCY LOCK COMMAND RECEIVED!")
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
                self.update_security_status("locked", "System locked via emergency command", "high")
                return True
                
            elif command == 'STATUS':
                print("📊 STATUS REQUEST RECEIVED!")
                self.update_security_status("online", "Status requested via emergency command", "normal")
                return True
                
            elif command == 'ALERT':
                print("🧪 TEST ALERT COMMAND RECEIVED!")
                self.send_security_alert("test_alert", "Test alert via emergency command", severity="low")
                return True
                
            else:
                print(f"❓ Unknown emergency command: {command}")
                return False
                
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return False
    
    def mark_command_processed(self, command_key):
        """Mark command as processed"""
        try:
            response = requests.patch(
                f"{self.base_url}/emergency_commands/{command_key}.json",
                json={'status': 'processed', 'processed_at': int(time.time() * 1000)},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Command {command_key} marked as processed")
            
        except Exception as e:
            print(f"❌ Error marking command processed: {e}")
    
    def start_monitoring(self):
        """Start monitoring for commands and updating status"""
        def monitor_loop():
            while self.is_running:
                try:
                    # Update status every 30 seconds
                    self.update_security_status("monitoring", "Security system active")
                    
                    # Check for commands every 5 seconds
                    for _ in range(6):  # 6 * 5 = 30 seconds
                        if not self.is_running:
                            break
                        self.check_emergency_commands()
                        time.sleep(5)
                        
                except Exception as e:
                    print(f"❌ Monitor loop error: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        print("👂 Started monitoring for emergency commands")
        print("💓 Started security status updates")
    
    def run(self):
        """Main service loop"""
        print("🚀 FIREBASE SECURITY SERVICE")
        print("=" * 50)
        print(f"🔗 Database URL: {self.base_url}")
        print(f"📞 Emergency phone: {self.user_phone}")
        print("📋 Monitoring for emergency commands via Firebase")
        print("=" * 50)
        
        # Test Firebase connection
        if not self.test_connection():
            print("❌ Failed to connect to Firebase.")
            input("Press Enter to exit...")
            return
        
        # Start monitoring
        self.start_monitoring()
        
        print("✅ Security service started successfully!")
        print("📱 Mobile app can now send emergency commands")
        print("🔥 Firebase security connection established")
        print("💡 Press Ctrl+C to stop the service")
        print("=" * 50)
        
        try:
            # Keep the service running
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Security service stopped by user")
            self.is_running = False

def main():
    """Main entry point"""
    try:
        service = FirebaseSecurityService()
        service.run()
    except Exception as e:
        print(f"❌ Service error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
