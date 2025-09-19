"""
Mobile App Simulator for Remote Control
Simulates the mobile app that sends remote commands to the laptop
"""

import json
import requests
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class MobileAppSimulator:
    def __init__(self):
        self.config_file = "mobile_config.json"
        self.load_config()
        self.setup_ui()
        
    def load_config(self):
        """Load mobile app configuration"""
        default_config = {
            "user_id": "main_user",
            "backend_url": "http://localhost:8080/api",
            "device_targets": [
                {
                    "device_id": "laptop_main",
                    "device_name": "Main Laptop",
                    "last_seen": ""
                }
            ]
        }
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = default_config
            self.save_config()
            
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def setup_ui(self):
        """Setup mobile app simulator UI"""
        self.root = tk.Tk()
        self.root.title("🔒 Security Mobile App Simulator")
        self.root.geometry("400x600")
        self.root.configure(bg='#1a1a2e')
        
        # Header
        header_frame = tk.Frame(self.root, bg='#16213e', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🔒 Security Control", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#16213e')
        title_label.pack(pady=20)
        
        # Status Section
        status_frame = tk.LabelFrame(self.root, text="📊 System Status", 
                                   font=('Arial', 12, 'bold'),
                                   fg='white', bg='#1a1a2e')
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = tk.Label(status_frame, text="🔍 Checking connection...", 
                                   font=('Arial', 10), fg='#a0a0a0', bg='#1a1a2e')
        self.status_label.pack(pady=10)
        
        # Device Selection
        device_frame = tk.LabelFrame(self.root, text="💻 Target Device", 
                                   font=('Arial', 12, 'bold'),
                                   fg='white', bg='#1a1a2e')
        device_frame.pack(fill='x', padx=20, pady=10)
        
        self.device_var = tk.StringVar(value="Main Laptop")
        device_combo = ttk.Combobox(device_frame, textvariable=self.device_var,
                                  values=["Main Laptop", "Secondary Device"])
        device_combo.pack(pady=10, padx=10, fill='x')
        
        # Emergency Controls
        emergency_frame = tk.LabelFrame(self.root, text="🚨 Emergency Controls", 
                                      font=('Arial', 12, 'bold'),
                                      fg='white', bg='#1a1a2e')
        emergency_frame.pack(fill='x', padx=20, pady=10)
        
        # Shutdown Button
        shutdown_btn = tk.Button(emergency_frame, text="🔴 EMERGENCY SHUTDOWN", 
                               font=('Arial', 14, 'bold'),
                               fg='white', bg='#e74c3c',
                               command=self.emergency_shutdown,
                               height=2)
        shutdown_btn.pack(pady=10, padx=10, fill='x')
        
        # Lock Button
        lock_btn = tk.Button(emergency_frame, text="🔒 LOCK SYSTEM", 
                           font=('Arial', 12, 'bold'),
                           fg='white', bg='#f39c12',
                           command=self.lock_system,
                           height=2)
        lock_btn.pack(pady=5, padx=10, fill='x')
        
        # Alert Controls
        alert_frame = tk.LabelFrame(self.root, text="📱 Alert Controls", 
                                  font=('Arial', 12, 'bold'),
                                  fg='white', bg='#1a1a2e')
        alert_frame.pack(fill='x', padx=20, pady=10)
        
        # Status Request
        status_btn = tk.Button(alert_frame, text="📊 GET STATUS", 
                             font=('Arial', 10, 'bold'),
                             fg='white', bg='#3498db',
                             command=self.get_device_status)
        status_btn.pack(pady=5, padx=10, fill='x')
        
        # Test Alert
        test_alert_btn = tk.Button(alert_frame, text="🧪 SEND TEST ALERT", 
                                 font=('Arial', 10, 'bold'),
                                 fg='white', bg='#9b59b6',
                                 command=self.send_test_alert)
        test_alert_btn.pack(pady=5, padx=10, fill='x')
        
        # Log Section
        log_frame = tk.LabelFrame(self.root, text="📋 Activity Log", 
                                font=('Arial', 12, 'bold'),
                                fg='white', bg='#1a1a2e')
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, font=('Courier', 9),
                              bg='#2c3e50', fg='#ecf0f1', 
                              insertbackground='white')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Start status checking
        self.start_status_monitoring()
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Keep only last 50 lines
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 50:
            self.log_text.delete("1.0", f"{len(lines)-50}.0")
            
    def start_status_monitoring(self):
        """Start monitoring device status"""
        def monitor():
            while True:
                try:
                    # Check if laptop is responding
                    response = requests.get(f"{self.config['backend_url']}/keystroke/stats", timeout=5)
                    if response.status_code == 200:
                        self.status_label.config(text="✅ Laptop Connected", fg='#2ecc71')
                    else:
                        self.status_label.config(text="⚠️ Connection Issues", fg='#f39c12')
                except:
                    self.status_label.config(text="❌ Laptop Offline", fg='#e74c3c')
                    
                time.sleep(10)  # Check every 10 seconds
                
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
    def send_remote_command(self, command, data=None):
        """Send remote command to laptop"""
        try:
            command_data = {
                "command": command,
                "source": "mobile_app",
                "command_id": f"cmd_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "data": data or {}
            }
            
            # In a real app, this would go through FCM
            # For simulation, we'll send directly to our web server
            response = requests.post(
                f"{self.config['backend_url']}/remote/command",
                json=command_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_message(f"✅ Command '{command}' sent successfully")
                return True
            else:
                self.log_message(f"❌ Command '{command}' failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Command error: {str(e)}")
            return False
            
    def emergency_shutdown(self):
        """Execute emergency shutdown"""
        # Confirmation dialog
        result = messagebox.askyesno(
            "🚨 EMERGENCY SHUTDOWN", 
            "Are you sure you want to SHUTDOWN the laptop?\n\n"
            "This will immediately shut down the system!\n\n"
            "Click YES to confirm shutdown.",
            icon='warning'
        )
        
        if result:
            self.log_message("🚨 EMERGENCY SHUTDOWN INITIATED")
            success = self.send_remote_command("shutdown", {
                "force": True,
                "delay": 10,
                "reason": "Emergency shutdown from mobile app"
            })
            
            if success:
                messagebox.showinfo("✅ Shutdown Sent", 
                                  "Emergency shutdown command sent!\n"
                                  "The laptop will shut down in 10 seconds.")
            else:
                messagebox.showerror("❌ Failed", 
                                   "Failed to send shutdown command.\n"
                                   "Check connection and try again.")
                                   
    def lock_system(self):
        """Lock the laptop system"""
        self.log_message("🔒 LOCK COMMAND SENT")
        success = self.send_remote_command("lock", {
            "reason": "Remote lock from mobile app"
        })
        
        if success:
            messagebox.showinfo("✅ Lock Sent", "System lock command sent successfully!")
        else:
            messagebox.showerror("❌ Failed", "Failed to send lock command.")
            
    def get_device_status(self):
        """Get device status"""
        self.log_message("📊 Requesting device status...")
        success = self.send_remote_command("status", {})
        
        if not success:
            messagebox.showerror("❌ Failed", "Failed to get device status.")
            
    def send_test_alert(self):
        """Send test alert"""
        self.log_message("🧪 Sending test alert...")
        success = self.send_remote_command("alert", {
            "alert_message": "This is a test alert from the mobile app",
            "priority": "normal"
        })
        
        if success:
            messagebox.showinfo("✅ Alert Sent", "Test alert sent successfully!")
        else:
            messagebox.showerror("❌ Failed", "Failed to send test alert.")
            
    def run(self):
        """Run the mobile app simulator"""
        self.log_message("📱 Mobile Security App Started")
        self.log_message("🔍 Monitoring laptop connection...")
        self.root.mainloop()

def main():
    """Run the mobile app simulator"""
    print("📱 Starting Mobile App Simulator...")
    app = MobileAppSimulator()
    app.run()

if __name__ == "__main__":
    main()
