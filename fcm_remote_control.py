"""
Firebase Cloud Messaging (FCM) Remote Control System
Enables global remote shutdown and control of the security system
"""

import json
import os
import time
import threading
import requests
import subprocess
import platform
from datetime import datetime
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials, messaging
import uuid

class FCMRemoteControl:
    def __init__(self, user_id="main_user"):
        self.user_id = user_id
        self.device_id = self.get_or_create_device_id()
        self.config_file = "fcm_config.json"
        self.device_token = None
        self.encryption_key = None
        self.is_listening = False
        self.listener_thread = None
        
        self.load_config()
        self.setup_encryption()
        
    def get_or_create_device_id(self):
        """Generate or load unique device ID"""
        device_file = "device_id.txt"
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                return f.read().strip()
        else:
            device_id = str(uuid.uuid4())
            with open(device_file, 'w') as f:
                f.write(device_id)
            return device_id
            
    def load_config(self):
        """Load FCM configuration"""
        default_config = {
            "firebase": {
                "project_id": "",
                "private_key_id": "",
                "private_key": "",
                "client_email": "",
                "client_id": "",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            },
            "server": {
                "backend_url": "https://your-backend-server.com/api",
                "api_key": ""
            },
            "device": {
                "device_id": self.device_id,
                "user_id": self.user_id,
                "registration_token": "",
                "last_registration": ""
            },
            "security": {
                "encryption_key": "",
                "hmac_secret": "",
                "allowed_commands": ["shutdown", "lock", "alert", "status"]
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
            
    def save_config(self):
        """Save FCM configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def setup_encryption(self):
        """Setup encryption for secure communication"""
        if not self.config["security"]["encryption_key"]:
            # Generate new encryption key
            self.encryption_key = Fernet.generate_key()
            self.config["security"]["encryption_key"] = base64.b64encode(self.encryption_key).decode()
            
            # Generate HMAC secret
            self.config["security"]["hmac_secret"] = base64.b64encode(os.urandom(32)).decode()
            self.save_config()
        else:
            self.encryption_key = base64.b64decode(self.config["security"]["encryption_key"])
            
        self.cipher = Fernet(self.encryption_key)
        
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not self.config["firebase"]["project_id"]:
                print("❌ Firebase configuration not found. Please configure FCM credentials.")
                return False
                
            # Create credentials from config
            firebase_config = {
                "type": "service_account",
                "project_id": self.config["firebase"]["project_id"],
                "private_key_id": self.config["firebase"]["private_key_id"],
                "private_key": self.config["firebase"]["private_key"].replace("\\n", "\n"),
                "client_email": self.config["firebase"]["client_email"],
                "client_id": self.config["firebase"]["client_id"],
                "auth_uri": self.config["firebase"]["auth_uri"],
                "token_uri": self.config["firebase"]["token_uri"]
            }
            
            # Initialize Firebase
            if not firebase_admin._apps:
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                
            print("✅ Firebase initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            return False
            
    def register_device(self):
        """Register this device with the backend server"""
        try:
            if not self.config["server"]["backend_url"]:
                print("❌ Backend server URL not configured")
                return False
                
            registration_data = {
                "device_id": self.device_id,
                "user_id": self.user_id,
                "device_type": "laptop",
                "platform": platform.system(),
                "hostname": platform.node(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Encrypt registration data
            encrypted_data = self.encrypt_message(registration_data)
            
            response = requests.post(
                f"{self.config['server']['backend_url']}/register",
                json={"encrypted_data": encrypted_data},
                headers={"Authorization": f"Bearer {self.config['server']['api_key']}"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.device_token = result.get("registration_token")
                self.config["device"]["registration_token"] = self.device_token
                self.config["device"]["last_registration"] = datetime.now().isoformat()
                self.save_config()
                
                print(f"✅ Device registered successfully")
                print(f"📱 Registration token: {self.device_token[:20]}...")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
            
    def encrypt_message(self, message):
        """Encrypt message for secure transmission"""
        try:
            message_json = json.dumps(message)
            encrypted = self.cipher.encrypt(message_json.encode())
            
            # Add HMAC for integrity
            hmac_secret = base64.b64decode(self.config["security"]["hmac_secret"])
            signature = hmac.new(hmac_secret, encrypted, hashlib.sha256).hexdigest()
            
            return {
                "data": base64.b64encode(encrypted).decode(),
                "signature": signature,
                "timestamp": time.time()
            }
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            return None
            
    def decrypt_message(self, encrypted_message):
        """Decrypt and verify message"""
        try:
            # Verify timestamp (prevent replay attacks)
            if time.time() - encrypted_message["timestamp"] > 300:  # 5 minutes
                print("❌ Message too old, possible replay attack")
                return None
                
            # Verify HMAC
            encrypted_data = base64.b64decode(encrypted_message["data"])
            hmac_secret = base64.b64decode(self.config["security"]["hmac_secret"])
            expected_signature = hmac.new(hmac_secret, encrypted_data, hashlib.sha256).hexdigest()
            
            if not hmac.compare_digest(expected_signature, encrypted_message["signature"]):
                print("❌ Message integrity check failed")
                return None
                
            # Decrypt message
            decrypted = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return None
            
    def start_listening(self):
        """Start listening for remote commands"""
        if self.is_listening:
            print("⚠️ Already listening for commands")
            return
            
        if not self.initialize_firebase():
            return False
            
        if not self.device_token:
            if not self.register_device():
                return False
                
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
        
        print("🎧 Started listening for remote commands...")
        print(f"📱 Device ID: {self.device_id}")
        print(f"👤 User ID: {self.user_id}")
        return True
        
    def _listen_loop(self):
        """Main listening loop for FCM messages"""
        while self.is_listening:
            try:
                # In a real implementation, you would use FCM's real-time listener
                # For this demo, we'll poll the backend server
                self._poll_for_messages()
                time.sleep(5)  # Poll every 5 seconds
                
            except Exception as e:
                print(f"❌ Listener error: {e}")
                time.sleep(10)  # Wait before retrying
                
    def _poll_for_messages(self):
        """Poll backend server for pending messages"""
        try:
            if not self.config["server"]["backend_url"]:
                return
                
            response = requests.get(
                f"{self.config['server']['backend_url']}/messages/{self.device_id}",
                headers={"Authorization": f"Bearer {self.config['server']['api_key']}"},
                timeout=5
            )
            
            if response.status_code == 200:
                messages = response.json().get("messages", [])
                for message in messages:
                    self._process_message(message)
                    
        except Exception as e:
            # Silently handle polling errors to avoid spam
            pass
            
    def _process_message(self, encrypted_message):
        """Process incoming encrypted message"""
        try:
            # Decrypt message
            message = self.decrypt_message(encrypted_message)
            if not message:
                return
                
            command = message.get("command")
            if command not in self.config["security"]["allowed_commands"]:
                print(f"❌ Unauthorized command: {command}")
                return
                
            print(f"📨 Received command: {command}")
            
            # Execute command
            if command == "shutdown":
                self._execute_shutdown(message)
            elif command == "lock":
                self._execute_lock(message)
            elif command == "alert":
                self._execute_alert(message)
            elif command == "status":
                self._send_status_response(message)
                
        except Exception as e:
            print(f"❌ Message processing error: {e}")
            
    def _execute_shutdown(self, message):
        """Execute system shutdown"""
        try:
            print("🚨 REMOTE SHUTDOWN COMMAND RECEIVED!")
            print(f"📱 From: {message.get('source', 'Unknown')}")
            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Log the shutdown
            self._log_remote_action("shutdown", message)
            
            # Send confirmation
            self._send_command_response(message, "shutdown_initiated", "System shutdown in progress")
            
            # Execute shutdown based on platform
            system = platform.system().lower()
            
            if system == "windows":
                print("💻 Executing Windows shutdown...")
                subprocess.run(["shutdown", "/s", "/f", "/t", "10"], check=True)
                
            elif system == "darwin":  # macOS
                print("🍎 Executing macOS shutdown...")
                subprocess.run(["sudo", "shutdown", "-h", "+1"], check=True)
                
            elif system == "linux":
                print("🐧 Executing Linux shutdown...")
                subprocess.run(["sudo", "shutdown", "-h", "+1"], check=True)
                
            else:
                print(f"❌ Unsupported platform: {system}")
                
        except Exception as e:
            print(f"❌ Shutdown execution failed: {e}")
            self._send_command_response(message, "shutdown_failed", str(e))
            
    def _execute_lock(self, message):
        """Execute system lock"""
        try:
            print("🔒 REMOTE LOCK COMMAND RECEIVED!")
            
            system = platform.system().lower()
            
            if system == "windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            elif system == "darwin":
                subprocess.run(["pmset", "displaysleepnow"], check=True)
            elif system == "linux":
                subprocess.run(["xdg-screensaver", "lock"], check=True)
                
            self._send_command_response(message, "lock_success", "System locked successfully")
            
        except Exception as e:
            print(f"❌ Lock execution failed: {e}")
            self._send_command_response(message, "lock_failed", str(e))
            
    def _execute_alert(self, message):
        """Execute alert command"""
        alert_message = message.get("alert_message", "Security Alert!")
        print(f"🚨 REMOTE ALERT: {alert_message}")
        
        # You could integrate with your existing mobile alert system here
        self._send_command_response(message, "alert_received", "Alert processed")
        
    def _send_status_response(self, message):
        """Send system status response"""
        status = {
            "device_id": self.device_id,
            "user_id": self.user_id,
            "platform": platform.system(),
            "hostname": platform.node(),
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time(),
            "listening": self.is_listening
        }
        
        self._send_command_response(message, "status_response", status)
        
    def _send_command_response(self, original_message, response_type, response_data):
        """Send response back to mobile app"""
        try:
            response = {
                "response_type": response_type,
                "response_data": response_data,
                "original_command_id": original_message.get("command_id"),
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # In a real implementation, you would send this via FCM to the mobile app
            print(f"📤 Response sent: {response_type}")
            
        except Exception as e:
            print(f"❌ Response sending failed: {e}")
            
    def _log_remote_action(self, action, message):
        """Log remote actions for security audit"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "source": message.get("source", "Unknown"),
            "command_id": message.get("command_id"),
            "device_id": self.device_id,
            "user_id": self.user_id
        }
        
        log_file = "remote_actions.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
            
    def send_emergency_alert(self, alert_type, details):
        """Send emergency alert to mobile app"""
        try:
            alert_message = {
                "alert_type": alert_type,
                "details": details,
                "device_id": self.device_id,
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat(),
                "priority": "high"
            }
            
            encrypted_alert = self.encrypt_message(alert_message)
            
            # Send via FCM to mobile app
            if self.config["server"]["backend_url"]:
                response = requests.post(
                    f"{self.config['server']['backend_url']}/alert",
                    json={"encrypted_data": encrypted_alert},
                    headers={"Authorization": f"Bearer {self.config['server']['api_key']}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"📱 Emergency alert sent: {alert_type}")
                    return True
                    
            return False
            
        except Exception as e:
            print(f"❌ Alert sending failed: {e}")
            return False
            
    def stop_listening(self):
        """Stop listening for remote commands"""
        self.is_listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=5)
        print("🔇 Stopped listening for remote commands")
        
    def test_connection(self):
        """Test FCM connection and configuration"""
        print("🧪 Testing FCM Remote Control System...")
        print("=" * 50)
        
        # Test Firebase initialization
        if self.initialize_firebase():
            print("✅ Firebase connection: OK")
        else:
            print("❌ Firebase connection: FAILED")
            
        # Test device registration
        if self.register_device():
            print("✅ Device registration: OK")
        else:
            print("❌ Device registration: FAILED")
            
        # Test encryption
        test_message = {"test": "encryption_test", "timestamp": time.time()}
        encrypted = self.encrypt_message(test_message)
        if encrypted:
            decrypted = self.decrypt_message(encrypted)
            if decrypted and decrypted["test"] == "encryption_test":
                print("✅ Encryption/Decryption: OK")
            else:
                print("❌ Encryption/Decryption: FAILED")
        else:
            print("❌ Encryption: FAILED")
            
        print("=" * 50)
        print(f"📱 Device ID: {self.device_id}")
        print(f"👤 User ID: {self.user_id}")
        
        return True

def main():
    """Test the FCM remote control system"""
    print("🔒 FCM REMOTE CONTROL SYSTEM")
    print("=" * 40)
    
    remote_control = FCMRemoteControl()
    
    while True:
        print("\nChoose option:")
        print("1. 🧪 Test Connection")
        print("2. 🎧 Start Listening for Commands")
        print("3. 🔇 Stop Listening")
        print("4. 📱 Send Test Alert")
        print("5. ⚙️ Configure FCM")
        print("6. 📊 Show Status")
        print("7. ❌ Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == '1':
            remote_control.test_connection()
        elif choice == '2':
            remote_control.start_listening()
        elif choice == '3':
            remote_control.stop_listening()
        elif choice == '4':
            remote_control.send_emergency_alert("test_alert", {"message": "This is a test alert"})
        elif choice == '5':
            print("📝 Edit fcm_config.json to configure Firebase credentials and backend server")
        elif choice == '6':
            print(f"📱 Device ID: {remote_control.device_id}")
            print(f"👤 User ID: {remote_control.user_id}")
            print(f"🎧 Listening: {remote_control.is_listening}")
        elif choice == '7':
            remote_control.stop_listening()
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
