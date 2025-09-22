"""
Advanced Security System with Keystroke Biometrics, Camera Capture, and Mobile Alerts
Features:
- Keystroke pattern authentication
- Camera capture on failed attempts
- Instant mobile alerts and phone calls
- Emergency shutdown via SMS
- Firebase integration for cross-network communication
"""

import cv2
import numpy as np
import time
import json
import os
import threading
import requests
import subprocess
from datetime import datetime
from collections import defaultdict
import pickle
import hashlib
import base64
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import keyboard
import sys

class AdvancedSecuritySystem:
    def __init__(self):
        self.user_phone = "8015339335"  # Your emergency contact
        self.firebase_url = "https://security-control-demo-default-rtdb.firebaseio.com"
        
        # Keystroke biometric data
        self.keystroke_patterns = {}
        self.current_typing = []
        self.failed_attempts = 0
        self.max_attempts = 3
        self.is_authenticated = False
        self.is_monitoring = False
        
        # Camera setup
        self.camera = None
        self.intruder_photos = []
        
        # Alert configuration
        self.twilio_sid = "YOUR_TWILIO_SID"  # Configure with your Twilio credentials
        self.twilio_token = "YOUR_TWILIO_TOKEN"
        self.twilio_phone = "YOUR_TWILIO_PHONE"
        
        # Load existing patterns if available
        self.load_keystroke_patterns()
        
        print("🔒 Advanced Security System Initialized")
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
        """Capture keystroke timing patterns"""
        timings = []
        start_time = time.time()
        
        print(f"🎯 Type the phrase: '{text}'")
        print("Press Enter when done...")
        
        typed_chars = []
        char_times = []
        
        def on_key_press(event):
            if event.event_type == keyboard.KEY_DOWN:
                current_time = time.time()
                if event.name == 'enter':
                    return False  # Stop recording
                elif len(event.name) == 1:  # Regular character
                    typed_chars.append(event.name)
                    char_times.append(current_time)
        
        keyboard.hook(on_key_press)
        keyboard.wait('enter')
        keyboard.unhook_all()
        
        # Calculate timing patterns
        if len(char_times) > 1:
            for i in range(1, len(char_times)):
                interval = char_times[i] - char_times[i-1]
                timings.append(interval)
        
        typed_text = ''.join(typed_chars)
        return timings, typed_text
    
    def train_keystroke_patterns(self, username, training_phrase="security system access"):
        """Train keystroke patterns for a user"""
        print(f"🎓 Training keystroke patterns for user: {username}")
        print("You'll need to type the same phrase 5 times for accuracy")
        
        all_timings = []
        
        for attempt in range(5):
            print(f"\n📝 Training attempt {attempt + 1}/5")
            timings, typed_text = self.capture_keystroke_timing(training_phrase)
            
            if typed_text.lower().replace(' ', '') == training_phrase.lower().replace(' ', ''):
                all_timings.append(timings)
                print("✅ Pattern recorded successfully")
            else:
                print("❌ Text mismatch, please try again")
                attempt -= 1  # Don't count this attempt
        
        # Calculate average patterns and thresholds
        if all_timings:
            avg_timings = np.mean(all_timings, axis=0)
            std_timings = np.std(all_timings, axis=0)
            
            self.keystroke_patterns[username] = {
                'phrase': training_phrase,
                'avg_timings': avg_timings.tolist(),
                'std_timings': std_timings.tolist(),
                'threshold': 0.3  # Tolerance threshold
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
        timings, typed_text = self.capture_keystroke_timing(phrase)
        
        # Check if text matches
        if typed_text.lower().replace(' ', '') != phrase.lower().replace(' ', ''):
            print("❌ Text mismatch")
            return False
        
        # Check timing patterns
        if len(timings) != len(pattern['avg_timings']):
            print("❌ Timing pattern length mismatch")
            return False
        
        # Calculate similarity score
        avg_timings = np.array(pattern['avg_timings'])
        std_timings = np.array(pattern['std_timings'])
        test_timings = np.array(timings)
        
        # Normalized difference
        differences = np.abs(test_timings - avg_timings) / (std_timings + 0.001)
        similarity_score = np.mean(differences)
        
        threshold = pattern['threshold']
        
        print(f"📊 Similarity score: {similarity_score:.3f} (threshold: {threshold})")
        
        if similarity_score <= threshold:
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed - keystroke pattern doesn't match")
            return False
    
    def initialize_camera(self):
        """Initialize camera for intruder detection"""
        try:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                print("📷 Camera initialized successfully")
                return True
            else:
                print("❌ Failed to initialize camera")
                return False
        except Exception as e:
            print(f"❌ Camera error: {e}")
            return False
    
    def capture_intruder_photo(self):
        """Capture photo of potential intruder"""
        try:
            if not self.camera or not self.camera.isOpened():
                if not self.initialize_camera():
                    return None
            
            print("📸 Capturing intruder photo...")
            ret, frame = self.camera.read()
            
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"intruder_{timestamp}.jpg"
                filepath = os.path.join("intruder_photos", filename)
                
                # Create directory if it doesn't exist
                os.makedirs("intruder_photos", exist_ok=True)
                
                # Save photo
                cv2.imwrite(filepath, frame)
                
                # Add face detection rectangle
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                
                # Save enhanced photo
                enhanced_filename = f"intruder_enhanced_{timestamp}.jpg"
                enhanced_filepath = os.path.join("intruder_photos", enhanced_filename)
                cv2.imwrite(enhanced_filepath, frame)
                
                print(f"📸 Intruder photo saved: {enhanced_filepath}")
                return enhanced_filepath
            
        except Exception as e:
            print(f"❌ Error capturing photo: {e}")
        
        return None
    
    def send_firebase_alert(self, alert_type, message, photo_path=None):
        """Send alert to Firebase for mobile app"""
        try:
            alert_data = {
                'type': alert_type,
                'message': message,
                'timestamp': int(time.time() * 1000),
                'phone': self.user_phone,
                'severity': 'critical',
                'location': 'Laptop Security System',
                'action_required': True
            }
            
            if photo_path and os.path.exists(photo_path):
                # Convert image to base64 for Firebase
                with open(photo_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    alert_data['photo'] = img_data[:50000]  # Limit size for Firebase
            
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
        """Send SMS alert using Twilio"""
        try:
            # For demo purposes, we'll simulate SMS
            print(f"📱 SMS Alert to {self.user_phone}:")
            print(f"🚨 {message}")
            print("💡 Reply 'SHUTDOWN' to immediately shutdown the laptop")
            
            # In production, use Twilio:
            # client = Client(self.twilio_sid, self.twilio_token)
            # message = client.messages.create(
            #     body=message,
            #     from_=self.twilio_phone,
            #     to=f"+91{self.user_phone}"
            # )
            
            return True
            
        except Exception as e:
            print(f"❌ SMS alert error: {e}")
            return False
    
    def make_emergency_call(self):
        """Make emergency phone call"""
        try:
            print(f"📞 Making emergency call to {self.user_phone}")
            print("🔊 'SECURITY BREACH DETECTED ON YOUR LAPTOP. UNAUTHORIZED ACCESS ATTEMPT.'")
            print("💡 In production, this would use Twilio Voice API")
            
            # In production, use Twilio Voice API:
            # client = Client(self.twilio_sid, self.twilio_token)
            # call = client.calls.create(
            #     twiml='<Response><Say>Security breach detected on your laptop. Unauthorized access attempt. Reply SHUTDOWN to secure your system.</Say></Response>',
            #     to=f"+91{self.user_phone}",
            #     from_=self.twilio_phone
            # )
            
            return True
            
        except Exception as e:
            print(f"❌ Emergency call error: {e}")
            return False
    
    def check_sms_commands(self):
        """Check for SMS commands like 'SHUTDOWN'"""
        try:
            # Check Firebase for emergency commands
            response = requests.get(f"{self.firebase_url}/emergency_commands.json")
            
            if response.status_code == 200:
                commands = response.json()
                if commands:
                    for cmd_id, cmd_data in commands.items():
                        if cmd_data.get('command') == 'SHUTDOWN' and cmd_data.get('phone') == self.user_phone:
                            # Verify timestamp (within last 5 minutes)
                            cmd_time = cmd_data.get('timestamp', 0)
                            current_time = int(time.time() * 1000)
                            
                            if current_time - cmd_time < 300000:  # 5 minutes
                                print("🚨 EMERGENCY SHUTDOWN COMMAND RECEIVED!")
                                self.emergency_shutdown()
                                return True
            
        except Exception as e:
            print(f"❌ SMS command check error: {e}")
        
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
        subprocess.run(['shutdown', '/s', '/f', '/t', '0'], shell=True)
    
    def handle_failed_authentication(self):
        """Handle failed authentication attempts"""
        self.failed_attempts += 1
        print(f"❌ Authentication failed! Attempts: {self.failed_attempts}/{self.max_attempts}")
        
        if self.failed_attempts >= self.max_attempts:
            print("🚨 SECURITY BREACH DETECTED!")
            
            # Capture intruder photo
            photo_path = self.capture_intruder_photo()
            
            # Send alerts
            alert_message = f"SECURITY BREACH: {self.failed_attempts} failed login attempts detected on your laptop at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send Firebase alert
            self.send_firebase_alert("security_breach", alert_message, photo_path)
            
            # Send SMS alert
            sms_message = f"🚨 SECURITY ALERT: Unauthorized access detected on your laptop. {self.failed_attempts} failed attempts. Photo captured. Reply 'SHUTDOWN' to secure system."
            self.send_sms_alert(sms_message)
            
            # Make emergency call
            self.make_emergency_call()
            
            # Start monitoring for SMS commands
            self.start_sms_monitoring()
            
            return True
        
        return False
    
    def start_sms_monitoring(self):
        """Start monitoring for SMS commands"""
        def sms_monitor():
            print("📱 Monitoring for SMS commands...")
            for _ in range(60):  # Monitor for 1 minute
                if self.check_sms_commands():
                    break
                time.sleep(1)
        
        sms_thread = threading.Thread(target=sms_monitor, daemon=True)
        sms_thread.start()
    
    def run_security_system(self):
        """Main security system loop"""
        print("🚀 Starting Advanced Security System")
        print("=" * 50)
        
        # Initialize camera
        self.initialize_camera()
        
        while True:
            print("\n🔒 SECURITY SYSTEM MENU")
            print("1. Train new user keystroke pattern")
            print("2. Authenticate existing user")
            print("3. Start continuous monitoring")
            print("4. Test emergency alerts")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
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
                if not self.is_authenticated:
                    print("❌ Authentication required first!")
                    continue
                
                print("👁️ Starting continuous monitoring...")
                print("💡 System will monitor for unauthorized access")
                print("Press Ctrl+C to stop monitoring")
                
                try:
                    self.start_continuous_monitoring()
                except KeyboardInterrupt:
                    print("\n🛑 Monitoring stopped")
            
            elif choice == '4':
                print("🧪 Testing emergency alerts...")
                photo_path = self.capture_intruder_photo()
                self.send_firebase_alert("test_alert", "This is a test security alert", photo_path)
                self.send_sms_alert("🧪 Test alert: Security system is working properly")
                print("✅ Test alerts sent!")
            
            elif choice == '5':
                print("👋 Shutting down security system...")
                if self.camera:
                    self.camera.release()
                break
            
            else:
                print("❌ Invalid choice!")
    
    def start_continuous_monitoring(self):
        """Start continuous monitoring mode"""
        self.is_monitoring = True
        
        def monitor_loop():
            while self.is_monitoring:
                # Check for SMS commands
                self.check_sms_commands()
                
                # Monitor system activity (simplified)
                time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Keep main thread alive
        while self.is_monitoring:
            time.sleep(1)

def main():
    """Main entry point"""
    try:
        security_system = AdvancedSecuritySystem()
        security_system.run_security_system()
    except KeyboardInterrupt:
        print("\n🛑 Security system stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    main()
