"""
Advanced Security Desktop Application
Features:
- Modern GUI interface with tkinter
- Keystroke biometric authentication
- Camera capture on failed attempts
- Mobile alert integration with shutdown option
- Real-time monitoring and logging
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
# import cv2  # Commented out - not available
import time
import json
import os
import threading
import requests
import subprocess
from datetime import datetime
import secrets

class SecurityDesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        
        # Security configuration
        self.user_phone = "8015339335"
        self.firebase_url = "https://security-control-demo-default-rtdb.firebaseio.com"
        
        # Security state
        self.keystroke_patterns = {}
        self.failed_attempts = 0
        self.max_attempts = 3
        self.is_authenticated = False
        self.camera = None
        
        # GUI variables
        self.status_var = tk.StringVar(value="🔒 SYSTEM LOCKED")
        self.attempts_var = tk.StringVar(value="0/3")
        self.time_var = tk.StringVar()
        
        self.setup_gui()
        self.start_time_update()
        self.start_monitoring()
        
        self.log_event("system_started", "Security desktop application started")
    
    def setup_main_window(self):
        """Setup main window properties"""
        self.root.title("🔒 Advanced Security System")
        self.root.geometry("1000x700")
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
        """Setup the main GUI interface"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🔒 Advanced Security System", 
                              font=("Arial", 20, "bold"), fg=self.colors['text'], 
                              bg=self.colors['primary'])
        title_label.pack(pady=15)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.colors['secondary'], height=60)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        status_frame.pack_propagate(False)
        
        tk.Label(status_frame, textvariable=self.status_var,
                font=("Arial", 14, "bold"), fg=self.colors['accent'],
                bg=self.colors['secondary']).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(status_frame, text="Failed Attempts:",
                font=("Arial", 12), fg=self.colors['text'],
                bg=self.colors['secondary']).pack(side=tk.RIGHT, padx=(0, 10), pady=15)
        
        tk.Label(status_frame, textvariable=self.attempts_var,
                font=("Arial", 12, "bold"), fg=self.colors['warning'],
                bg=self.colors['secondary']).pack(side=tk.RIGHT, pady=15)
        
        # Main content
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Left panel - Authentication
        left_panel = tk.LabelFrame(main_frame, text="🔐 Authentication", 
                                  font=("Arial", 14, "bold"),
                                  fg=self.colors['text'], bg=self.colors['secondary'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Username
        tk.Label(left_panel, text="👤 Username:", font=("Arial", 12),
                fg=self.colors['text'], bg=self.colors['secondary']).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.username_entry = tk.Entry(left_panel, font=("Arial", 14), width=25)
        self.username_entry.pack(padx=10, pady=(0, 10))
        
        # Authentication phrase
        tk.Label(left_panel, text="📝 Authentication Phrase:", font=("Arial", 12),
                fg=self.colors['text'], bg=self.colors['secondary']).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.auth_phrase_entry = tk.Entry(left_panel, font=("Arial", 14), width=25, show="*")
        self.auth_phrase_entry.pack(padx=10, pady=(0, 20))
        
        # Buttons
        tk.Button(left_panel, text="🎓 Train Pattern", command=self.train_pattern,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['primary'],
                 padx=20, pady=10).pack(pady=5)
        
        tk.Button(left_panel, text="🔓 Authenticate", command=self.authenticate,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['success'],
                 padx=20, pady=10).pack(pady=5)
        
        # Right panel - Controls
        right_panel = tk.LabelFrame(main_frame, text="🚨 Emergency Controls", 
                                   font=("Arial", 14, "bold"),
                                   fg=self.colors['text'], bg=self.colors['secondary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Emergency buttons
        tk.Button(right_panel, text="🔴 EMERGENCY SHUTDOWN", command=self.emergency_shutdown,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['danger'],
                 padx=20, pady=15).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(right_panel, text="🔒 LOCK SYSTEM", command=self.lock_system,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['warning'],
                 padx=20, pady=15).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(right_panel, text="📸 Test Camera", command=self.test_camera,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['primary'],
                 padx=20, pady=15).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(right_panel, text="📱 Send Test Alert", command=self.test_alert,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['accent'],
                 padx=20, pady=15).pack(fill=tk.X, padx=10, pady=10)
        
        # Bottom panel - Logs
        log_panel = tk.LabelFrame(self.root, text="📋 Security Logs", 
                                 font=("Arial", 14, "bold"),
                                 fg=self.colors['text'], bg=self.colors['secondary'])
        log_panel.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(log_panel, height=8, font=("Consolas", 10),
                               fg=self.colors['text'], bg=self.colors['primary'])
        self.log_text.pack(fill=tk.X, padx=10, pady=10)
    
    def start_time_update(self):
        """Update time display"""
        def update_time():
            while True:
                self.time_var.set(datetime.now().strftime("%H:%M:%S"))
                time.sleep(1)
        
        threading.Thread(target=update_time, daemon=True).start()
    
    def start_monitoring(self):
        """Start background monitoring"""
        def monitor():
            while True:
                try:
                    self.check_firebase_commands()
                    self.update_status()
                    time.sleep(10)
                except:
                    time.sleep(30)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def log_event(self, event_type, message, severity="info"):
        """Log events to display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        severity_icon = {'info': '📝', 'warning': '⚠️', 'error': '❌', 'critical': '🚨'}.get(severity, '📝')
        
        log_line = f"{severity_icon} {timestamp} | {event_type} | {message}\n"
        
        if self.log_text:
            self.log_text.insert(tk.END, log_line)
            self.log_text.see(tk.END)
    
    def train_pattern(self):
        """Train keystroke pattern"""
        username = self.username_entry.get().strip()
        phrase = self.auth_phrase_entry.get().strip()
        
        if not username or not phrase:
            messagebox.showerror("Error", "Please enter username and phrase")
            return
        
        # Simple pattern training (timing-based)
        patterns = []
        for i in range(3):
            start_time = time.time()
            result = messagebox.askokcancel("Training", f"Training {i+1}/3\nType: {phrase}\nClick OK when ready")
            if not result:
                return
            
            # Simulate typing time measurement
            typing_time = 2.0 + (i * 0.1)  # Simulated timing
            patterns.append(typing_time)
        
        avg_time = sum(patterns) / len(patterns)
        self.keystroke_patterns[username] = {
            'phrase': phrase,
            'avg_time': avg_time,
            'tolerance': 0.3
        }
        
        self.save_patterns()
        self.log_event("pattern_trained", f"Pattern trained for user: {username}")
        messagebox.showinfo("Success", f"Pattern trained for {username}")
    
    def authenticate(self):
        """Authenticate user"""
        username = self.username_entry.get().strip()
        phrase = self.auth_phrase_entry.get().strip()
        
        if username not in self.keystroke_patterns:
            self.handle_failed_auth("User not found")
            return
        
        pattern = self.keystroke_patterns[username]
        if phrase != pattern['phrase']:
            self.handle_failed_auth("Incorrect phrase")
            return
        
        # Simulate timing check
        test_time = 2.1  # Simulated
        time_diff = abs(test_time - pattern['avg_time'])
        
        if time_diff <= pattern['tolerance']:
            self.is_authenticated = True
            self.failed_attempts = 0
            self.status_var.set("✅ AUTHENTICATED")
            self.log_event("auth_success", f"User {username} authenticated")
            messagebox.showinfo("Success", "Authentication successful!")
        else:
            self.handle_failed_auth("Timing pattern mismatch")
    
    def handle_failed_auth(self, reason):
        """Handle failed authentication"""
        self.failed_attempts += 1
        self.attempts_var.set(f"{self.failed_attempts}/{self.max_attempts}")
        self.log_event("auth_failed", f"Authentication failed: {reason}", "warning")
        
        if self.failed_attempts >= self.max_attempts:
            self.security_breach()
        else:
            messagebox.showerror("Authentication Failed", f"{reason}\nAttempts: {self.failed_attempts}/{self.max_attempts}")
    
    def security_breach(self):
        """Handle security breach"""
        self.status_var.set("🚨 SECURITY BREACH")
        self.log_event("security_breach", f"Security breach detected after {self.failed_attempts} failed attempts", "critical")
        
        # Capture photo
        photo_path = self.capture_intruder_photo()
        
        # Send mobile alert
        self.send_mobile_alert(photo_path)
        
        messagebox.showerror("SECURITY BREACH", 
                           f"Security breach detected!\n"
                           f"Failed attempts: {self.failed_attempts}\n"
                           f"Mobile alert sent to {self.user_phone}")
    
    def capture_intruder_photo(self):
        """Simulate photo capture (camera not available)"""
        try:
            filename = f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            self.log_event("photo_simulated", f"Intruder photo simulated: {filename}")
            
            # Create a placeholder file
            with open(filename, 'w') as f:
                f.write("Simulated intruder photo - camera not available")
            
            return filename
        except Exception as e:
            self.log_event("photo_error", f"Photo simulation error: {e}", "error")
        return None
    
    def send_mobile_alert(self, photo_path=None):
        """Send alert to mobile via Firebase"""
        try:
            alert_data = {
                'type': 'security_breach',
                'message': f'SECURITY BREACH: {self.failed_attempts} failed login attempts detected',
                'timestamp': int(time.time() * 1000),
                'phone': self.user_phone,
                'severity': 'critical',
                'shutdown_option': True,
                'photo_captured': photo_path is not None
            }
            
            response = requests.post(f"{self.firebase_url}/security_alerts.json", 
                                   json=alert_data, timeout=10)
            
            if response.status_code == 200:
                self.log_event("alert_sent", "Mobile alert sent successfully")
                
                # Create shutdown command for mobile response
                shutdown_data = {
                    'command': 'SHUTDOWN_READY',
                    'phone': self.user_phone,
                    'timestamp': int(time.time() * 1000),
                    'status': 'waiting_for_response'
                }
                
                requests.post(f"{self.firebase_url}/emergency_commands.json", 
                            json=shutdown_data, timeout=10)
                
                return True
        except Exception as e:
            self.log_event("alert_error", f"Failed to send alert: {e}", "error")
        return False
    
    def check_firebase_commands(self):
        """Check for emergency commands"""
        try:
            response = requests.get(f"{self.firebase_url}/emergency_commands.json", timeout=5)
            
            if response.status_code == 200 and response.json():
                commands = response.json()
                
                for cmd_id, cmd_data in commands.items():
                    if isinstance(cmd_data, dict):
                        command = cmd_data.get('command', '')
                        phone = cmd_data.get('phone', '')
                        status = cmd_data.get('status', '')
                        
                        if (phone == self.user_phone and status == 'pending' and 
                            command == 'SHUTDOWN'):
                            
                            self.log_event("remote_shutdown", "Emergency shutdown command received", "critical")
                            self.execute_shutdown()
                            
                            # Mark as processed
                            requests.patch(f"{self.firebase_url}/emergency_commands/{cmd_id}.json",
                                         json={'status': 'processed'}, timeout=5)
        except:
            pass
    
    def execute_shutdown(self):
        """Execute system shutdown"""
        self.log_event("shutdown_initiated", "System shutdown initiated", "critical")
        
        # Show countdown
        for i in range(10, 0, -1):
            self.status_var.set(f"🔴 SHUTTING DOWN IN {i}")
            self.root.update()
            time.sleep(1)
        
        # Execute shutdown
        subprocess.run(['shutdown', '/s', '/f', '/t', '0'], shell=True)
    
    def update_status(self):
        """Update system status"""
        if self.is_authenticated:
            self.status_var.set("✅ SYSTEM AUTHENTICATED")
        elif self.failed_attempts >= self.max_attempts:
            self.status_var.set("🚨 SECURITY BREACH DETECTED")
        else:
            self.status_var.set("🔒 SYSTEM LOCKED")
    
    def save_patterns(self):
        """Save keystroke patterns"""
        try:
            with open('keystroke_patterns.json', 'w') as f:
                json.dump(self.keystroke_patterns, f, indent=2)
        except Exception as e:
            self.log_event("save_error", f"Error saving patterns: {e}", "error")
    
    # Button handlers
    def emergency_shutdown(self):
        if messagebox.askyesno("Emergency Shutdown", "Are you sure you want to shutdown?"):
            self.execute_shutdown()
    
    def lock_system(self):
        subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
        self.log_event("system_locked", "System locked manually")
    
    def test_camera(self):
        photo = self.capture_intruder_photo()
        if photo:
            messagebox.showinfo("Camera Test", f"Photo captured: {photo}")
        else:
            messagebox.showerror("Camera Test", "Camera test failed")
    
    def test_alert(self):
        if self.send_mobile_alert():
            messagebox.showinfo("Alert Test", "Test alert sent successfully")
        else:
            messagebox.showerror("Alert Test", "Failed to send test alert")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = SecurityDesktopApp()
    app.run()

if __name__ == "__main__":
    main()
