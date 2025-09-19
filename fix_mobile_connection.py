"""
Mobile Connection Diagnostic and Fix Tool
Automatically diagnoses and fixes mobile app connection issues
"""

import subprocess
import socket
import requests
import json
import time
import os
from datetime import datetime

class MobileConnectionFixer:
    def __init__(self):
        self.local_ip = self.get_local_ip()
        self.service_port = 8080
        self.firebase_url = "https://security-control-demo-default-rtdb.firebaseio.com/"
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def test_laptop_service(self):
        """Test if laptop service is running"""
        try:
            response = requests.get(f"http://localhost:{self.service_port}/status", timeout=5)
            if response.status_code == 200:
                print("✅ Laptop service is running")
                return True
            else:
                print(f"❌ Laptop service returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Laptop service not responding: {e}")
            return False
    
    def test_firebase_connection(self):
        """Test Firebase connection"""
        try:
            response = requests.get(f"{self.firebase_url}laptop_status.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and data.get('status') == 'online':
                    last_seen = data.get('last_seen', 0)
                    now = int(time.time() * 1000)
                    if now - last_seen < 120000:  # 2 minutes
                        print("✅ Firebase connection active")
                        return True
                    else:
                        print("⚠️ Firebase data is stale")
                        return False
                else:
                    print("❌ No active laptop status in Firebase")
                    return False
            else:
                print(f"❌ Firebase returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Firebase connection failed: {e}")
            return False
    
    def check_firewall(self):
        """Check Windows Firewall settings"""
        try:
            # Check if port 8080 is blocked
            result = subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'show', 'rule', 
                'name=all', 'dir=in', 'protocol=tcp', 'localport=8080'
            ], capture_output=True, text=True)
            
            if "No rules match" in result.stdout:
                print("⚠️ No firewall rule found for port 8080")
                return False
            else:
                print("✅ Firewall rule exists for port 8080")
                return True
        except Exception as e:
            print(f"❌ Could not check firewall: {e}")
            return False
    
    def create_firewall_rule(self):
        """Create firewall rule for port 8080"""
        try:
            print("🔧 Creating firewall rule for port 8080...")
            result = subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                'name=Security Control App',
                'dir=in', 'action=allow', 'protocol=TCP', 'localport=8080'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Firewall rule created successfully")
                return True
            else:
                print(f"❌ Failed to create firewall rule: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error creating firewall rule: {e}")
            return False
    
    def start_laptop_service(self):
        """Start the laptop service"""
        try:
            print("🚀 Starting laptop service...")
            
            # Check if service file exists
            if not os.path.exists("laptop_service.py"):
                print("❌ laptop_service.py not found!")
                return False
            
            # Start the service in background
            process = subprocess.Popen([
                'python', 'laptop_service.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment for service to start
            time.sleep(3)
            
            # Check if service is running
            if self.test_laptop_service():
                print("✅ Laptop service started successfully")
                return True
            else:
                print("❌ Laptop service failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting laptop service: {e}")
            return False
    
    def diagnose_and_fix(self):
        """Run complete diagnosis and fix"""
        print("🔍 MOBILE CONNECTION DIAGNOSTIC TOOL")
        print("=" * 50)
        print(f"💻 Local IP: {self.local_ip}")
        print(f"🌐 Service Port: {self.service_port}")
        print(f"🔥 Firebase URL: {self.firebase_url}")
        print("=" * 50)
        
        issues_found = []
        fixes_applied = []
        
        # Test 1: Check if laptop service is running
        print("\n🧪 TEST 1: Checking laptop service...")
        if not self.test_laptop_service():
            issues_found.append("Laptop service not running")
            
            # Try to start the service
            if self.start_laptop_service():
                fixes_applied.append("Started laptop service")
            else:
                print("❌ Could not start laptop service automatically")
                print("📋 Manual fix: Run 'python laptop_service.py'")
        
        # Test 2: Check firewall
        print("\n🧪 TEST 2: Checking firewall settings...")
        if not self.check_firewall():
            issues_found.append("Firewall blocking port 8080")
            
            choice = input("Create firewall rule? (y/n): ").strip().lower()
            if choice == 'y':
                if self.create_firewall_rule():
                    fixes_applied.append("Created firewall rule")
        
        # Test 3: Check Firebase connection
        print("\n🧪 TEST 3: Checking Firebase connection...")
        firebase_ok = self.test_firebase_connection()
        if not firebase_ok:
            issues_found.append("Firebase connection not working")
            print("📋 Manual fix: Set up Firebase project or use direct IP connection")
        
        # Test 4: Re-test laptop service after fixes
        print("\n🧪 TEST 4: Re-testing laptop service...")
        service_ok = self.test_laptop_service()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 50)
        
        if issues_found:
            print("❌ Issues found:")
            for issue in issues_found:
                print(f"   • {issue}")
        else:
            print("✅ No issues found!")
        
        if fixes_applied:
            print("\n🔧 Fixes applied:")
            for fix in fixes_applied:
                print(f"   • {fix}")
        
        # Final status
        print(f"\n📱 MOBILE APP CONNECTION STATUS:")
        if service_ok or firebase_ok:
            print("✅ Mobile app should now connect successfully!")
            print(f"📱 Connect to: http://{self.local_ip}:{self.service_port}")
            if firebase_ok:
                print("🔥 Firebase connection also available")
        else:
            print("❌ Mobile app will still show 'Laptop Offline'")
            print("📋 Manual steps required:")
            print("   1. Run: python laptop_service.py")
            print("   2. Check Windows Firewall settings")
            print("   3. Ensure phone and laptop on same WiFi")
        
        return service_ok or firebase_ok

def main():
    """Main diagnostic function"""
    fixer = MobileConnectionFixer()
    
    print("🔒 MOBILE APP CONNECTION FIXER")
    print("=" * 40)
    print("This tool will diagnose and fix connection issues")
    print("between your mobile app and laptop.")
    print()
    
    # Run diagnosis
    success = fixer.diagnose_and_fix()
    
    if success:
        print("\n🎉 CONNECTION FIXED!")
        print("=" * 25)
        print("Your mobile app should now show:")
        print("✅ 'Laptop Connected' (green status)")
        print()
        print("📱 Next steps:")
        print("1. Open your mobile app")
        print("2. Check that status shows connected")
        print("3. Test the emergency shutdown button")
        print("4. Verify all commands work")
    else:
        print("\n❌ MANUAL INTERVENTION REQUIRED")
        print("=" * 35)
        print("Please follow these steps:")
        print("1. Run: start_laptop_service.bat")
        print("2. Check Windows Firewall settings")
        print("3. Ensure phone and laptop on same network")
        print("4. Update IP address in mobile app settings")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()