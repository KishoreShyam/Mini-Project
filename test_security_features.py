"""
Test Security Features
Demonstrates the alarm system and intruder photo capture functionality
"""

import time
from security_system import SecuritySystem
import os

def test_alarm_system():
    """Test the PC alarm system"""
    print("🧪 TESTING PC ALARM SYSTEM")
    print("=" * 40)
    
    security = SecuritySystem()
    
    print("⚠️  WARNING: This will activate a loud alarm!")
    choice = input("Continue? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n🚨 Starting alarm test in 3 seconds...")
        time.sleep(1)
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        
        # Test alarm for 5 seconds
        security.activate_alarm(5)
        print("✅ Alarm test completed!")
    else:
        print("❌ Alarm test cancelled")

def test_camera_capture():
    """Test the intruder photo capture system"""
    print("\n🧪 TESTING INTRUDER PHOTO CAPTURE")
    print("=" * 45)
    
    security = SecuritySystem()
    
    print("📸 This will capture a photo using your webcam")
    choice = input("Continue? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n📷 Starting camera test...")
        print("👀 Look at your camera - photo will be taken in 3 seconds!")
        time.sleep(1)
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        
        photo_path = security.capture_intruder_photo()
        
        if photo_path:
            print(f"✅ Photo captured successfully!")
            print(f"📁 Saved as: {photo_path}")
            
            if os.path.exists(photo_path):
                file_size = os.path.getsize(photo_path)
                print(f"📊 File size: {file_size} bytes")
                print(f"📂 Full path: {os.path.abspath(photo_path)}")
            
            # Test sending photo to mobile
            print("\n📱 Testing photo transmission to mobile...")
            message = "Test intruder photo from security system"
            alert_sent = security.send_alert_notification(photo_path)
            
            if alert_sent:
                print("✅ Photo sent to mobile successfully!")
            else:
                print("❌ Failed to send photo - check notification configuration")
                
        else:
            print("❌ Failed to capture photo")
            print("🔧 Troubleshooting tips:")
            print("   - Check if camera is connected")
            print("   - Close other applications using camera")
            print("   - Try running as administrator")
    else:
        print("❌ Camera test cancelled")

def test_full_security_breach():
    """Test complete security breach scenario"""
    print("\n🧪 TESTING FULL SECURITY BREACH SCENARIO")
    print("=" * 50)
    
    security = SecuritySystem()
    
    print("⚠️  WARNING: This will:")
    print("   🚨 Activate loud alarm for 15 seconds")
    print("   📸 Capture intruder photo")
    print("   📞 Send emergency alerts to +918015339335")
    print("   🔒 Simulate 5-minute lockdown (shortened to 10 seconds for test)")
    
    choice = input("\nProceed with full test? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n🚨 SIMULATING SECURITY BREACH...")
        print("Setting failed attempts to maximum...")
        
        # Simulate 3 failed attempts
        security.failed_attempts = security.max_attempts
        
        print(f"Failed attempts: {security.failed_attempts}/{security.max_attempts}")
        print("\n⏰ Starting security breach response in 3 seconds...")
        time.sleep(3)
        
        # Temporarily reduce lockdown time for testing
        original_handle = security.handle_security_breach
        
        def test_handle_security_breach():
            """Modified security breach handler for testing"""
            print(f"\n" + "="*70)
            print("🚨 CRITICAL SECURITY BREACH DETECTED! 🚨")
            print("="*70)
            print(f"❌ Failed Attempts: {security.failed_attempts}/{security.max_attempts}")
            print(f"🚫 UNAUTHORIZED ACCESS ATTEMPT!")
            print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)
            
            # STEP 1: Capture photo
            print("\n🔍 STEP 1: CAPTURING INTRUDER EVIDENCE")
            photo_path = security.capture_intruder_photo()
            
            # STEP 2: Activate alarm (shortened for test)
            print("\n🚨 STEP 2: ACTIVATING PC ALARM SYSTEM")
            print("🔊 Starting 5-second alarm sequence (shortened for test)...")
            import threading
            alarm_thread = threading.Thread(target=security.activate_alarm, args=(5,))
            alarm_thread.daemon = True
            alarm_thread.start()
            
            # STEP 3: Send alerts
            print("\n📱 STEP 3: SENDING EMERGENCY ALERTS TO MOBILE")
            print(f"📞 Calling +918015339335...")
            
            breach_message = f"""TEST SECURITY BREACH!
            
This is a test of your security system.

Details:
- Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
- Failed Attempts: {security.failed_attempts}
- Status: TEST MODE
- Photo: {'Captured' if photo_path else 'Failed'}

This was a test - your system is working!"""
            
            alert_sent = security.send_alert_notification(photo_path)
            
            # STEP 4: Short lockdown for test
            print("\n🔒 STEP 4: INITIATING TEST LOCKDOWN (10 seconds)")
            for i in range(10, 0, -1):
                print(f"\r🔒 TEST LOCKDOWN: {i:02d} seconds remaining", end="", flush=True)
                time.sleep(1)
            
            print(f"\n✅ Test completed successfully!")
            security.failed_attempts = 0
        
        # Run the test
        test_handle_security_breach()
        
    else:
        print("❌ Full test cancelled")

def main():
    """Main test menu"""
    print("🔒 SECURITY SYSTEM FEATURE TESTING")
    print("=" * 40)
    print(f"📱 Your mobile: +918015339335")
    print()
    
    while True:
        print("\nSelect test:")
        print("1. 🚨 Test PC Alarm System")
        print("2. 📸 Test Camera Capture")
        print("3. 🔥 Test Full Security Breach")
        print("4. 📋 View Test Results")
        print("5. ❌ Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            test_alarm_system()
            
        elif choice == '2':
            test_camera_capture()
            
        elif choice == '3':
            test_full_security_breach()
            
        elif choice == '4':
            print("\n📋 TEST RESULTS")
            print("=" * 20)
            
            # Check for captured photos
            import glob
            photos = glob.glob("intruder_*.jpg")
            if photos:
                print(f"📸 Intruder photos found: {len(photos)}")
                for photo in photos[-3:]:  # Show last 3
                    if os.path.exists(photo):
                        size = os.path.getsize(photo)
                        print(f"   📁 {photo} ({size} bytes)")
            else:
                print("📸 No intruder photos found")
            
            # Check for security logs
            if os.path.exists("security_breaches.json"):
                print("📝 Security breach log exists")
            else:
                print("📝 No security breach log found")
                
            if os.path.exists("security_alerts.json"):
                print("📱 Security alerts log exists")
            else:
                print("📱 No security alerts log found")
                
        elif choice == '5':
            print("👋 Exiting test suite")
            break
            
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
