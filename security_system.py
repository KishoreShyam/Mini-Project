import time
import threading
import json
import os
from datetime import datetime
from keystroke_collector import KeystrokeCollector
from typing_model import TypingPatternModel
from notification_system import NotificationSystem
from instant_mobile_alerts import InstantMobileAlerts
from emergency_call_system import EmergencyCallSystem
import cv2
import pygame
import requests

class SecuritySystem:
    def __init__(self):
        self.keystroke_collector = KeystrokeCollector()
        self.typing_model = TypingPatternModel()
        self.notification_system = NotificationSystem()
        self.instant_alerts = InstantMobileAlerts()
        self.emergency_calls = EmergencyCallSystem()
        self.failed_attempts = 0
        self.max_attempts = 3
        self.is_locked = True
        self.camera = None
        self.alarm_active = False
        self.user_phone = None  # Will be set from config
        self.config_file = "security_config.json"
        self.load_config()
        
        # Initialize pygame for alarm sounds
        pygame.mixer.init()
        
    def load_config(self):
        """Load security system configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.user_phone = config.get('user_phone', None)
                    self.max_attempts = config.get('max_attempts', 3)
                    print("Configuration loaded successfully!")
            except Exception as e:
                print(f"Error loading config: {e}")
                self.create_default_config()
        else:
            self.create_default_config()
            
    def create_default_config(self):
        """Create default configuration file"""
        config = {
            'user_phone': None,
            'max_attempts': 3,
            'notification_service': 'email',  # or 'sms'
            'email_settings': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'email': '',
                'password': ''
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"Default configuration created at {self.config_file}")
        print("Please update the configuration with your contact details!")
        
    def setup_user_profile(self):
        """Setup user profile and train the model"""
        print("Setting up user profile...")
        print("You need to provide typing samples to train the security system.")
        
        num_sessions = int(input("How many training sessions? (recommended: 5-10): ") or "5")
        
        for i in range(num_sessions):
            print(f"\nTraining session {i+1}/{num_sessions}")
            print("Please type the following text naturally:")
            print("The quick brown fox jumps over the lazy dog. Security systems protect our digital lives.")
            
            input("Press Enter when ready to start typing...")
            
            if not self.keystroke_collector.collect_training_session(30):
                print("Failed to collect training data!")
                return False
                
        # Train the model
        print("\nTraining the authentication model...")
        if self.typing_model.train_model():
            self.typing_model.save_model()
            print("User profile setup completed successfully!")
            return True
        else:
            print("Failed to train the model!")
            return False
            
    def authenticate_user(self, timeout=30):
        """Authenticate user based on typing pattern"""
        print("Please type to authenticate (you have 30 seconds):")
        print("Type: 'I am the authorized user of this system'")
        
        # Collect keystroke data
        self.keystroke_collector.start_collection(duration=timeout)
        time.sleep(timeout + 1)
        
        # Get typing features
        features = self.keystroke_collector.get_typing_features()
        
        if features is None:
            print("No typing data collected!")
            return False
            
        # Authenticate using the model
        is_authentic, confidence = self.typing_model.authenticate(features)
        
        print(f"Authentication confidence: {confidence:.2%}")
        
        if is_authentic and confidence > 0.7:  # 70% confidence threshold
            print("✅ Authentication successful!")
            self.failed_attempts = 0
            self.is_locked = False
            return True
        else:
            print("❌ Authentication failed!")
            self.failed_attempts += 1
            return False
            
    def capture_intruder_photo(self):
        """Capture photo of potential intruder with enhanced detection"""
        try:
            print("\n📸 INTRUDER DETECTION ACTIVATED!")
            print("🚨 CAPTURING INTRUDER PHOTO...")
            
            # Initialize camera
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                print("❌ Error: Could not access camera!")
                print("🔧 Trying alternative camera indices...")
                
                # Try different camera indices
                for i in range(1, 4):
                    self.camera = cv2.VideoCapture(i)
                    if self.camera.isOpened():
                        print(f"✅ Camera found at index {i}")
                        break
                else:
                    print("❌ No camera available!")
                    return None
            
            # Set camera properties for better quality
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print("📷 Camera initialized - warming up...")
            
            # Warm up camera and take multiple shots
            best_frame = None
            for i in range(10):
                ret, frame = self.camera.read()
                if ret:
                    best_frame = frame
                time.sleep(0.1)  # Small delay for camera stabilization
                
            if best_frame is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"intruder_{timestamp}.jpg"
                
                # Add timestamp and warning text to image
                height, width = best_frame.shape[:2]
                
                # Add red warning overlay
                overlay = best_frame.copy()
                cv2.rectangle(overlay, (0, 0), (width, 80), (0, 0, 255), -1)
                cv2.addWeighted(overlay, 0.7, best_frame, 0.3, 0, best_frame)
                
                # Add warning text
                warning_text = "SECURITY BREACH DETECTED!"
                time_text = f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                cv2.putText(best_frame, warning_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(best_frame, time_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Save the enhanced image
                cv2.imwrite(filename, best_frame)
                
                print(f"✅ INTRUDER PHOTO CAPTURED: {filename}")
                print(f"📊 Image size: {width}x{height}")
                print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                self.camera.release()
                return filename
            else:
                print("❌ Failed to capture photo!")
                self.camera.release()
                return None
                
        except Exception as e:
            print(f"❌ Error capturing photo: {e}")
            if self.camera:
                self.camera.release()
            return None
            
    def activate_alarm(self, duration=15):
        """Activate enhanced PC alarm system"""
        try:
            self.alarm_active = True
            print("\n" + "="*60)
            print("🚨 SECURITY ALARM SYSTEM ACTIVATED! 🚨")
            print("="*60)
            print(f"⏰ Alarm Duration: {duration} seconds")
            print(f"🔊 Volume: MAXIMUM")
            print("="*60)
            
            # Create multiple alarm sounds for variety
            sample_rate = 22050
            
            # High-pitched urgent beep
            def create_urgent_beep():
                duration_ms = 300
                frequency = 1000
                frames = int(duration_ms * sample_rate / 1000)
                arr = []
                for i in range(frames):
                    wave = 4096 * (i % (sample_rate // frequency) < (sample_rate // frequency) // 2) - 2048
                    arr.append([wave, wave])
                import numpy as np
                return pygame.sndarray.make_sound(np.array(arr, dtype=np.int16))
            
            # Lower warning tone
            def create_warning_tone():
                duration_ms = 400
                frequency = 600
                frames = int(duration_ms * sample_rate / 1000)
                arr = []
                for i in range(frames):
                    wave = 3000 * (i % (sample_rate // frequency) < (sample_rate // frequency) // 2) - 1500
                    arr.append([wave, wave])
                import numpy as np
                return pygame.sndarray.make_sound(np.array(arr, dtype=np.int16))
            
            # Siren-like sound
            def create_siren():
                duration_ms = 600
                arr = []
                frames = int(duration_ms * sample_rate / 1000)
                for i in range(frames):
                    # Frequency sweep from 400 to 1200 Hz
                    freq = 400 + (800 * i / frames)
                    wave = 3500 * (i % int(sample_rate / freq) < int(sample_rate / freq) // 2) - 1750
                    arr.append([wave, wave])
                import numpy as np
                return pygame.sndarray.make_sound(np.array(arr, dtype=np.int16))
            
            # Create all alarm sounds
            urgent_beep = create_urgent_beep()
            warning_tone = create_warning_tone()
            siren = create_siren()
            
            # Play alarm sequence for specified duration
            start_time = time.time()
            pattern_cycle = 0
            
            while time.time() - start_time < duration and self.alarm_active:
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                
                print(f"\r🚨 ALARM ACTIVE - {remaining}s remaining 🚨", end="", flush=True)
                
                # Alternate between different alarm sounds
                if pattern_cycle % 3 == 0:
                    urgent_beep.play()
                    time.sleep(0.3)
                    urgent_beep.play()
                    time.sleep(0.3)
                elif pattern_cycle % 3 == 1:
                    warning_tone.play()
                    time.sleep(0.4)
                else:
                    siren.play()
                    time.sleep(0.6)
                
                pattern_cycle += 1
                
            print(f"\n🔇 Alarm stopped after {duration} seconds")
                
        except Exception as e:
            print(f"❌ Error activating pygame alarm: {e}")
            print("🔄 Switching to fallback alarm system...")
            
            # Enhanced fallback alarm system
            try:
                import winsound
                # Windows system beep
                start_time = time.time()
                while time.time() - start_time < duration and self.alarm_active:
                    elapsed = int(time.time() - start_time)
                    remaining = duration - elapsed
                    print(f"\r🚨 SYSTEM ALARM ACTIVE - {remaining}s remaining 🚨", end="", flush=True)
                    
                    # High frequency beep
                    winsound.Beep(1000, 300)
                    time.sleep(0.1)
                    winsound.Beep(800, 200)
                    time.sleep(0.2)
                    
                print(f"\n🔇 System alarm stopped")
                    
            except ImportError:
                # Final fallback - console alarm
                print("🔄 Using console alarm system...")
                for i in range(duration * 2):
                    if not self.alarm_active:
                        break
                    remaining = duration - (i // 2)
                    print(f"\r🚨 SECURITY BREACH! UNAUTHORIZED ACCESS! - {remaining}s 🚨", end="", flush=True)
                    time.sleep(0.5)
                print("\n🔇 Console alarm stopped")
                
    def send_alert_notification(self, photo_path=None):
        """Send instant mobile alert notification to user"""
        try:
            message = f"Unauthorized access attempt detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            if photo_path:
                message += f"\nIntruder photo captured: {photo_path}"
                
            # PRIORITY 1: Make EMERGENCY PHONE CALL (most effective!)
            call_sent = self.emergency_calls.send_emergency_alert(message, photo_path)
            
            # PRIORITY 2: Send INSTANT mobile alerts (immediate notification)
            instant_sent = self.instant_alerts.send_instant_alerts(message, photo_path)
            
            # PRIORITY 3: Send traditional email/SMS as backup
            email_sent = self.notification_system.send_alert(message, photo_path)
            
            # Display status
            if call_sent or instant_sent or email_sent:
                print("\n" + "="*60)
                print("🚨 EMERGENCY ALERTS SENT! 🚨")
                print("="*60)
                print(message)
                if call_sent:
                    print("📞 EMERGENCY CALL: SUCCESS")
                if instant_sent:
                    print("✅ INSTANT notifications: SUCCESS")
                if email_sent:
                    print("✅ Email notifications: SUCCESS")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("⚠️ ALL NOTIFICATIONS FAILED!")
                print("="*60)
                print(message)
                print("❌ Please configure emergency alerts immediately!")
                print("Run: python emergency_call_system.py")
                print("="*60)
            
            # Save alert log
            alert_log = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'photo_path': photo_path,
                'failed_attempts': self.failed_attempts,
                'emergency_call_sent': call_sent,
                'instant_alerts_sent': instant_sent,
                'email_notification_sent': email_sent,
                'total_success': call_sent or instant_sent or email_sent
            }
            
            # Append to alerts log file
            alerts_file = "security_alerts.json"
            alerts = []
            
            if os.path.exists(alerts_file):
                try:
                    with open(alerts_file, 'r') as f:
                        alerts = json.load(f)
                except:
                    alerts = []
                    
            alerts.append(alert_log)
            
            with open(alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
                
            return call_sent or instant_sent or email_sent
            
        except Exception as e:
            print(f"Error sending notifications: {e}")
            return False
            
    def handle_security_breach(self):
        """Handle security breach after 3+ failed attempts"""
        print(f"\n" + "="*70)
        print("🚨 CRITICAL SECURITY BREACH DETECTED! 🚨")
        print("="*70)
        print(f"❌ Failed Attempts: {self.failed_attempts}/{self.max_attempts}")
        print(f"🚫 UNAUTHORIZED ACCESS ATTEMPT!")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # STEP 1: Immediately capture intruder photo
        print("\n🔍 STEP 1: CAPTURING INTRUDER EVIDENCE")
        photo_path = self.capture_intruder_photo()
        
        if photo_path:
            print(f"✅ Intruder photo saved: {photo_path}")
        else:
            print("❌ Failed to capture intruder photo")
        
        # STEP 2: Activate PC alarm system
        print("\n🚨 STEP 2: ACTIVATING PC ALARM SYSTEM")
        print("🔊 Starting 15-second alarm sequence...")
        alarm_thread = threading.Thread(target=self.activate_alarm, args=(15,))
        alarm_thread.daemon = True
        alarm_thread.start()
        
        # STEP 3: Send emergency alerts with photo to mobile
        print("\n📱 STEP 3: SENDING EMERGENCY ALERTS TO MOBILE")
        print(f"📞 Calling +918015339335...")
        print(f"📧 Sending photo to mobile...")
        
        # Enhanced message with more details
        breach_message = f"""CRITICAL SECURITY BREACH!

