"""
Basic Security System - No external dependencies
Features:
- Keystroke pattern authentication
- Failed attempt monitoring
- Local alerts and logging
- Emergency shutdown simulation
"""

import time
import json
import os
import threading
import subprocess
from datetime import datetime
from collections import defaultdict
import pickle

class BasicSecuritySystem:
    def __init__(self):
        self.user_phone = "8015339335"  # Your emergency contact
        
        # Keystroke timing data
        self.keystroke_patterns = {}
        self.failed_attempts = 0
        self.max_attempts = 3
        self.is_authenticated = False
        
        # Create logs directory
        os.makedirs('security_logs', exist_ok=True)
        
        # Load existing patterns if available
        self.load_keystroke_patterns()
        
        print("🔒 Basic Security System Initialized")
        print(f"📞 Emergency contact: {self.user_phone}")
        print("🎯 Ready for keystroke authentication")
        print("📁 Logs will be saved in: security_logs/")
    
    def load_keystroke_patterns(self):
        """Load saved keystroke patterns"""
        try:
            if os.path.exists('keystroke_patterns.json'):
                with open('keystroke_patterns.json', 'r') as f:
                    self.keystroke_patterns = json.load(f)
                print("✅ Keystroke patterns loaded")
            else:
                print("📋 No existing patterns found - training mode required")
        except Exception as e:
            print(f"❌ Error loading patterns: {e}")
    
    def save_keystroke_patterns(self):
        """Save keystroke patterns"""
        try:
            with open('keystroke_patterns.json', 'w') as f:
                json.dump(self.keystroke_patterns, f, indent=2)
            print("✅ Keystroke patterns saved")
        except Exception as e:
            print(f"❌ Error saving patterns: {e}")
    
    def log_security_event(self, event_type, message, severity="info"):
        """Log security events to file"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'event_type': event_type,
                'message': message,
                'severity': severity,
                'failed_attempts': self.failed_attempts
            }
            
            log_filename = f"security_logs/security_log_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Load existing logs
            logs = []
            if os.path.exists(log_filename):
                with open(log_filename, 'r') as f:
                    logs = json.load(f)
            
            # Add new log entry
            logs.append(log_entry)
            
            # Save logs
            with open(log_filename, 'w') as f:
                json.dump(logs, f, indent=2)
            
            print(f"📝 Logged: {event_type} - {message}")
            
        except Exception as e:
            print(f"❌ Logging error: {e}")
    
    def capture_keystroke_timing(self, text):
        """Capture keystroke timing patterns"""
        print(f"🎯 Type the phrase: '{text}'")
        print("Press Enter when done...")
        
        start_time = time.time()
        typed_text = input(">>> ")
        end_time = time.time()
        
        # Calculate typing metrics
        total_time = end_time - start_time
        chars_per_second = len(typed_text) / total_time if total_time > 0 else 0
        words_per_minute = (len(typed_text.split()) / total_time) * 60 if total_time > 0 else 0
        
        # Simple timing pattern
        timing_pattern = {
            'total_time': total_time,
            'chars_per_second': chars_per_second,
            'words_per_minute': words_per_minute,
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
                print(f"   ⏱️  Time: {pattern['total_time']:.2f}s")
                print(f"   ⚡ Speed: {pattern['chars_per_second']:.1f} chars/sec")
                print(f"   📝 WPM: {pattern['words_per_minute']:.1f}")
            else:
                print("❌ Text mismatch, please try again")
                attempt -= 1  # Don't count this attempt
        
        # Calculate average patterns
        if all_patterns:
            avg_total_time = sum(p['total_time'] for p in all_patterns) / len(all_patterns)
            avg_chars_per_second = sum(p['chars_per_second'] for p in all_patterns) / len(all_patterns)
            avg_wpm = sum(p['words_per_minute'] for p in all_patterns) / len(all_patterns)
            avg_rhythm = sum(p['typing_rhythm'] for p in all_patterns) / len(all_patterns)
            
            self.keystroke_patterns[username] = {
                'phrase': training_phrase,
                'avg_total_time': avg_total_time,
                'avg_chars_per_second': avg_chars_per_second,
                'avg_words_per_minute': avg_wpm,
                'avg_rhythm': avg_rhythm,
                'tolerance': 0.4,  # 40% tolerance
                'trained_at': datetime.now().isoformat()
            }
            
            self.save_keystroke_patterns()
            self.log_security_event("training_completed", f"Keystroke patterns trained for user: {username}")
            
            print(f"🎉 Training completed for {username}")
            print(f"📊 Average typing speed: {avg_chars_per_second:.1f} chars/sec ({avg_wpm:.1f} WPM)")
            return True
        
        return False
    
    def authenticate_keystroke(self, username, test_phrase=None):
        """Authenticate user based on keystroke pattern"""
        if username not in self.keystroke_patterns:
            print(f"❌ No patterns found for user: {username}")
            self.log_security_event("auth_failed", f"No patterns found for user: {username}", "warning")
            return False
        
        pattern = self.keystroke_patterns[username]
        phrase = test_phrase or pattern['phrase']
        
        print(f"🔐 Authentication required for: {username}")
        test_pattern, typed_text = self.capture_keystroke_timing(phrase)
        
        # Check if text matches
        if typed_text.lower().strip() != phrase.lower().strip():
            print("❌ Text mismatch")
            self.log_security_event("auth_failed", f"Text mismatch for user: {username}", "warning")
            return False
        
        # Check timing patterns
        time_diff = abs(test_pattern['total_time'] - pattern['avg_total_time'])
        speed_diff = abs(test_pattern['chars_per_second'] - pattern['avg_chars_per_second'])
        wpm_diff = abs(test_pattern['words_per_minute'] - pattern['avg_words_per_minute'])
        rhythm_diff = abs(test_pattern['typing_rhythm'] - pattern['avg_rhythm'])
        
        # Calculate similarity scores (lower is better)
        time_similarity = time_diff / pattern['avg_total_time'] if pattern['avg_total_time'] > 0 else 1
        speed_similarity = speed_diff / pattern['avg_chars_per_second'] if pattern['avg_chars_per_second'] > 0 else 1
        wpm_similarity = wpm_diff / pattern['avg_words_per_minute'] if pattern['avg_words_per_minute'] > 0 else 1
        rhythm_similarity = rhythm_diff / pattern['avg_rhythm'] if pattern['avg_rhythm'] > 0 else 1
        
        overall_similarity = (time_similarity + speed_similarity + wpm_similarity + rhythm_similarity) / 4
        
        print(f"📊 Authentication Analysis:")
        print(f"   ⏱️  Time difference: {time_diff:.2f}s")
        print(f"   ⚡ Speed difference: {speed_diff:.1f} chars/sec")
        print(f"   📝 WPM difference: {wpm_diff:.1f}")
        print(f"   🎯 Overall similarity: {overall_similarity:.3f} (tolerance: {pattern['tolerance']})")
        
        if overall_similarity <= pattern['tolerance']:
            print("✅ Authentication successful!")
            self.log_security_event("auth_success", f"User {username} authenticated successfully")
            return True
        else:
            print("❌ Authentication failed - keystroke pattern doesn't match")
            self.log_security_event("auth_failed", f"Keystroke pattern mismatch for user: {username}", "warning")
            return False
    
    def send_alert(self, alert_type, message):
        """Send alert (local simulation)"""
        print("\n" + "="*60)
        print("🚨 SECURITY ALERT")
        print("="*60)
        print(f"📱 Alert Type: {alert_type}")
        print(f"📞 Emergency Contact: {self.user_phone}")
        print(f"💬 Message: {message}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Log the alert
        self.log_security_event("alert_sent", f"{alert_type}: {message}", "critical")
        
        # Simulate SMS
        print(f"📱 SMS to {self.user_phone}:")
        print(f"🚨 {message}")
        print("💡 In a real system, this would:")
        print("   • Send actual SMS via Twilio")
        print("   • Make emergency phone call")
        print("   • Send Firebase notification to mobile app")
        print("   • Allow 'SHUTDOWN' reply for emergency shutdown")
        
        return True
    
    def simulate_emergency_shutdown(self):
        """Simulate emergency shutdown"""
        print("\n🚨 EMERGENCY SHUTDOWN SIMULATION")
        print("⚠️  In a real system, this would:")
        print("   • Execute: shutdown /s /f /t 0")
        print("   • Force immediate system shutdown")
        print("   • Close all applications")
        
        choice = input("\n❓ Simulate shutdown countdown? (y/n): ").lower().strip()
        
        if choice == 'y':
            print("\n🚨 EMERGENCY SHUTDOWN INITIATED!")
            print("⏰ Shutdown countdown...")
            
            for i in range(10, 0, -1):
                print(f"🔴 Shutdown in {i} seconds...")
                time.sleep(1)
            
            print("💻 SYSTEM SHUTDOWN (simulated)")
            self.log_security_event("emergency_shutdown", "Emergency shutdown executed", "critical")
        else:
            print("✅ Shutdown cancelled")
    
    def handle_failed_authentication(self):
        """Handle failed authentication attempts"""
        self.failed_attempts += 1
        print(f"❌ Authentication failed! Attempts: {self.failed_attempts}/{self.max_attempts}")
        
        if self.failed_attempts >= self.max_attempts:
            print("🚨 SECURITY BREACH DETECTED!")
            
            # Send alerts
            alert_message = f"SECURITY BREACH: {self.failed_attempts} failed login attempts detected on your laptop at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.send_alert("SECURITY_BREACH", alert_message)
            
            # Log the breach
            self.log_security_event("security_breach", f"{self.failed_attempts} failed authentication attempts", "critical")
            
            # Offer emergency shutdown
            print("\n🔧 EMERGENCY RESPONSE OPTIONS:")
            print("1. Simulate emergency shutdown")
            print("2. Lock system (simulation)")
            print("3. Continue monitoring")
            
            choice = input("Select response (1-3): ").strip()
            
            if choice == '1':
                self.simulate_emergency_shutdown()
            elif choice == '2':
                print("🔒 System locked (simulated)")
                self.log_security_event("system_locked", "System locked due to security breach", "high")
            else:
                print("👁️ Continuing security monitoring...")
            
            return True
        
        return False
    
    def show_security_logs(self):
        """Show recent security logs"""
        try:
            log_filename = f"security_logs/security_log_{datetime.now().strftime('%Y%m%d')}.json"
            
            if os.path.exists(log_filename):
                with open(log_filename, 'r') as f:
                    logs = json.load(f)
                
                print(f"\n📋 Security Logs for {datetime.now().strftime('%Y-%m-%d')}")
                print("="*60)
                
                for log in logs[-10:]:  # Show last 10 entries
                    timestamp = log['timestamp'][:19]  # Remove microseconds
                    event_type = log['event_type']
                    message = log['message']
                    severity = log['severity']
                    
                    severity_icon = {
                        'info': '📝',
                        'warning': '⚠️',
                        'high': '🔴',
                        'critical': '🚨'
                    }.get(severity, '📝')
                    
                    print(f"{severity_icon} {timestamp} | {event_type} | {message}")
                
                print("="*60)
            else:
                print("📭 No security logs found for today")
                
        except Exception as e:
            print(f"❌ Error reading logs: {e}")
    
    def run_security_system(self):
        """Main security system loop"""
        print("🚀 Starting Basic Security System")
        print("=" * 50)
        
        while True:
            print("\n🔒 SECURITY SYSTEM MENU")
            print("1. Train new user keystroke pattern")
            print("2. Authenticate existing user")
            print("3. Test security alerts")
            print("4. View security logs")
            print("5. Reset failed attempts")
            print("6. Show user patterns")
            print("7. Exit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
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
                        self.log_security_event("access_granted", f"User {username} granted access")
                    else:
                        if self.handle_failed_authentication():
                            print("🚨 Security protocols activated!")
                else:
                    print("❌ User not found!")
                    self.handle_failed_authentication()
            
            elif choice == '3':
                print("🧪 Testing security alerts...")
                self.send_alert("TEST_ALERT", "This is a test security alert from the Basic Security System")
                print("✅ Test alert sent!")
            
            elif choice == '4':
                self.show_security_logs()
            
            elif choice == '5':
                self.failed_attempts = 0
                print("🔄 Failed attempts reset to 0")
                self.log_security_event("attempts_reset", "Failed attempts counter reset")
            
            elif choice == '6':
                if self.keystroke_patterns:
                    print("\n👥 Trained Users:")
                    for username, pattern in self.keystroke_patterns.items():
                        print(f"   🔐 {username}")
                        print(f"      📝 Phrase: '{pattern['phrase']}'")
                        print(f"      ⚡ Speed: {pattern['avg_chars_per_second']:.1f} chars/sec")
                        print(f"      📊 WPM: {pattern['avg_words_per_minute']:.1f}")
                        print(f"      📅 Trained: {pattern.get('trained_at', 'Unknown')[:10]}")
                else:
                    print("📭 No users trained yet")
            
            elif choice == '7':
                print("👋 Shutting down security system...")
                self.log_security_event("system_shutdown", "Security system shut down by user")
                break
            
            else:
                print("❌ Invalid choice!")

def main():
    """Main entry point"""
    try:
        print("🔒 BASIC SECURITY SYSTEM")
        print("=" * 50)
        print("📋 Features:")
        print("   • Keystroke biometric authentication")
        print("   • Failed attempt monitoring")
        print("   • Security event logging")
        print("   • Emergency alert simulation")
        print("   • Local data storage")
        print("=" * 50)
        
        security_system = BasicSecuritySystem()
        security_system.run_security_system()
        
    except KeyboardInterrupt:
        print("\n🛑 Security system stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    main()
