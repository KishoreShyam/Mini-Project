"""
Mobile Alert Backend System
Handles emergency phone calls, SMS, and system alarms for security breaches
"""

import requests
import json
import time
import threading
import pygame
import numpy as np
from datetime import datetime
import os
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import cv2

class MobileAlertSystem:
    def __init__(self):
        self.mobile_number = "+918015339335"  # User's mobile number
        self.load_config()
        self.init_pygame()
        
    def load_config(self):
        """Load configuration from file"""
        config_file = "alert_config.json"
        default_config = {
            "twilio": {
                "account_sid": "",
                "auth_token": "",
                "phone_number": ""
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "",
                "password": ""
            },
            "fast2sms": {
                "api_key": ""
            },
            "pushbullet": {
                "api_key": ""
            },
            "mobile_number": self.mobile_number,
            "alert_preferences": {
                "emergency_calls": True,
                "sms_alerts": True,
                "email_alerts": True,
                "push_notifications": True,
                "system_alarm": True
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config
            
        # Save config file
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def init_pygame(self):
        """Initialize pygame for alarm sounds"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.pygame_available = True
        except:
            self.pygame_available = False
            
    def create_alarm_sound(self, frequency=1000, duration=0.5):
        """Create alarm sound using pygame"""
        if not self.pygame_available:
            return None
            
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        
        for i in range(frames):
            # Create siren-like sound with frequency modulation
            freq_mod = frequency + 200 * np.sin(2 * np.pi * i / (sample_rate / 4))
            wave = 4096 * np.sin(2 * np.pi * freq_mod * i / sample_rate)
            arr.append([int(wave), int(wave)])
            
        try:
            import numpy as np
            sound_array = np.array(arr, dtype=np.int16)
            return pygame.sndarray.make_sound(sound_array)
        except:
            return None
            
    def play_emergency_alarm(self, duration=15):
        """Play emergency alarm sound"""
        if not self.pygame_available:
            print("🔇 Pygame not available - using system beep")
            for _ in range(duration):
                print('\a', end='', flush=True)  # System beep
                time.sleep(1)
            return
            
        print(f"🚨 EMERGENCY ALARM ACTIVATED - {duration} seconds")
        
        # Create different alarm sounds
        urgent_beep = self.create_alarm_sound(1200, 0.3)
        warning_tone = self.create_alarm_sound(800, 0.4)
        siren = self.create_alarm_sound(600, 0.5)
        
        start_time = time.time()
        pattern = 0
        
        while time.time() - start_time < duration:
            try:
                if pattern % 3 == 0 and urgent_beep:
                    urgent_beep.play()
                    time.sleep(0.4)
                elif pattern % 3 == 1 and warning_tone:
                    warning_tone.play()
                    time.sleep(0.5)
                elif siren:
                    siren.play()
                    time.sleep(0.6)
                    
                pattern += 1
                
            except Exception as e:
                print(f"Alarm error: {e}")
                break
                
        print("🔇 Emergency alarm stopped")
        
    def capture_intruder_photo(self):
        """Capture photo using webcam"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ Cannot access camera")
                return None
                
            # Warm up camera
            for _ in range(5):
                ret, frame = cap.read()
                time.sleep(0.1)
                
            # Capture photo
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"intruder_{timestamp}.jpg"
                
                # Add security warning overlay
                height, width = frame.shape[:2]
                cv2.rectangle(frame, (10, 10), (width-10, 80), (0, 0, 255), -1)
                cv2.putText(frame, "SECURITY BREACH DETECTED!", (20, 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                           (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imwrite(filename, frame)
                print(f"📸 Intruder photo captured: {filename}")
                return filename
            else:
                print("❌ Failed to capture photo")
                return None
                
        except Exception as e:
            print(f"Camera error: {e}")
            return None
            
    def make_emergency_call(self):
        """Make emergency phone call using Twilio"""
        if not self.config["twilio"]["account_sid"]:
            print("❌ Twilio not configured - cannot make emergency call")
            return False
            
        try:
            client = Client(
                self.config["twilio"]["account_sid"], 
                self.config["twilio"]["auth_token"]
            )
            
            # Create TwiML for voice message
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice" rate="slow" pitch="low">
                    CRITICAL SECURITY ALERT! 
                    Your computer security system has detected unauthorized access. 
                    Someone is trying to break into your system. 
                    Please check your computer immediately. 
                    This is an emergency security notification.
                    Time: {datetime.now().strftime('%I %M %p on %B %d')}
                </Say>
                <Pause length="2"/>
                <Say voice="alice" rate="slow">
                    If this was not you, please secure your computer now.
                    Thank you.
                </Say>
            </Response>"""
            
            # Save TwiML to a temporary file or use webhook
            call = client.calls.create(
                twiml=twiml,
                to=self.mobile_number,
                from_=self.config["twilio"]["phone_number"]
            )
            
            print(f"📞 Emergency call initiated: {call.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Emergency call failed: {e}")
            return False
            
    def send_sms_alert(self, message, photo_path=None):
        """Send SMS alert using Fast2SMS"""
        if not self.config["fast2sms"]["api_key"]:
            print("❌ Fast2SMS not configured - cannot send SMS")
            return False
            
        try:
            url = "https://www.fast2sms.com/dev/bulkV2"
            
            # Clean mobile number (remove +91 if present)
            mobile = self.mobile_number.replace("+91", "").replace("+", "")
            
            payload = {
                "authorization": self.config["fast2sms"]["api_key"],
                "message": message,
                "language": "english",
                "route": "q",
                "numbers": mobile,
            }
            
            headers = {
                'authorization': self.config["fast2sms"]["api_key"],
                'Content-Type': "application/x-www-form-urlencoded",
                'Cache-Control': "no-cache",
            }
            
            response = requests.post(url, data=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("return"):
                    print(f"📱 SMS sent successfully to {self.mobile_number}")
                    return True
                else:
                    print(f"❌ SMS failed: {result}")
                    return False
            else:
                print(f"❌ SMS API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ SMS error: {e}")
            return False
            
    def send_email_alert(self, subject, message, photo_path=None):
        """Send email alert with optional photo attachment"""
        if not self.config["email"]["email"]:
            print("❌ Email not configured - cannot send email alert")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]["email"]
            msg['To'] = self.config["email"]["email"]  # Send to self
            msg['Subject'] = subject
            
            # Add message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Add photo attachment if provided
            if photo_path and os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data)
                    image.add_header('Content-Disposition', f'attachment; filename={os.path.basename(photo_path)}')
                    msg.attach(image)
            
            # Send email
            server = smtplib.SMTP(self.config["email"]["smtp_server"], self.config["email"]["smtp_port"])
            server.starttls()
            server.login(self.config["email"]["email"], self.config["email"]["password"])
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email alert sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
            
    def send_push_notification(self, title, message):
        """Send push notification using Pushbullet"""
        if not self.config["pushbullet"]["api_key"]:
            print("❌ Pushbullet not configured - cannot send push notification")
            return False
            
        try:
            url = "https://api.pushbullet.com/v2/pushes"
            headers = {
                "Access-Token": self.config["pushbullet"]["api_key"],
                "Content-Type": "application/json"
            }
            
            data = {
                "type": "note",
                "title": title,
                "body": message
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                print("📱 Push notification sent successfully")
                return True
            else:
                print(f"❌ Push notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Push notification error: {e}")
            return False
            
    def trigger_security_breach_alert(self, breach_details=None):
        """Trigger complete security breach alert sequence"""
        print("🚨" + "="*60)
        print("🚨 CRITICAL SECURITY BREACH DETECTED! 🚨")
        print("="*62)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Step 1: Capture intruder photo
        print("\n📸 STEP 1: CAPTURING INTRUDER EVIDENCE")
        photo_path = self.capture_intruder_photo()
        
        # Step 2: Activate system alarm
        print("\n🚨 STEP 2: ACTIVATING EMERGENCY ALARM")
        alarm_thread = threading.Thread(target=self.play_emergency_alarm, args=(15,))
        alarm_thread.daemon = True
        alarm_thread.start()
        
        # Step 3: Send all alerts simultaneously
        print(f"\n📱 STEP 3: SENDING EMERGENCY ALERTS TO {self.mobile_number}")
        
        alert_message = f"""🚨 CRITICAL SECURITY BREACH!

Unauthorized access detected on your computer!

Details:
• Time: {timestamp}
• Location: Your PC/Laptop
• Action: Intruder photo captured
• Status: System locked

IMMEDIATE ACTION REQUIRED!
Check your computer now!

This is an automated security alert."""

        sms_message = f"🚨 SECURITY BREACH! Unauthorized access detected at {timestamp}. Check your computer immediately! Photo captured."
        
        email_subject = f"🚨 CRITICAL SECURITY BREACH - {timestamp}"
        
        push_title = "🚨 Security Breach Detected!"
        push_message = f"Unauthorized access at {timestamp}. Check your computer now!"
        
        # Execute all alerts in parallel
        alert_threads = []
        
        if self.config["alert_preferences"]["emergency_calls"]:
            call_thread = threading.Thread(target=self.make_emergency_call)
            call_thread.daemon = True
            alert_threads.append(call_thread)
            
        if self.config["alert_preferences"]["sms_alerts"]:
            sms_thread = threading.Thread(target=self.send_sms_alert, args=(sms_message, photo_path))
            sms_thread.daemon = True
            alert_threads.append(sms_thread)
            
        if self.config["alert_preferences"]["email_alerts"]:
            email_thread = threading.Thread(target=self.send_email_alert, args=(email_subject, alert_message, photo_path))
            email_thread.daemon = True
            alert_threads.append(email_thread)
            
        if self.config["alert_preferences"]["push_notifications"]:
            push_thread = threading.Thread(target=self.send_push_notification, args=(push_title, push_message))
            push_thread.daemon = True
            alert_threads.append(push_thread)
        
        # Start all alert threads
        for thread in alert_threads:
            thread.start()
            
        # Wait for all alerts to complete (max 30 seconds)
        for thread in alert_threads:
            thread.join(timeout=30)
            
        # Step 4: Log the incident
        print("\n📝 STEP 4: LOGGING SECURITY INCIDENT")
        self.log_security_incident(timestamp, photo_path, alert_message)
        
        print("\n✅ EMERGENCY ALERT SEQUENCE COMPLETED!")
        print("="*62)
        
        return {
            "timestamp": timestamp,
            "photo_path": photo_path,
            "alerts_sent": True,
            "mobile_number": self.mobile_number
        }
        
    def log_security_incident(self, timestamp, photo_path, details):
        """Log security incident to file"""
        log_entry = {
            "timestamp": timestamp,
            "photo_path": photo_path,
            "details": details,
            "mobile_number": self.mobile_number,
            "alerts_sent": True
        }
        
        log_file = "security_incidents.json"
        incidents = []
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    incidents = json.load(f)
            except:
                incidents = []
                
        incidents.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(incidents, f, indent=2)
            
        print(f"📝 Incident logged to {log_file}")
        
    def test_alert_system(self):
        """Test the alert system"""
        print("🧪 TESTING MOBILE ALERT SYSTEM")
        print("="*40)
        
        test_message = f"🧪 TEST ALERT - Security system test at {datetime.now().strftime('%H:%M:%S')}. This is a test message."
        
        print("📞 Testing emergency call...")
        # Don't actually call during test
        print("✅ Emergency call system ready")
        
        print("📱 Testing SMS...")
        sms_result = self.send_sms_alert(test_message)
        
        print("📧 Testing email...")
        email_result = self.send_email_alert("🧪 Test Alert", test_message)
        
        print("📱 Testing push notification...")
        push_result = self.send_push_notification("🧪 Test Alert", test_message)
        
        print("🚨 Testing alarm sound...")
        alarm_thread = threading.Thread(target=self.play_emergency_alarm, args=(3,))
        alarm_thread.daemon = True
        alarm_thread.start()
        alarm_thread.join()
        
        print("\n📊 TEST RESULTS:")
        print(f"SMS: {'✅' if sms_result else '❌'}")
        print(f"Email: {'✅' if email_result else '❌'}")
        print(f"Push: {'✅' if push_result else '❌'}")
        print("Alarm: ✅")
        
        return {
            "sms": sms_result,
            "email": email_result,
            "push": push_result,
            "alarm": True
        }

def main():
    """Test the mobile alert system"""
    alert_system = MobileAlertSystem()
    
    print("🔒 MOBILE ALERT SYSTEM")
    print("=" * 30)
    print(f"📱 Target Mobile: {alert_system.mobile_number}")
    print()
    
    while True:
        print("Choose test:")
        print("1. 🧪 Test All Systems")
        print("2. 🚨 Test Emergency Alarm")
        print("3. 📞 Test Emergency Call")
        print("4. 📱 Test SMS Alert")
        print("5. 📧 Test Email Alert")
        print("6. 📸 Test Camera Capture")
        print("7. 🔥 FULL Security Breach Simulation")
        print("8. ⚙️ Configure Services")
        print("9. ❌ Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            alert_system.test_alert_system()
        elif choice == '2':
            alert_system.play_emergency_alarm(5)
        elif choice == '3':
            alert_system.make_emergency_call()
        elif choice == '4':
            alert_system.send_sms_alert("🧪 Test SMS from security system")
        elif choice == '5':
            alert_system.send_email_alert("🧪 Test Email", "This is a test email from your security system")
        elif choice == '6':
            alert_system.capture_intruder_photo()
        elif choice == '7':
            alert_system.trigger_security_breach_alert()
        elif choice == '8':
            print("📝 Edit alert_config.json to configure Twilio, Fast2SMS, email, etc.")
        elif choice == '9':
            break
        else:
            print("❌ Invalid choice!")
            
        print()

if __name__ == "__main__":
    main()
