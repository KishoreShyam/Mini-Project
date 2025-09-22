"""
Mobile Alert Simulator
Simulates mobile app receiving security alerts and sending shutdown commands
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import time
import threading
from datetime import datetime

class MobileAlertSimulator:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Configuration
        self.firebase_url = "https://security-control-demo-default-rtdb.firebaseio.com"
        self.user_phone = "8015339335"
        
        # State
        self.monitoring = False
        self.alerts = []
        
        self.setup_gui()
        self.start_monitoring()
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("📱 Mobile Security Alert Simulator")
        self.root.geometry("500x700")
        self.root.configure(bg='#1a1a2e')
        
        # Colors
        self.colors = {
            'primary': '#16213e',
            'secondary': '#0f3460',
            'accent': '#e94560',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'text': '#ecf0f1',
            'bg': '#1a1a2e'
        }
    
    def setup_gui(self):
        """Setup GUI interface"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📱 Security Alert Center", 
                font=("Arial", 18, "bold"), fg=self.colors['text'], 
                bg=self.colors['primary']).pack(pady=20)
        
        # Phone info
        info_frame = tk.Frame(self.root, bg=self.colors['secondary'])
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(info_frame, text=f"📞 Phone: {self.user_phone}", 
                font=("Arial", 12), fg=self.colors['text'], 
                bg=self.colors['secondary']).pack(pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="🔍 Monitoring for alerts...")
        status_label = tk.Label(self.root, textvariable=self.status_var,
                               font=("Arial", 14, "bold"), fg=self.colors['success'],
                               bg=self.colors['bg'])
        status_label.pack(pady=10)
        
        # Alert display
        alert_frame = tk.LabelFrame(self.root, text="🚨 Security Alerts", 
                                   font=("Arial", 14, "bold"),
                                   fg=self.colors['text'], bg=self.colors['secondary'])
        alert_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Alert list
        self.alert_listbox = tk.Listbox(alert_frame, font=("Arial", 11),
                                       fg=self.colors['text'], bg=self.colors['primary'],
                                       selectbackground=self.colors['accent'])
        self.alert_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Emergency controls
        emergency_frame = tk.LabelFrame(self.root, text="🚨 Emergency Response", 
                                       font=("Arial", 14, "bold"),
                                       fg=self.colors['danger'], bg=self.colors['secondary'])
        emergency_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Emergency buttons
        tk.Button(emergency_frame, text="🔴 EMERGENCY SHUTDOWN LAPTOP", 
                 command=self.emergency_shutdown,
                 font=("Arial", 14, "bold"), fg='white', bg=self.colors['danger'],
                 padx=20, pady=15).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(emergency_frame, text="🔒 LOCK LAPTOP", 
                 command=self.lock_laptop,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['warning'],
                 padx=20, pady=10).pack(fill=tk.X, padx=10, pady=5)
        
        # Test controls
        test_frame = tk.Frame(self.root, bg=self.colors['bg'])
        test_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(test_frame, text="🧪 Send Test Alert", 
                 command=self.send_test_alert,
                 font=("Arial", 11), fg='white', bg=self.colors['primary'],
                 padx=15, pady=8).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(test_frame, text="🔄 Refresh Alerts", 
                 command=self.refresh_alerts,
                 font=("Arial", 11), fg='white', bg=self.colors['primary'],
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(test_frame, text="🗑️ Clear Alerts", 
                 command=self.clear_alerts,
                 font=("Arial", 11), fg='white', bg=self.colors['secondary'],
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
    
    def start_monitoring(self):
        """Start monitoring for alerts"""
        def monitor():
            self.monitoring = True
            while self.monitoring:
                try:
                    self.check_for_alerts()
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def check_for_alerts(self):
        """Check Firebase for new alerts"""
        try:
            response = requests.get(f"{self.firebase_url}/security_alerts.json", timeout=5)
            
            if response.status_code == 200 and response.json():
                alerts = response.json()
                
                for alert_id, alert_data in alerts.items():
                    if isinstance(alert_data, dict):
                        phone = alert_data.get('phone', '')
                        alert_type = alert_data.get('type', '')
                        timestamp = alert_data.get('timestamp', 0)
                        
                        # Check if alert is for this phone and is new
                        if (phone == self.user_phone and 
                            alert_id not in [a['id'] for a in self.alerts]):
                            
                            alert_data['id'] = alert_id
                            self.alerts.append(alert_data)
                            self.display_new_alert(alert_data)
                            
                            # Show critical alert popup
                            if alert_data.get('severity') == 'critical':
                                self.show_critical_alert(alert_data)
        except Exception as e:
            pass  # Silent fail for network issues
    
    def display_new_alert(self, alert_data):
        """Display new alert in the list"""
        timestamp = datetime.fromtimestamp(alert_data.get('timestamp', 0) / 1000)
        alert_text = f"🚨 {timestamp.strftime('%H:%M:%S')} - {alert_data.get('message', 'Security Alert')}"
        
        self.alert_listbox.insert(0, alert_text)
        self.alert_listbox.selection_set(0)
        
        # Update status
        self.status_var.set(f"🚨 NEW ALERT RECEIVED - {len(self.alerts)} total")
        
        # Flash the window
        self.root.bell()
    
    def show_critical_alert(self, alert_data):
        """Show critical alert popup"""
        message = alert_data.get('message', 'Critical Security Alert')
        alert_type = alert_data.get('type', 'unknown')
        
        if alert_type == 'security_breach':
            result = messagebox.askyesno(
                "🚨 CRITICAL SECURITY ALERT",
                f"{message}\n\n"
                f"📞 Phone: {self.user_phone}\n"
                f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"🔴 Do you want to SHUTDOWN the laptop immediately?",
                icon='warning'
            )
            
            if result:
                self.emergency_shutdown()
        else:
            messagebox.showwarning("Security Alert", message)
    
    def emergency_shutdown(self):
        """Send emergency shutdown command"""
        try:
            # Confirm action
            result = messagebox.askyesno(
                "🔴 EMERGENCY SHUTDOWN",
                "⚠️ WARNING: This will immediately shutdown the laptop!\n\n"
                "Are you absolutely sure you want to proceed?",
                icon='warning'
            )
            
            if not result:
                return
            
            # Send shutdown command
            shutdown_data = {
                'command': 'SHUTDOWN',
                'phone': self.user_phone,
                'timestamp': int(time.time() * 1000),
                'status': 'pending',
                'source': 'mobile_emergency'
            }
            
            response = requests.post(f"{self.firebase_url}/emergency_commands.json", 
                                   json=shutdown_data, timeout=10)
            
            if response.status_code == 200:
                messagebox.showinfo("Command Sent", 
                                  "🔴 Emergency shutdown command sent!\n"
                                  "Laptop will shutdown in 10 seconds.")
                
                # Add to alert list
                alert_text = f"🔴 {datetime.now().strftime('%H:%M:%S')} - EMERGENCY SHUTDOWN SENT"
                self.alert_listbox.insert(0, alert_text)
                self.status_var.set("🔴 EMERGENCY SHUTDOWN COMMAND SENT")
            else:
                messagebox.showerror("Error", "Failed to send shutdown command")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")
    
    def lock_laptop(self):
        """Send lock command"""
        try:
            lock_data = {
                'command': 'LOCK',
                'phone': self.user_phone,
                'timestamp': int(time.time() * 1000),
                'status': 'pending',
                'source': 'mobile_lock'
            }
            
            response = requests.post(f"{self.firebase_url}/emergency_commands.json", 
                                   json=lock_data, timeout=10)
            
            if response.status_code == 200:
                messagebox.showinfo("Command Sent", "🔒 Lock command sent to laptop")
                alert_text = f"🔒 {datetime.now().strftime('%H:%M:%S')} - LOCK COMMAND SENT"
                self.alert_listbox.insert(0, alert_text)
            else:
                messagebox.showerror("Error", "Failed to send lock command")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")
    
    def send_test_alert(self):
        """Send test alert"""
        try:
            test_alert = {
                'type': 'test_alert',
                'message': 'Test alert from mobile simulator',
                'timestamp': int(time.time() * 1000),
                'phone': self.user_phone,
                'severity': 'low',
                'source': 'mobile_test'
            }
            
            response = requests.post(f"{self.firebase_url}/security_alerts.json", 
                                   json=test_alert, timeout=10)
            
            if response.status_code == 200:
                messagebox.showinfo("Test Alert", "Test alert sent successfully")
            else:
                messagebox.showerror("Error", "Failed to send test alert")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send test alert: {e}")
    
    def refresh_alerts(self):
        """Refresh alert list"""
        self.check_for_alerts()
        self.status_var.set(f"🔄 Refreshed - {len(self.alerts)} alerts")
    
    def clear_alerts(self):
        """Clear alert list"""
        if messagebox.askyesno("Clear Alerts", "Clear all alerts from the list?"):
            self.alerts.clear()
            self.alert_listbox.delete(0, tk.END)
            self.status_var.set("🔍 Monitoring for alerts...")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("📱 Starting Mobile Alert Simulator...")
    print("🔍 Monitoring for security alerts...")
    print("📞 Phone: 8015339335")
    print("🔥 Firebase: Connected")
    
    app = MobileAlertSimulator()
    app.run()

if __name__ == "__main__":
    main()
