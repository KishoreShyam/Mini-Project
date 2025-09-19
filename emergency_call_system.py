import json
import os
import requests
from datetime import datetime
import time

class EmergencyCallSystem:
    def __init__(self, config_file="emergency_call_config.json"):
        self.config_file = config_file
        self.user_phone = "+918015339335"  # User's mobile number
        self.config = self.load_config()
        
    def load_config(self):
        """Load emergency call configuration"""
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
        """Create default emergency call configuration"""
        config = {
            'user_phone': self.user_phone,
            'twilio': {
                'account_sid': '',
                'auth_token': '',
                'from_number': '',
                'enabled': False
            },
            'alternative_services': {
                'textlocal': {
                    'api_key': '',
                    'enabled': False
                },
                'fast2sms': {
                    'api_key': '',
                    'enabled': False
                }
            },
            'emergency_message': {
                'voice_message': "Security Alert! Security Alert! Unauthorized access detected on your computer at {time}. Someone is trying to break into your system. Please check your computer immediately. This is an automated security alert from your keystroke authentication system.",
                'sms_message': "🚨 SECURITY BREACH! Unauthorized access detected on your computer at {time}. Check your system NOW! - Your Security System"
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"Emergency call config created at {self.config_file}")
        return config
        
    def setup_twilio(self):
        """Interactive setup for Twilio (recommended for voice calls)"""
        print("\n🚨 TWILIO SETUP FOR EMERGENCY CALLS 🚨")
        print("=" * 50)
        print("Twilio provides reliable voice calls worldwide.")
        print("Sign up at: https://www.twilio.com/")
        print("You get FREE credits to test the service!")
        print()
        
        print("After signing up:")
        print("1. Go to Console Dashboard")
        print("2. Find your Account SID and Auth Token")
        print("3. Get a Twilio phone number")
        print()
        
        account_sid = input("Enter your Twilio Account SID: ").strip()
        auth_token = input("Enter your Twilio Auth Token: ").strip()
        from_number = input("Enter your Twilio phone number (e.g., +1234567890): ").strip()
        
        if account_sid and auth_token and from_number:
            self.config['twilio'] = {
                'account_sid': account_sid,
                'auth_token': auth_token,
                'from_number': from_number,
                'enabled': True
            }
            self.save_config()
            print("✅ Twilio configured successfully!")
            
            # Test the setup
            test_choice = input("\nTest emergency call now? (y/n): ").strip().lower()
            if test_choice == 'y':
                self.make_emergency_call("This is a test call from your security system.")
                
            return True
        else:
            print("❌ Setup incomplete. Please provide all required information.")
            return False
            
    def setup_fast2sms(self):
        """Setup Fast2SMS for Indian numbers (SMS backup)"""
        print("\n📱 FAST2SMS SETUP (SMS Backup)")
        print("=" * 40)
        print("Fast2SMS provides SMS services for Indian numbers.")
        print("Sign up at: https://www.fast2sms.com/")
        print("Get FREE SMS credits!")
        print()
        
        api_key = input("Enter your Fast2SMS API key: ").strip()
        
        if api_key:
            self.config['alternative_services']['fast2sms'] = {
                'api_key': api_key,
                'enabled': True
            }
            self.save_config()
            print("✅ Fast2SMS configured!")
            
            # Test SMS
            test_choice = input("\nTest SMS alert now? (y/n): ").strip().lower()
            if test_choice == 'y':
                self.send_emergency_sms("🧪 Test SMS from your security system!")
                
            return True
        else:
            print("❌ API key required.")
            return False
            
    def make_emergency_call(self, message):
        """Make emergency voice call using Twilio"""
        try:
            twilio_config = self.config.get('twilio', {})
            if not twilio_config.get('enabled'):
                print("❌ Twilio not configured for voice calls!")
                return False
                
            try:
                from twilio.rest import Client
            except ImportError:
                print("❌ Twilio library not installed!")
                print("Install with: pip install twilio")
                return False
                
            account_sid = twilio_config.get('account_sid')
            auth_token = twilio_config.get('auth_token')
            from_number = twilio_config.get('from_number')
            
            if not all([account_sid, auth_token, from_number]):
                print("❌ Twilio configuration incomplete!")
                return False
                
            client = Client(account_sid, auth_token)
            
            # Format the voice message
            current_time = datetime.now().strftime('%I:%M %p on %B %d')
            voice_message = self.config['emergency_message']['voice_message'].format(time=current_time)
            
            # Create TwiML for voice message
            twiml = f'''
            <Response>
                <Say voice="alice" rate="slow">
                    {voice_message}
                </Say>
                <Pause length="2"/>
                <Say voice="alice" rate="slow">
                    Security Alert! Please check your computer immediately!
                </Say>
                <Pause length="1"/>
                <Say voice="alice">
                    Press any key to acknowledge this alert.
                </Say>
            </Response>
            '''
            
            print(f"\n📞 MAKING EMERGENCY CALL TO {self.user_phone}")
            print("🚨 CALLING NOW... 🚨")
            
            call = client.calls.create(
                twiml=twiml,
                to=self.user_phone,
                from_=from_number
            )
            
            print(f"✅ EMERGENCY CALL INITIATED!")
            print(f"📞 Call SID: {call.sid}")
            print(f"📱 Calling: {self.user_phone}")
            print(f"⏰ Time: {datetime.now().strftime('%I:%M:%S %p')}")
            
            # Log the call
            self.log_emergency_call(call.sid, voice_message)
            
            return True
            
        except Exception as e:
            print(f"❌ Emergency call failed: {e}")
            return False
            
    def send_emergency_sms(self, message):
        """Send emergency SMS as backup"""
        try:
            # Try Fast2SMS first (for Indian numbers)
            fast2sms_config = self.config.get('alternative_services', {}).get('fast2sms', {})
            if fast2sms_config.get('enabled'):
                return self.send_fast2sms(message)
                
            print("❌ No SMS service configured!")
            return False
            
        except Exception as e:
            print(f"❌ Emergency SMS failed: {e}")
            return False
            
    def send_fast2sms(self, message):
        """Send SMS using Fast2SMS"""
        try:
            api_key = self.config['alternative_services']['fast2sms']['api_key']
            
            url = "https://www.fast2sms.com/dev/bulkV2"
            
            # Remove +91 from phone number for Fast2SMS
            phone_number = self.user_phone.replace('+91', '').replace('+', '')
            
            payload = {
                'authorization': api_key,
                'sender_id': 'FSTSMS',
                'message': message,
                'language': 'english',
                'route': 'q',
                'numbers': phone_number
            }
            
            headers = {
                'authorization': api_key,
                'Content-Type': "application/x-www-form-urlencoded",
                'Cache-Control': "no-cache",
            }
            
            response = requests.post(url, data=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('return'):
                    print(f"✅ EMERGENCY SMS SENT to {self.user_phone}")
                    return True
                else:
                    print(f"❌ SMS failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ SMS API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Fast2SMS error: {e}")
            return False
            
    def send_emergency_alert(self, security_message, photo_path=None):
        """Send complete emergency alert (call + SMS)"""
        print("\n" + "="*60)
        print("🚨 EMERGENCY ALERT SYSTEM ACTIVATED 🚨")
        print("="*60)
        
        current_time = datetime.now().strftime('%I:%M %p on %B %d, %Y')
        full_message = f"{security_message} at {current_time}"
        
        success_count = 0
        
        # Priority 1: Make emergency voice call
        print("📞 INITIATING EMERGENCY VOICE CALL...")
        if self.make_emergency_call(full_message):
            success_count += 1
            print("✅ Emergency call: SUCCESS")
        else:
            print("❌ Emergency call: FAILED")
            
        # Priority 2: Send emergency SMS as backup
        print("\n📱 SENDING EMERGENCY SMS BACKUP...")
        sms_message = self.config['emergency_message']['sms_message'].format(time=current_time)
        if self.send_emergency_sms(sms_message):
            success_count += 1
            print("✅ Emergency SMS: SUCCESS")
        else:
            print("❌ Emergency SMS: FAILED")
            
        print(f"\n📊 EMERGENCY ALERTS: {success_count}/2 successful")
        print("="*60)
        
        return success_count > 0
        
    def log_emergency_call(self, call_sid, message):
        """Log emergency call details"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'call_sid': call_sid,
            'phone_number': self.user_phone,
            'message': message,
            'type': 'emergency_call'
        }
        
        # Save to emergency log
        log_file = "emergency_calls.json"
        logs = []
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
                
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def test_emergency_system(self):
        """Test the complete emergency system"""
        print("\n🧪 TESTING EMERGENCY ALERT SYSTEM")
        print("=" * 40)
        
        test_message = "This is a test of your emergency security alert system. If you can hear this, your emergency calls are working perfectly!"
        
        return self.send_emergency_alert(test_message)

def main():
    """Setup and test emergency call system"""
    emergency_system = EmergencyCallSystem()
    
    print("🚨 EMERGENCY CALL SYSTEM SETUP 🚨")
    print("=" * 40)
    print(f"📱 Your phone number: {emergency_system.user_phone}")
    print()
    
    while True:
        print("\n1. 📞 Setup Twilio (Voice Calls)")
        print("2. 📱 Setup Fast2SMS (SMS Backup)")
        print("3. 🧪 Test Emergency System")
        print("4. 📋 View Configuration")
        print("5. 📊 View Emergency Logs")
        print("6. ❌ Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            emergency_system.setup_twilio()
            
        elif choice == '2':
            emergency_system.setup_fast2sms()
            
        elif choice == '3':
            emergency_system.test_emergency_system()
            
        elif choice == '4':
            print("\nCurrent Configuration:")
            print(f"Phone Number: {emergency_system.user_phone}")
            
            twilio_status = "✅ Enabled" if emergency_system.config['twilio']['enabled'] else "❌ Disabled"
            print(f"Twilio Voice Calls: {twilio_status}")
            
            sms_status = "✅ Enabled" if emergency_system.config['alternative_services']['fast2sms']['enabled'] else "❌ Disabled"
            print(f"Fast2SMS Backup: {sms_status}")
            
        elif choice == '5':
            log_file = "emergency_calls.json"
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                    
                    if logs:
                        print(f"\nFound {len(logs)} emergency calls:")
                        for i, log in enumerate(logs[-5:], 1):  # Show last 5
                            print(f"\n{i}. {log['timestamp']}")
                            print(f"   Call SID: {log.get('call_sid', 'N/A')}")
                            print(f"   Phone: {log['phone_number']}")
                            print(f"   Type: {log['type']}")
                    else:
                        print("No emergency calls logged yet.")
                        
                except Exception as e:
                    print(f"Error reading logs: {e}")
            else:
                print("No emergency call logs found.")
                
        elif choice == '6':
            break
            
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
