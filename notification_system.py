import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import requests

class NotificationSystem:
    def __init__(self, config_file="security_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Load notification configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.create_default_config()
        else:
            return self.create_default_config()
            
    def create_default_config(self):
        """Create default notification configuration"""
        config = {
            'email_settings': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',  # Use app password for Gmail
                'recipient_email': ''
            },
            'sms_settings': {
                'api_key': '',
                'api_url': 'https://api.textlocal.in/send/',
                'sender': 'SECURITY',
                'recipient_phone': ''
            },
            'notification_methods': ['email']  # Can include 'email', 'sms'
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"Default notification config created at {self.config_file}")
        print("Please update with your email/SMS credentials!")
        return config
        
    def send_email_alert(self, subject, message, photo_path=None):
        """Send email alert notification"""
        try:
            email_config = self.config.get('email_settings', {})
            
            if not email_config.get('sender_email') or not email_config.get('recipient_email'):
                print("Email configuration incomplete!")
                return False
                
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = subject
            
            # Add body
            body = f"""
SECURITY ALERT - Keystroke Authentication System

{message}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated security alert from your keystroke-based authentication system.
If this was not you, please check your system immediately.

Best regards,
Your Security System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach photo if provided
            if photo_path and os.path.exists(photo_path):
                try:
                    with open(photo_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(photo_path)}'
                    )
                    msg.attach(part)
                except Exception as e:
                    print(f"Error attaching photo: {e}")
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(email_config['sender_email'], email_config['recipient_email'], text)
            server.quit()
            
            print("✅ Email alert sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
            
    def send_sms_alert(self, message):
        """Send SMS alert notification"""
        try:
            sms_config = self.config.get('sms_settings', {})
            
            if not sms_config.get('api_key') or not sms_config.get('recipient_phone'):
                print("SMS configuration incomplete!")
                return False
                
            # Prepare SMS data
            data = {
                'apikey': sms_config['api_key'],
                'numbers': sms_config['recipient_phone'],
                'message': f"SECURITY ALERT: {message}",
                'sender': sms_config.get('sender', 'SECURITY')
            }
            
            # Send SMS via API
            response = requests.post(sms_config['api_url'], data=data)
            
            if response.status_code == 200:
                print("✅ SMS alert sent successfully!")
                return True
            else:
                print(f"❌ SMS sending failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending SMS: {e}")
            return False
            
    def send_alert(self, message, photo_path=None):
        """Send alert using configured notification methods"""
        subject = "🚨 SECURITY BREACH DETECTED"
        success = False
        
        notification_methods = self.config.get('notification_methods', ['email'])
        
        for method in notification_methods:
            if method == 'email':
                if self.send_email_alert(subject, message, photo_path):
                    success = True
            elif method == 'sms':
                if self.send_sms_alert(message):
                    success = True
                    
        return success
        
    def test_notifications(self):
        """Test notification system"""
        test_message = "This is a test message from your security system."
        
        print("Testing notification system...")
        
        if self.send_alert(test_message):
            print("✅ Notification test successful!")
            return True
        else:
            print("❌ Notification test failed!")
            return False
            
    def configure_email(self, sender_email, sender_password, recipient_email):
        """Configure email settings"""
        self.config['email_settings'].update({
            'sender_email': sender_email,
            'sender_password': sender_password,
            'recipient_email': recipient_email
        })
        
        if 'email' not in self.config.get('notification_methods', []):
            self.config.setdefault('notification_methods', []).append('email')
            
        self.save_config()
        print("Email configuration updated!")
        
    def configure_sms(self, api_key, recipient_phone, sender='SECURITY'):
        """Configure SMS settings"""
        self.config['sms_settings'].update({
            'api_key': api_key,
            'recipient_phone': recipient_phone,
            'sender': sender
        })
        
        if 'sms' not in self.config.get('notification_methods', []):
            self.config.setdefault('notification_methods', []).append('sms')
            
        self.save_config()
        print("SMS configuration updated!")
        
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

def main():
    """Test the notification system"""
    notifier = NotificationSystem()
    
    print("Notification System Configuration")
    print("=" * 35)
    
    while True:
        print("\n1. Configure Email")
        print("2. Configure SMS")
        print("3. Test Notifications")
        print("4. Send Test Alert")
        print("5. View Current Config")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            print("\nEmail Configuration:")
            print("Note: For Gmail, use an app password instead of your regular password")
            print("Enable 2-factor authentication and generate an app password")
            
            sender = input("Sender email: ").strip()
            password = input("Sender password (app password for Gmail): ").strip()
            recipient = input("Recipient email: ").strip()
            
            if sender and password and recipient:
                notifier.configure_email(sender, password, recipient)
            else:
                print("All fields are required!")
                
        elif choice == '2':
            print("\nSMS Configuration:")
            print("You need an SMS API service like TextLocal, Twilio, etc.")
            
            api_key = input("API Key: ").strip()
            phone = input("Recipient phone number: ").strip()
            sender_name = input("Sender name (optional, default: SECURITY): ").strip() or "SECURITY"
            
            if api_key and phone:
                notifier.configure_sms(api_key, phone, sender_name)
            else:
                print("API key and phone number are required!")
                
        elif choice == '3':
            notifier.test_notifications()
            
        elif choice == '4':
            message = input("Enter test message: ").strip()
            if message:
                notifier.send_alert(message)
            else:
                print("Message cannot be empty!")
                
        elif choice == '5':
            print("\nCurrent Configuration:")
            config = notifier.config
            
            print(f"Notification methods: {config.get('notification_methods', [])}")
            
            email_config = config.get('email_settings', {})
            if email_config.get('sender_email'):
                print(f"Email sender: {email_config['sender_email']}")
                print(f"Email recipient: {email_config.get('recipient_email', 'Not set')}")
            else:
                print("Email: Not configured")
                
            sms_config = config.get('sms_settings', {})
            if sms_config.get('api_key'):
                print(f"SMS recipient: {sms_config.get('recipient_phone', 'Not set')}")
            else:
                print("SMS: Not configured")
                
        elif choice == '6':
            break
            
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
