import requests
import json
import os
from datetime import datetime
import subprocess
import platform
import webbrowser
from urllib.parse import quote
import time

class InstantMobileAlerts:
    def __init__(self, config_file="mobile_alert_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Load mobile alert configuration"""
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
        """Create default mobile alert configuration"""
        config = {
            'whatsapp': {
                'enabled': True,
                'phone_number': '',  # Format: +1234567890
                'use_web': True
            },
            'telegram': {
                'enabled': False,
                'bot_token': '',
                'chat_id': ''
            },
            'discord': {
                'enabled': False,
                'webhook_url': ''
            },
            'pushbullet': {
                'enabled': False,
                'api_key': '',
                'device_iden': ''
            },
            'ntfy': {
                'enabled': True,
                'topic': 'security_alerts_' + str(int(time.time())),
                'server': 'https://ntfy.sh'
            },
            'desktop_notification': {
                'enabled': True,
                'sound': True,
                'popup_duration': 10
            },
            'phone_call': {
                'enabled': False,
                'twilio_sid': '',
                'twilio_token': '',
                'from_number': '',
                'to_number': ''
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"Mobile alert config created at {self.config_file}")
        return config
        
    def send_whatsapp_alert(self, message, photo_path=None):
        """Send WhatsApp alert via web interface"""
        try:
            whatsapp_config = self.config.get('whatsapp', {})
            if not whatsapp_config.get('enabled') or not whatsapp_config.get('phone_number'):
                return False
                
            phone = whatsapp_config['phone_number'].replace('+', '').replace(' ', '')
            encoded_message = quote(f"🚨 SECURITY ALERT 🚨\n\n{message}")
            
            whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
            
            print("🔥 OPENING WHATSAPP FOR INSTANT ALERT!")
            webbrowser.open(whatsapp_url)
            return True
            
        except Exception as e:
            print(f"WhatsApp alert failed: {e}")
            return False
            
    def send_telegram_alert(self, message, photo_path=None):
        """Send Telegram alert via bot"""
        try:
            telegram_config = self.config.get('telegram', {})
            if not telegram_config.get('enabled'):
                return False
                
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                return False
                
            # Send text message
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': f"🚨 SECURITY ALERT 🚨\n\n{message}",
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            # Send photo if available
            if photo_path and os.path.exists(photo_path):
                photo_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
                with open(photo_path, 'rb') as photo:
                    files = {'photo': photo}
                    photo_data = {'chat_id': chat_id, 'caption': 'Intruder Photo'}
                    requests.post(photo_url, data=photo_data, files=files, timeout=10)
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Telegram alert failed: {e}")
            return False
            
    def send_discord_alert(self, message, photo_path=None):
        """Send Discord alert via webhook"""
        try:
            discord_config = self.config.get('discord', {})
            if not discord_config.get('enabled'):
                return False
                
            webhook_url = discord_config.get('webhook_url')
            if not webhook_url:
                return False
                
            data = {
                'content': f"🚨 **SECURITY ALERT** 🚨\n\n{message}",
                'username': 'Security System'
            }
            
            response = requests.post(webhook_url, json=data, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Discord alert failed: {e}")
            return False
            
    def send_pushbullet_alert(self, message, photo_path=None):
        """Send Pushbullet notification"""
        try:
            pushbullet_config = self.config.get('pushbullet', {})
            if not pushbullet_config.get('enabled'):
                return False
                
            api_key = pushbullet_config.get('api_key')
            if not api_key:
                return False
                
            url = 'https://api.pushbullet.com/v2/pushes'
            headers = {'Authorization': f'Bearer {api_key}'}
            data = {
                'type': 'note',
                'title': '🚨 SECURITY ALERT',
                'body': message
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Pushbullet alert failed: {e}")
            return False
            
    def send_ntfy_alert(self, message, photo_path=None):
        """Send ntfy.sh notification (no signup required!)"""
        try:
            ntfy_config = self.config.get('ntfy', {})
            if not ntfy_config.get('enabled'):
                return False
                
            topic = ntfy_config.get('topic')
            server = ntfy_config.get('server', 'https://ntfy.sh')
            
            if not topic:
                return False
                
            url = f"{server}/{topic}"
            headers = {
                'Title': '🚨 SECURITY BREACH',
                'Priority': 'urgent',
                'Tags': 'warning,skull'
            }
            
            response = requests.post(url, data=message, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"📱 INSTANT NOTIFICATION SENT!")
                print(f"📱 Install ntfy app and subscribe to: {topic}")
                print(f"📱 Or visit: {server}/{topic}")
                return True
                
            return False
            
        except Exception as e:
            print(f"ntfy alert failed: {e}")
            return False
            
    def send_desktop_notification(self, message, photo_path=None):
        """Send desktop notification"""
        try:
            desktop_config = self.config.get('desktop_notification', {})
            if not desktop_config.get('enabled'):
                return False
                
            system = platform.system()
            title = "🚨 SECURITY BREACH DETECTED"
            
            if system == "Windows":
                # Windows toast notification
                try:
                    import win10toast
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(
                        title,
                        message,
                        duration=desktop_config.get('popup_duration', 10),
                        icon_path=photo_path if photo_path and os.path.exists(photo_path) else None
                    )
                    return True
                except ImportError:
                    # Fallback to PowerShell notification
                    ps_command = f'''
                    Add-Type -AssemblyName System.Windows.Forms
                    $notification = New-Object System.Windows.Forms.NotifyIcon
                    $notification.Icon = [System.Drawing.SystemIcons]::Warning
                    $notification.BalloonTipTitle = "{title}"
                    $notification.BalloonTipText = "{message}"
                    $notification.Visible = $true
                    $notification.ShowBalloonTip(10000)
                    '''
                    subprocess.run(["powershell", "-Command", ps_command], shell=True)
                    return True
                    
            elif system == "Darwin":  # macOS
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"'
                ])
                return True
                
            elif system == "Linux":
                subprocess.run([
                    "notify-send", title, message
                ])
                return True
                
            return False
            
        except Exception as e:
            print(f"Desktop notification failed: {e}")
            return False
            
    def make_phone_call_alert(self, message):
        """Make an actual phone call using Twilio"""
        try:
            phone_config = self.config.get('phone_call', {})
            if not phone_config.get('enabled'):
                return False
                
            try:
                from twilio.rest import Client
            except ImportError:
                print("Twilio not installed. Run: pip install twilio")
                return False
                
            account_sid = phone_config.get('twilio_sid')
            auth_token = phone_config.get('twilio_token')
            from_number = phone_config.get('from_number')
            to_number = phone_config.get('to_number')
            
            if not all([account_sid, auth_token, from_number, to_number]):
                return False
                
            client = Client(account_sid, auth_token)
            
            # Create TwiML for voice message
            twiml = f'''
            <Response>
                <Say voice="alice">
                    Security Alert! Security Alert! 
                    Unauthorized access detected on your computer at {datetime.now().strftime('%I %M %p')}.
                    Please check your system immediately.
                    This is an automated security alert.
                </Say>
                <Pause length="2"/>
                <Say voice="alice">
                    Security Alert! Unauthorized access detected.
                </Say>
            </Response>
            '''
            
            call = client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=from_number
            )
            
            print(f"📞 EMERGENCY CALL INITIATED: {call.sid}")
            return True
            
        except Exception as e:
            print(f"Phone call alert failed: {e}")
            return False
            
    def send_instant_alerts(self, message, photo_path=None):
        """Send all enabled instant alerts"""
        print("\n" + "="*60)
        print("🚨 SENDING INSTANT MOBILE ALERTS 🚨")
        print("="*60)
        
        alert_methods = [
            ("Desktop Notification", self.send_desktop_notification),
            ("ntfy Push Notification", self.send_ntfy_alert),
            ("WhatsApp", self.send_whatsapp_alert),
            ("Telegram", self.send_telegram_alert),
            ("Discord", self.send_discord_alert),
            ("Pushbullet", self.send_pushbullet_alert),
            ("Phone Call", self.make_phone_call_alert)
        ]
        
        success_count = 0
        
        for method_name, method_func in alert_methods:
            try:
                if method_func(message, photo_path):
                    print(f"✅ {method_name}: SUCCESS")
                    success_count += 1
                else:
                    print(f"❌ {method_name}: Not configured or failed")
            except Exception as e:
                print(f"❌ {method_name}: Error - {e}")
                
        print(f"\n📱 {success_count}/{len(alert_methods)} alert methods succeeded")
        print("="*60)
        
        return success_count > 0
        
    def setup_ntfy_quick(self):
        """Quick setup for ntfy (no signup required)"""
        print("\n🚀 QUICK MOBILE ALERT SETUP (No signup required!)")
        print("="*50)
        
        topic = self.config['ntfy']['topic']
        server = self.config['ntfy']['server']
        
        print(f"1. Install 'ntfy' app on your phone from:")
        print(f"   📱 Android: Google Play Store")
        print(f"   📱 iPhone: App Store")
        print(f"\n2. Subscribe to topic: {topic}")
        print(f"   Or visit: {server}/{topic}")
        print(f"\n3. You'll receive INSTANT notifications!")
        
        # Send test notification
        test_message = f"✅ Mobile alerts are now active! You'll receive instant notifications here."
        if self.send_ntfy_alert(test_message):
            print(f"\n🎉 Test notification sent! Check your phone!")
        
        return True
        
    def configure_whatsapp(self, phone_number):
        """Configure WhatsApp alerts"""
        self.config['whatsapp']['phone_number'] = phone_number
        self.config['whatsapp']['enabled'] = True
        self.save_config()
        print(f"✅ WhatsApp configured for {phone_number}")
        
    def configure_telegram(self, bot_token, chat_id):
        """Configure Telegram alerts"""
        self.config['telegram']['bot_token'] = bot_token
        self.config['telegram']['chat_id'] = chat_id
        self.config['telegram']['enabled'] = True
        self.save_config()
        print("✅ Telegram configured")
        
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

def main():
    """Setup and test instant mobile alerts"""
    alerts = InstantMobileAlerts()
    
    print("🚨 INSTANT MOBILE ALERT SYSTEM 🚨")
    print("="*40)
    
    while True:
        print("\n1. 🚀 Quick Setup (ntfy - No signup!)")
        print("2. 📱 Configure WhatsApp")
        print("3. 🤖 Configure Telegram")
        print("4. 🎮 Configure Discord")
        print("5. 📲 Configure Pushbullet")
        print("6. 📞 Configure Phone Calls")
        print("7. 🧪 Test All Alerts")
        print("8. 📋 View Configuration")
        print("9. ❌ Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            alerts.setup_ntfy_quick()
            
        elif choice == '2':
            phone = input("Enter your WhatsApp number (with country code, e.g., +1234567890): ").strip()
            if phone:
                alerts.configure_whatsapp(phone)
                
        elif choice == '3':
            print("\nTelegram Setup:")
            print("1. Message @BotFather on Telegram")
            print("2. Create a bot with /newbot")
            print("3. Get your bot token")
            print("4. Message your bot, then visit: https://api.telegram.org/bot<TOKEN>/getUpdates")
            print("5. Find your chat_id in the response")
            
            bot_token = input("Enter bot token: ").strip()
            chat_id = input("Enter chat ID: ").strip()
            
            if bot_token and chat_id:
                alerts.configure_telegram(bot_token, chat_id)
                
        elif choice == '4':
            print("\nDiscord Setup:")
            print("1. Create a Discord webhook in your server")
            print("2. Copy the webhook URL")
            
            webhook = input("Enter Discord webhook URL: ").strip()
            if webhook:
                alerts.config['discord']['webhook_url'] = webhook
                alerts.config['discord']['enabled'] = True
                alerts.save_config()
                print("✅ Discord configured")
                
        elif choice == '5':
            print("\nPushbullet Setup:")
            print("1. Go to https://www.pushbullet.com/")
            print("2. Create account and get API key")
            
            api_key = input("Enter Pushbullet API key: ").strip()
            if api_key:
                alerts.config['pushbullet']['api_key'] = api_key
                alerts.config['pushbullet']['enabled'] = True
                alerts.save_config()
                print("✅ Pushbullet configured")
                
        elif choice == '6':
            print("\nPhone Call Setup (Twilio):")
            print("1. Sign up at https://www.twilio.com/")
            print("2. Get Account SID, Auth Token, and phone number")
            
            sid = input("Enter Twilio Account SID: ").strip()
            token = input("Enter Auth Token: ").strip()
            from_num = input("Enter Twilio phone number: ").strip()
            to_num = input("Enter your phone number: ").strip()
            
            if all([sid, token, from_num, to_num]):
                alerts.config['phone_call'].update({
                    'twilio_sid': sid,
                    'twilio_token': token,
                    'from_number': from_num,
                    'to_number': to_num,
                    'enabled': True
                })
                alerts.save_config()
                print("✅ Phone calls configured")
                
        elif choice == '7':
            test_message = "🧪 This is a test security alert from your keystroke security system!"
            alerts.send_instant_alerts(test_message)
            
        elif choice == '8':
            print("\nCurrent Configuration:")
            for service, config in alerts.config.items():
                status = "✅ Enabled" if config.get('enabled') else "❌ Disabled"
                print(f"{service}: {status}")
                
        elif choice == '9':
            break
            
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
