"""
Simplified Security System - Works with existing packages
Features:
- Keystroke pattern authentication
- Failed attempt monitoring
- Firebase alerts
- Emergency shutdown via Firebase
"""

import time
import json
import os
import threading
import requests
import subprocess
from datetime import datetime
from collections import defaultdict
import pickle
import sys

class SimpleSecuritySystem:
    def __init__(self):
        self.user_phone = "8015339335"  # Your emergency contact
        self.firebase_url = "https://security-control-demo-default-rtdb.firebaseio.com"
        
        # Keystroke timing data
        self.keystroke_patterns = {}
        self.failed_attempts = 0
        self.max_attempts = 3
        self.is_authenticated = False
        
        # Load existing patterns if available
        self.load_keystroke_patterns()
        
        print("🔒 Simple Security System Initialized")
        print(f"📞 Emergency contact: {self.user_phone}")
        print("🎯 Ready for keystroke authentication")
    
    def load_keystroke_patterns(self):
        """Load saved keystroke patterns"""
        try:
            if os.path.exists('keystroke_patterns.pkl'):
                with open('keystroke_patterns.pkl', 'rb') as f:
                    self.keystroke_patterns = pickle.load(f)
                print("✅ Keystroke patterns loaded")
            else:
                print("📋 No existing patterns found - training mode required")
        except Exception as e:
            print(f"❌ Error loading patterns: {e}")
    
    def save_keystroke_patterns(self):
        """Save keystroke patterns"""
        try:
            with open('keystroke_patterns.pkl', 'wb') as f:
                pickle.dump(self.keystroke_patterns, f)
            print("✅ Keystroke patterns saved")
        except Exception as e:
            print(f"❌ Error saving patterns: {e}")
    
    def capture_keystroke_timing(self, text):
        """Capture keystroke timing patterns (simplified)"""
        print(f"🎯 Type the phrase: '{text}'")
        print("Press Enter when done...")
        
        start_time = time.time()
        typed_text = input(">>> ")
        end_time = time.time()
        
        # Calculate typing speed and pattern
        total_time = end_time - start_time
        chars_per_second = len(typed_text) / total_time if total_time > 0 else 0
        
        # Simple timing pattern based on typing speed
        timing_pattern = {
            'total_time': total_time,
            'chars_per_second': chars_per_second,
            'text_length': len(typed_text),
            'typing_rhythm': total_time / len(typed_text) if len(typed_text) > 0 else 0
        }
        
        return timing_pattern, typed_text
    
    def train_keystroke_patterns(self, username, training_phrase="security system access"):
        """Train keystroke patterns for a user"""
        print(f"🎓 Training keystroke patterns for user: {username}")
        print("You'll need to type the same phrase 3 times for accuracy")
        
        all_patterns = []
        
        for attempt in range(3):
            print(f"\n📝 Training attempt {attempt + 1}/3")
            pattern, typed_text = self.capture_keystroke_timing(training_phrase)
            
            if typed_text.lower().strip() == training_phrase.lower().strip():
                all_patterns.append(pattern)
                print("✅ Pattern recorded successfully")
            else:
                print("❌ Text mismatch, please try again")
                attempt -= 1  # Don't count this attempt
        
        # Calculate average patterns
        if all_patterns:
            avg_total_time = sum(p['total_time'] for p in all_patterns) / len(all_patterns)
            avg_chars_per_second = sum(p['chars_per_second'] for p in all_patterns) / len(all_patterns)
            avg_rhythm = sum(p['typing_rhythm'] for p in all_patterns) / len(all_patterns)
            
            self.keystroke_patterns[username] = {
                'phrase': training_phrase,
                'avg_total_time': avg_total_time,
                'avg_chars_per_second': avg_chars_per_second,
                'avg_rhythm': avg_rhythm,
                'tolerance': 0.3  # 30% tolerance
            }
            
            self.save_keystroke_patterns()
            print(f"🎉 Training completed for {username}")
            return True
        
        return False
    
    def authenticate_keystroke(self, username, test_phrase=None):
        """Authenticate user based on keystroke pattern"""
        if username not in self.keystroke_patterns:
            print(f"❌ No patterns found for user: {username}")
            return False
        
        pattern = self.keystroke_patterns[username]
        phrase = test_phrase or pattern['phrase']
        
        print(f"🔐 Authentication required for: {username}")
        test_pattern, typed_text = self.capture_keystroke_timing(phrase)
        
        # Check if text matches
        if typed_text.lower().strip() != phrase.lower().strip():
            print("❌ Text mismatch")
            return False
        
        # Check timing patterns
        time_diff = abs(test_pattern['total_time'] - pattern['avg_total_time'])
        speed_diff = abs(test_pattern['chars_per_second'] - pattern['avg_chars_per_second'])
        rhythm_diff = abs(test_pattern['typing_rhythm'] - pattern['avg_rhythm'])
        
        # Calculate similarity (lower is better)
        time_similarity = time_diff / pattern['avg_total_time'] if pattern['avg_total_time'] > 0 else 1
        speed_similarity = speed_diff / pattern['avg_chars_per_second'] if pattern['avg_chars_per_second'] > 0 else 1
        rhythm_similarity = rhythm_diff / pattern['avg_rhythm'] if pattern['avg_rhythm'] > 0 else 1
        
        overall_similarity = (time_similarity + speed_similarity + rhythm_similarity) / 3
        
        print(f"📊 Similarity score: {overall_similarity:.3f} (tolerance: {pattern['tolerance']})")
        
        if overall_similarity <= pattern['tolerance']:
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed - keystroke pattern doesn't match")
            return False
    
    def send_firebase_alert(self, alert_type, message):
        """Send alert to Firebase for mobile app"""
        try:
            alert_data = {
                'type': alert_type,
                'message': message,
                'timestamp': int(time.time() * 1000),
                'phone': self.user_phone,
                'severity': 'critical',
                'location': 'Laptop Security System',
                'action_required': True,
                'failed_attempts': self.failed_attempts
            }
            
            # Send to Firebase
            response = requests.post(
                f"{self.firebase_url}/security_alerts.json",
                json=alert_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("🔥 Alert sent to Firebase successfully")
                return True
            else:
                print(f"❌ Firebase alert failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Firebase alert error: {e}")
        
        return False
    
    def send_sms_alert(self, message):
        """Send SMS alert (simulated)"""
        print(f"📱 SMS Alert to {self.user_phone}:")
        print(f"🚨 {message}")
        print("💡 Reply 'SHUTDOWN' to immediately shutdown the laptop")
        print("💡 Use the mobile app for emergency controls")
        return True
    
    def check_emergency_commands(self):
        """Check for emergency commands from Firebase"""
        try:
            response = requests.get(f"{self.firebase_url}/emergency_commands.json", timeout=5)
            
            if response.status_code == 200 and response.json():
                commands = response.json()
                
                for cmd_id, cmd_data in commands.items():
                    if isinstance(cmd_data, dict):
                        command = cmd_data.get('command', '')
                        phone = cmd_data.get('phone', '')
                        status = cmd_data.get('status', '')
                        timestamp = cmd_data.get('timestamp', 0)
                        
                        # Check if command is for this phone and is pending
                        if (phone == self.user_phone and 
                            status == 'pending' and 
                            command == 'SHUTDOWN'):
                            
                            # Check if command is recent (within 5 minutes)
                            current_time = int(time.time() * 1000)
                            if current_time - timestamp < 300000:  # 5 minutes
                                print("🚨 EMERGENCY SHUTDOWN COMMAND RECEIVED!")
                                self.emergency_shutdown()
                                return True
            
        except Exception as e:
            print(f"❌ Error checking commands: {e}")
        
        return False
    
    def emergency_shutdown(self):
        """Execute emergency shutdown"""
        print("🚨 EMERGENCY SHUTDOWN INITIATED!")
        print("⏰ Shutting down in 10 seconds...")
        
        # Send confirmation
        self.send_firebase_alert("shutdown_initiated", "Emergency shutdown command executed")
        
        # Countdown
        for i in range(10, 0, -1):
            print(f"🔴 Shutdown in {i} seconds...")
            time.sleep(1)
        
        # Execute shutdown
        try:
            subprocess.run(['shutdown', '/s', '/f', '/t', '0'], shell=True)
        except Exception as e:
            print(f"❌ Shutdown failed: {e}")
    
    def handle_failed_authentication(self):
        """Handle failed authentication attempts"""
        self.failed_attempts += 1
        print(f"❌ Authentication failed! Attempts: {self.failed_attempts}/{self.max_attempts}")
        
        if self.failed_attempts >= self.max_attempts:
            print("🚨 SECURITY BREACH DETECTED!")
            
            # Send alerts
            alert_message = f"SECURITY BREACH: {self.failed_attempts} failed login attempts detected on your laptop at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send Firebase alert
            self.send_firebase_alert("security_breach", alert_message)
            
            # Send SMS alert
            sms_message = f"🚨 SECURITY ALERT: Unauthorized access detected on your laptop. {self.failed_attempts} failed attempts. Reply 'SHUTDOWN' to secure system."
            self.send_sms_alert(sms_message)
            
            # Start monitoring for emergency commands
            self.start_emergency_monitoring()
            
            return True
        
        return False
    
    def start_emergency_monitoring(self):
        """Start monitoring for emergency commands"""
        def monitor_commands():
            print("📱 Monitoring for emergency commands for 60 seconds...")
            for _ in range(60):  # Monitor for 1 minute
                if self.check_emergency_commands():
                    break
                time.sleep(1)
            print("⏰ Emergency monitoring timeout")
        
        monitor_thread = threading.Thread(target=monitor_commands, daemon=True)
        monitor_thread.start()
    
    def run_security_system(self):
        """Main security system loop"""
        print("🚀 Starting Simple Security System")
        print("=" * 50)
        
        while True:
            print("\n🔒 SECURITY SYSTEM MENU")
            print("1. Train new user keystroke pattern")
            print("2. Authenticate existing user")
            print("3. Test emergency alerts")
            print("4. Check for emergency commands")
            print("5. Reset failed attempts")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                username = input("Enter username for training: ").strip()
                phrase = input("Enter training phrase (or press Enter for default): ").strip()
                if not phrase:
                    phrase = "security system access"
                
                if self.train_keystroke_patterns(username, phrase):
                    print("✅ Training completed successfully!")
                else:
                    print("❌ Training failed!")
            
            elif choice == '2':
                username = input("Enter username: ").strip()
                if username in self.keystroke_patterns:
                    if self.authenticate_keystroke(username):
                        self.is_authenticated = True
                        self.failed_attempts = 0
                        print("🎉 Access granted!")
                    else:
                        if self.handle_failed_authentication():
                            print("🚨 Security protocols activated!")
                else:
                    print("❌ User not found!")
                    self.handle_failed_authentication()
            
            elif choice == '3':
                print("🧪 Testing emergency alerts...")
                self.send_firebase_alert("test_alert", "This is a test security alert")
                self.send_sms_alert("🧪 Test alert: Security system is working properly")
                print("✅ Test alerts sent!")
            
            elif choice == '4':
                print("🔍 Checking for emergency commands...")
                if self.check_emergency_commands():
                    print("✅ Emergency command found and executed!")
                else:
                    print("📭 No emergency commands found")
            
            elif choice == '5':
                self.failed_attempts = 0
                print("🔄 Failed attempts reset to 0")
            
            elif choice == '6':
                print("👋 Shutting down security system...")
                break
            
            else:
                print("❌ Invalid choice!")

def main():
    """Main entry point"""
    try:
        security_system = SimpleSecuritySystem()
        security_system.run_security_system()
    except KeyboardInterrupt:
        print("\n🛑 Security system stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    main()
