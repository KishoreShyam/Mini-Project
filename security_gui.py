import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
import json
import os
from security_system import SecuritySystem

class SecuritySystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keystroke Security System")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Initialize security system
        self.security_system = SecuritySystem()
        self.is_running = False
        self.auth_thread = None
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.create_widgets()
        self.update_status()
        
    def configure_styles(self):
        """Configure custom styles for the GUI"""
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'),
                           background='#2c3e50',
                           foreground='#ecf0f1')
        
        self.style.configure('Status.TLabel',
                           font=('Arial', 12),
                           background='#2c3e50',
                           foreground='#e74c3c')
        
        self.style.configure('Success.TLabel',
                           font=('Arial', 12),
                           background='#2c3e50',
                           foreground='#27ae60')
        
        self.style.configure('Custom.TButton',
                           font=('Arial', 10, 'bold'))
        
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=20)
        
        title_label = ttk.Label(title_frame, 
                               text="🔒 Keystroke Security System", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#34495e', relief='raised', bd=2)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(status_frame, text="System Status:", 
                 font=('Arial', 12, 'bold'),
                 background='#34495e',
                 foreground='#ecf0f1').pack(pady=5)
        
        self.status_label = ttk.Label(status_frame, 
                                     text="🔒 LOCKED", 
                                     style='Status.TLabel')
        self.status_label.pack(pady=5)
        
        self.attempts_label = ttk.Label(status_frame,
                                       text="Failed Attempts: 0/3",
                                       font=('Arial', 10),
                                       background='#34495e',
                                       foreground='#ecf0f1')
        self.attempts_label.pack(pady=2)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=20)
        
        # First row of buttons
        button_frame1 = tk.Frame(control_frame, bg='#2c3e50')
        button_frame1.pack(pady=5)
        
        self.setup_btn = ttk.Button(button_frame1, 
                                   text="🎯 Setup User Profile",
                                   command=self.setup_profile,
                                   style='Custom.TButton',
                                   width=20)
        self.setup_btn.pack(side='left', padx=5)
        
        self.start_btn = ttk.Button(button_frame1,
                                   text="🚀 Start Security System",
                                   command=self.start_security,
                                   style='Custom.TButton',
                                   width=20)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(button_frame1,
                                  text="⏹️ Stop System",
                                  command=self.stop_security,
                                  style='Custom.TButton',
                                  width=20,
                                  state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Second row of buttons
        button_frame2 = tk.Frame(control_frame, bg='#2c3e50')
        button_frame2.pack(pady=5)
        
        self.test_btn = ttk.Button(button_frame2,
                                  text="🧪 Test Authentication",
                                  command=self.test_auth,
                                  style='Custom.TButton',
                                  width=20)
        self.test_btn.pack(side='left', padx=5)
        
        self.alerts_btn = ttk.Button(button_frame2,
                                    text="📱 View Alerts",
                                    command=self.view_alerts,
                                    style='Custom.TButton',
                                    width=20)
        self.alerts_btn.pack(side='left', padx=5)
        
        self.config_btn = ttk.Button(button_frame2,
                                    text="⚙️ Settings",
                                    command=self.open_settings,
                                    style='Custom.TButton',
                                    width=20)
        self.config_btn.pack(side='left', padx=5)
        
        # Log display
        log_frame = tk.Frame(self.root, bg='#2c3e50')
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        ttk.Label(log_frame, text="System Log:",
                 font=('Arial', 12, 'bold'),
                 background='#2c3e50',
                 foreground='#ecf0f1').pack(anchor='w')
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 height=15,
                                                 bg='#1a1a1a',
                                                 fg='#00ff00',
                                                 font=('Consolas', 9),
                                                 wrap='word')
        self.log_text.pack(fill='both', expand=True, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=5)
        
        self.log("Security System GUI initialized")
        
    def log(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert('end', log_message)
        self.log_text.see('end')
        self.root.update_idletasks()
        
    def setup_profile(self):
        """Setup user profile in a separate thread"""
        def setup_thread():
            self.log("Starting user profile setup...")
            self.progress.start()
            
            try:
                # Disable buttons during setup
                self.setup_btn.config(state='disabled')
                
                # Show setup dialog
                setup_window = tk.Toplevel(self.root)
                setup_window.title("User Profile Setup")
                setup_window.geometry("500x400")
                setup_window.configure(bg='#2c3e50')
                setup_window.transient(self.root)
                setup_window.grab_set()
                
                ttk.Label(setup_window, 
                         text="User Profile Setup",
                         font=('Arial', 14, 'bold'),
                         background='#2c3e50',
                         foreground='#ecf0f1').pack(pady=20)
                
                info_text = scrolledtext.ScrolledText(setup_window,
                                                     height=15,
                                                     bg='#34495e',
                                                     fg='#ecf0f1',
                                                     font=('Arial', 10))
                info_text.pack(fill='both', expand=True, padx=20, pady=10)
                
                info_text.insert('end', "Setting up your typing profile...\n\n")
                info_text.insert('end', "You will need to complete 5 training sessions.\n")
                info_text.insert('end', "Each session lasts 30 seconds.\n\n")
                info_text.insert('end', "Please type naturally during each session.\n")
                info_text.insert('end', "You can type anything - sentences, passwords, etc.\n\n")
                info_text.insert('end', "Click 'Start Training' when ready.\n")
                
                def start_training():
                    info_text.delete('1.0', 'end')
                    
                    for i in range(5):
                        info_text.insert('end', f"\nTraining Session {i+1}/5\n")
                        info_text.insert('end', "Please type naturally for 30 seconds...\n")
                        info_text.insert('end', "Press ESC to stop early if needed.\n\n")
                        info_text.see('end')
                        setup_window.update()
                        
                        # Start keystroke collection
                        if not self.security_system.keystroke_collector.collect_training_session(30):
                            info_text.insert('end', "Training session failed!\n")
                            return
                            
                        info_text.insert('end', f"Session {i+1} completed!\n")
                        
                        if i < 4:
                            info_text.insert('end', "Take a short break...\n")
                            time.sleep(2)
                    
                    info_text.insert('end', "\nTraining the model...\n")
                    info_text.see('end')
                    setup_window.update()
                    
                    if self.security_system.typing_model.train_model():
                        self.security_system.typing_model.save_model()
                        info_text.insert('end', "✅ Profile setup completed successfully!\n")
                        self.log("User profile setup completed successfully!")
                    else:
                        info_text.insert('end', "❌ Failed to train the model!\n")
                        self.log("Failed to train the model!")
                    
                    setup_window.after(3000, setup_window.destroy)
                
                ttk.Button(setup_window,
                          text="Start Training",
                          command=start_training,
                          style='Custom.TButton').pack(pady=10)
                
            except Exception as e:
                self.log(f"Error during profile setup: {e}")
                messagebox.showerror("Error", f"Profile setup failed: {e}")
            finally:
                self.progress.stop()
                self.setup_btn.config(state='normal')
        
        threading.Thread(target=setup_thread, daemon=True).start()
        
    def start_security(self):
        """Start the security system"""
        if not self.security_system.typing_model.load_model():
            messagebox.showerror("Error", "No trained model found! Please setup user profile first.")
            return
            
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.log("Security system started")
        
        def security_loop():
            while self.is_running:
                try:
                    if self.security_system.is_locked:
                        self.log(f"System locked - Failed attempts: {self.security_system.failed_attempts}/{self.security_system.max_attempts}")
                        
                        if self.security_system.failed_attempts >= self.security_system.max_attempts:
                            self.log("🚨 SECURITY BREACH DETECTED!")
                            self.handle_breach()
                            continue
                        
                        # Attempt authentication
                        self.log("Waiting for authentication...")
                        if self.security_system.authenticate_user():
                            self.log("✅ Authentication successful! System unlocked.")
                            self.security_system.is_locked = False
                        else:
                            self.log("❌ Authentication failed!")
                    else:
                        self.log("System is unlocked. Press any key to lock again...")
                        time.sleep(5)  # Simulate system usage
                        self.security_system.is_locked = True
                        self.log("System locked again.")
                        
                    time.sleep(1)
                    
                except Exception as e:
                    self.log(f"Error in security loop: {e}")
                    
        self.auth_thread = threading.Thread(target=security_loop, daemon=True)
        self.auth_thread.start()
        
    def stop_security(self):
        """Stop the security system"""
        self.is_running = False
        self.security_system.stop_alarm()
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        self.log("Security system stopped")
        
    def handle_breach(self):
        """Handle security breach"""
        self.log("📸 Capturing intruder photo...")
        photo_path = self.security_system.capture_intruder_photo()
        
        self.log("🚨 Activating alarm...")
        alarm_thread = threading.Thread(target=self.security_system.activate_alarm, args=(15,), daemon=True)
        alarm_thread.start()
        
        self.log("📱 Sending alert notification...")
        self.security_system.send_alert_notification(photo_path)
        
        self.log("System locked for 5 minutes due to security breach!")
        time.sleep(300)  # 5 minutes lockout
        
        self.security_system.failed_attempts = 0
        self.log("Lockout period ended. System ready for authentication.")
        
    def test_auth(self):
        """Test authentication"""
        if not self.security_system.typing_model.load_model():
            messagebox.showerror("Error", "No trained model found! Please setup user profile first.")
            return
            
        def test_thread():
            self.log("Starting authentication test...")
            result = self.security_system.authenticate_user()
            self.log(f"Test result: {'PASSED' if result else 'FAILED'}")
            
        threading.Thread(target=test_thread, daemon=True).start()
        
    def view_alerts(self):
        """View security alerts"""
        alerts_window = tk.Toplevel(self.root)
        alerts_window.title("Security Alerts")
        alerts_window.geometry("600x400")
        alerts_window.configure(bg='#2c3e50')
        
        ttk.Label(alerts_window,
                 text="Security Alerts",
                 font=('Arial', 14, 'bold'),
                 background='#2c3e50',
                 foreground='#ecf0f1').pack(pady=10)
        
        alerts_text = scrolledtext.ScrolledText(alerts_window,
                                               bg='#34495e',
                                               fg='#ecf0f1',
                                               font=('Arial', 10))
        alerts_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        alerts_file = "security_alerts.json"
        if os.path.exists(alerts_file):
            try:
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)
                
                if alerts:
                    alerts_text.insert('end', f"Found {len(alerts)} security alerts:\n\n")
                    for i, alert in enumerate(alerts[-10:], 1):  # Show last 10 alerts
                        alerts_text.insert('end', f"{i}. {alert['timestamp']}\n")
                        alerts_text.insert('end', f"   {alert['message']}\n")
                        if alert.get('photo_path'):
                            alerts_text.insert('end', f"   Photo: {alert['photo_path']}\n")
                        alerts_text.insert('end', "\n")
                else:
                    alerts_text.insert('end', "No security alerts found.")
            except Exception as e:
                alerts_text.insert('end', f"Error reading alerts: {e}")
        else:
            alerts_text.insert('end', "No security alerts file found.")
            
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#2c3e50')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        ttk.Label(settings_window,
                 text="Security Settings",
                 font=('Arial', 14, 'bold'),
                 background='#2c3e50',
                 foreground='#ecf0f1').pack(pady=20)
        
        # Max attempts setting
        attempts_frame = tk.Frame(settings_window, bg='#2c3e50')
        attempts_frame.pack(pady=10)
        
        ttk.Label(attempts_frame,
                 text="Max Failed Attempts:",
                 background='#2c3e50',
                 foreground='#ecf0f1').pack(side='left')
        
        attempts_var = tk.StringVar(value=str(self.security_system.max_attempts))
        attempts_entry = ttk.Entry(attempts_frame, textvariable=attempts_var, width=10)
        attempts_entry.pack(side='left', padx=10)
        
        # Phone number setting
        phone_frame = tk.Frame(settings_window, bg='#2c3e50')
        phone_frame.pack(pady=10)
        
        ttk.Label(phone_frame,
                 text="Phone Number:",
                 background='#2c3e50',
                 foreground='#ecf0f1').pack(side='left')
        
        phone_var = tk.StringVar(value=self.security_system.user_phone or "")
        phone_entry = ttk.Entry(phone_frame, textvariable=phone_var, width=20)
        phone_entry.pack(side='left', padx=10)
        
        def save_settings():
            try:
                self.security_system.max_attempts = int(attempts_var.get())
                self.security_system.user_phone = phone_var.get()
                
                config = {
                    'user_phone': self.security_system.user_phone,
                    'max_attempts': self.security_system.max_attempts,
                    'notification_service': 'email'
                }
                
                with open(self.security_system.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                messagebox.showinfo("Success", "Settings saved successfully!")
                settings_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Invalid max attempts value!")
        
        ttk.Button(settings_window,
                  text="Save Settings",
                  command=save_settings,
                  style='Custom.TButton').pack(pady=20)
        
    def update_status(self):
        """Update status display"""
        if hasattr(self.security_system, 'is_locked'):
            if self.security_system.is_locked:
                self.status_label.config(text="🔒 LOCKED", style='Status.TLabel')
            else:
                self.status_label.config(text="🔓 UNLOCKED", style='Success.TLabel')
                
            self.attempts_label.config(
                text=f"Failed Attempts: {self.security_system.failed_attempts}/{self.security_system.max_attempts}"
            )
        
        # Schedule next update
        self.root.after(1000, self.update_status)

def main():
    root = tk.Tk()
    app = SecuritySystemGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_running:
            app.stop_security()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
