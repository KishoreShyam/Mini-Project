"""
Keystroke-Based Security System
Main Entry Point

This security system uses typing pattern recognition to authenticate users
and protect devices from unauthorized access.

Author: Security System Developer
Version: 1.0
"""

import sys
import os

def main():
    """Main entry point for the security system"""
    print("🔒 Keystroke-Based Security System")
    print("=" * 40)
    print()
    
    while True:
        print("Choose interface:")
        print("1. 📱 Desktop App (NEW - Recommended)")
        print("2. 🖥️  GUI Interface") 
        print("3. 💻 Command Line Interface")
        print("4. 🎯 Training Mode Only")
        print("5. 🔧 Configuration Setup")
        print("6. 📊 Model Testing")
        print("7. 📧 Email Notification Setup")
        print("8. 🚨 INSTANT Mobile Alerts Setup")
        print("9. 📞 EMERGENCY Phone Calls Setup")
        print("10. 🧪 Test Security Features")
        print("11. ❌ Exit")
        print()
        
        choice = input("Enter your choice (1-11): ").strip()
        
        if choice == '1':
            try:
                from typing_security_app import main as app_main
                print("Starting Desktop App...")
                app_main()
                break
            except ImportError as e:
                print(f"Error starting Desktop App: {e}")
                
        elif choice == '2':
            try:
                from security_gui import main as gui_main
                print("Starting GUI interface...")
                gui_main()
                break
            except ImportError as e:
                print(f"Error starting GUI: {e}")
                print("Make sure all dependencies are installed: pip install -r requirements.txt")
                
        elif choice == '3':
            try:
                from security_system import main as cli_main
                print("Starting command line interface...")
                cli_main()
                break
            except ImportError as e:
                print(f"Error starting CLI: {e}")
                
        elif choice == '4':
            try:
                from keystroke_collector import main as collector_main
                print("Starting training mode...")
                collector_main()
                break
            except ImportError as e:
                print(f"Error starting training mode: {e}")
                
        elif choice == '5':
            try:
                from security_system import SecuritySystem
                security = SecuritySystem()
                print("Configuration created/updated!")
                print("Please edit security_config.json to add your notification settings.")
                break
            except ImportError as e:
                print(f"Error creating configuration: {e}")
                
        elif choice == '6':
            try:
                from typing_model import main as model_main
                print("Starting model testing...")
                model_main()
                break
            except ImportError as e:
                print(f"Error starting model testing: {e}")
                
        elif choice == '7':
            try:
                from notification_system import main as notification_main
                print("Starting notification setup...")
                notification_main()
                break
            except ImportError as e:
                print(f"Error starting notification setup: {e}")
                
        elif choice == '8':
            try:
                from instant_mobile_alerts import main as alerts_main
                print("Starting INSTANT mobile alerts setup...")
                alerts_main()
                break
            except ImportError as e:
                print(f"Error starting mobile alerts setup: {e}")
                
        elif choice == '9':
            try:
                from emergency_call_system import main as emergency_main
                print("Starting EMERGENCY phone call setup...")
                print(f"📱 Your number: +918015339335")
                emergency_main()
                break
            except ImportError as e:
                print(f"Error starting emergency call setup: {e}")
                
        elif choice == '10':
            try:
                from test_security_features import main as test_main
                print("Starting security features testing...")
                print("🧪 Testing alarm system and camera capture...")
                test_main()
                break
            except ImportError as e:
                print(f"Error starting security tests: {e}")
                
        elif choice == '11':
            print("Goodbye! Stay secure! 🔒")
            break
            
        else:
            print("Invalid choice! Please enter 1-11.")
            
        print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSystem interrupted by user. Goodbye! 🔒")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check your installation and try again.")