Unauthorized person detected trying to access your computer!

Details:
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Failed Attempts: {self.failed_attempts}
- Location: Your PC/Laptop
- Action: Intruder photo captured
- Status: System locked for 5 minutes

IMMEDIATE ACTION REQUIRED!
Check your computer now!"""
        
        alert_sent = self.send_alert_notification(photo_path)
        
        if alert_sent:
            print("✅ Emergency alerts sent successfully!")
        else:
            print("❌ Failed to send some alerts - check configuration")
        
        # STEP 4: System lockdown
        print("\n🔒 STEP 4: INITIATING SECURITY LOCKDOWN")
        print("🚫 System will be locked for 5 minutes")
        print("⏳ Lockdown timer started...")
        
        # Show countdown
        lockdown_duration = 300  # 5 minutes
        for remaining in range(lockdown_duration, 0, -30):
            minutes = remaining // 60
            seconds = remaining % 60
            print(f"\r🔒 LOCKDOWN: {minutes:02d}:{seconds:02d} remaining", end="", flush=True)
            time.sleep(30)
        
        print(f"\n✅ Lockdown period completed")
        print("🔓 System ready for authentication again")
        
        # Reset failed attempts after lockout
        self.failed_attempts = 0
        
        # Log the security breach
        self.log_security_breach(photo_path, breach_message)
        
    def log_security_breach(self, photo_path, message):
        """Log detailed security breach information"""
        breach_log = {
            'timestamp': datetime.now().isoformat(),
            'failed_attempts': self.failed_attempts,
            'max_attempts': self.max_attempts,
            'photo_path': photo_path,
            'message': message,
            'system_info': {
                'os': os.name,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'breach_type': 'typing_pattern_mismatch'
            }
        }
        
        # Save to breach log file
        breach_file = "security_breaches.json"
        breaches = []
        
        if os.path.exists(breach_file):
            try:
                with open(breach_file, 'r') as f:
                    breaches = json.load(f)
            except:
                breaches = []
                
        breaches.append(breach_log)
        
        with open(breach_file, 'w') as f:
            json.dump(breaches, f, indent=2)
            
        print(f"📝 Security breach logged to {breach_file}")
        
    def run_security_system(self):
        """Main security system loop"""
        print("🔒 Security System Started")
        print("=" * 30)
        
        # Load the trained model
        if not self.typing_model.load_model():
            print("No trained model found! Please set up user profile first.")
            return
            
        while True:
            if self.is_locked:
                print(f"\n🔒 System is LOCKED")
                print(f"Failed attempts: {self.failed_attempts}/{self.max_attempts}")
                
                if self.failed_attempts >= self.max_attempts:
                    self.handle_security_breach()
                    continue
                    
                # Attempt authentication
                if self.authenticate_user():
                    print("🔓 System UNLOCKED! Welcome back!")
                    
                    # Simulate system usage
                    print("System is now accessible. Press Enter to lock again...")
                    input()
                    self.is_locked = True
                    print("System locked.")
                    
            time.sleep(1)
            
    def stop_alarm(self):
        """Stop the alarm"""
        self.alarm_active = False
        print("Alarm stopped.")

def main():
    security = SecuritySystem()
    
    print("Keystroke-Based Security System")
    print("=" * 35)
    
    while True:
        print("\n1. Setup user profile (train model)")
        print("2. Run security system")
        print("3. Test authentication")
        print("4. View security alerts")
        print("5. Configure settings")
        print("6. 📱 Setup INSTANT Mobile Alerts")
        print("7. 📞 Setup EMERGENCY Phone Calls")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            security.setup_user_profile()
            
        elif choice == '2':
            try:
                security.run_security_system()
            except KeyboardInterrupt:
                print("\nSecurity system stopped.")
                security.stop_alarm()
                
        elif choice == '3':
            if not security.typing_model.load_model():
                print("Please setup user profile first!")
                continue
                
            result = security.authenticate_user()
            print(f"Test result: {'PASSED' if result else 'FAILED'}")
            
        elif choice == '4':
            alerts_file = "security_alerts.json"
            if os.path.exists(alerts_file):
                try:
                    with open(alerts_file, 'r') as f:
                        alerts = json.load(f)
                    
                    if alerts:
                        print(f"\nFound {len(alerts)} security alerts:")
                        for i, alert in enumerate(alerts[-5:], 1):  # Show last 5 alerts
                            print(f"\n{i}. {alert['timestamp']}")
                            print(f"   {alert['message']}")
                            if alert.get('photo_path'):
                                print(f"   Photo: {alert['photo_path']}")
                    else:
                        print("No security alerts found.")
                        
                except Exception as e:
                    print(f"Error reading alerts: {e}")
            else:
                print("No security alerts file found.")
                
        elif choice == '5':
            print("Configuration settings:")
            print(f"Current max attempts: {security.max_attempts}")
            
            new_attempts = input(f"Enter new max attempts ({security.max_attempts}): ").strip()
            if new_attempts.isdigit():
                security.max_attempts = int(new_attempts)
                
            phone = input("Enter phone number for alerts (optional): ").strip()
            if phone:
                security.user_phone = phone
                
            # Save updated config
            config = {
                'user_phone': security.user_phone,
                'max_attempts': security.max_attempts,
                'notification_service': 'email'
            }
            
            with open(security.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            print("Configuration updated!")
            
        elif choice == '6':
            print("\n🚨 INSTANT MOBILE ALERT SETUP 🚨")
            print("=" * 40)
            print("Setting up instant notifications for immediate security alerts...")
            
            # Quick setup for ntfy (no signup required)
            security.instant_alerts.setup_ntfy_quick()
            
            print("\nFor additional alert methods:")
            print("Run: python instant_mobile_alerts.py")
            
        elif choice == '7':
            print("\n📞 EMERGENCY PHONE CALL SETUP 📞")
            print("=" * 45)
            print(f"Your mobile number: +918015339335")
            print("Setting up emergency voice calls for security breaches...")
            
            # Setup emergency calls
            from emergency_call_system import main as emergency_main
            emergency_main()
            
        elif choice == '8':
            break
            
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
