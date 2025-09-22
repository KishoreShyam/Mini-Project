"""
SMS Command Handler for Emergency Security Actions
Allows user to send commands via SMS/Firebase to control laptop remotely
"""

import requests
import time
import subprocess
import json
from datetime import datetime
import threading

class SMSCommandHandler:
    def __init__(self):
        self.firebase_url = "https://security-control-demo-default-rtdb.firebaseio.com"
        self.user_phone = "8015339335"
        self.is_monitoring = False
        
    def send_emergency_command(self, command, phone_number):
        """Send emergency command via Firebase (simulates SMS response)"""
        try:
            command_data = {
                'command': command,
                'phone': phone_number,
                'timestamp': int(time.time() * 1000),
                'status': 'pending',
                'source': 'sms_response'
            }
            
            response = requests.post(
                f"{self.firebase_url}/emergency_commands.json",
                json=command_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Emergency command '{command}' sent successfully")
                return True
            else:
                print(f"❌ Failed to send command: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return False
    
    def simulate_sms_response(self):
        """Simulate SMS response for demo purposes"""
        print("\n📱 SMS COMMAND SIMULATOR")
        print("=" * 30)
        print("Available commands:")
        print("1. SHUTDOWN - Emergency shutdown laptop")
        print("2. LOCK - Lock laptop screen")
        print("3. STATUS - Get laptop status")
        print("4. ALERT - Send test alert")
        
        while True:
            command = input("\nEnter command (or 'exit' to quit): ").strip().upper()
            
            if command == 'EXIT':
                break
            elif command in ['SHUTDOWN', 'LOCK', 'STATUS', 'ALERT']:
                if self.send_emergency_command(command, self.user_phone):
                    print(f"📤 Command '{command}' sent to laptop")
                    if command == 'SHUTDOWN':
                        print("⚠️ Laptop will shutdown in 10 seconds!")
                else:
                    print("❌ Failed to send command")
            else:
                print("❌ Invalid command")

def main():
    """Main entry point for SMS command handler"""
    handler = SMSCommandHandler()
    
    print("🚀 SMS Command Handler")
    print("📱 This simulates sending SMS commands to your laptop")
    print(f"📞 Configured for phone: {handler.user_phone}")
    
    handler.simulate_sms_response()

if __name__ == "__main__":
    main()
