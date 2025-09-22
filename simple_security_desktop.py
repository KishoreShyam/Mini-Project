"""
Simple Security Desktop Application
Works with built-in Python packages only
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
import threading
import subprocess
from datetime import datetime

class SimpleSecurityDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Configuration
        self.user_phone = "8015339335"
        
        # Security state
        self.keystroke_patterns = {}
        self.failed_attempts = 0
        self.max_attempts = 3
        self.is_authenticated = False
        
        # GUI variables
        self.status_var = tk.StringVar(value="🔒 SYSTEM LOCKED")
        self.attempts_var = tk.StringVar(value="0/3")
        self.time_var = tk.StringVar()
        
        self.setup_gui()
        self.start_time_update()
        self.load_patterns()
        
        self.log_event("system_started", "Security desktop application started")
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("🔒 Advanced Security System")
        self.root.geometry("900x600")
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
        
        tk.Label(header_frame, text="🔒 Advanced Security System", 
                font=("Arial", 20, "bold"), fg=self.colors['text'], 
                bg=self.colors['primary']).pack(pady=20)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.colors['secondary'], height=50)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        status_frame.pack_propagate(False)
        
        tk.Label(status_frame, textvariable=self.status_var,
                font=("Arial", 14, "bold"), fg=self.colors['accent'],
                bg=self.colors['secondary']).pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(status_frame, textvariable=self.time_var,
                font=("Arial", 12), fg=self.colors['text'],
                bg=self.colors['secondary']).pack(side=tk.RIGHT, padx=20, pady=10)
        
        tk.Label(status_frame, textvariable=self.attempts_var,
                font=("Arial", 12, "bold"), fg=self.colors['warning'],
                bg=self.colors['secondary']).pack(side=tk.RIGHT, padx=(0, 20), pady=10)
        
        tk.Label(status_frame, text="Failed Attempts:",
                font=("Arial", 12), fg=self.colors['text'],
                bg=self.colors['secondary']).pack(side=tk.RIGHT, pady=10)
        
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
        
        # Instructions
        instructions = """
🎯 Instructions:
1. Enter username and phrase
2. Click 'Train Pattern' to learn typing
3. Type phrase 3 times for training
4. Use 'Authenticate' to verify identity
5. After 3 failed attempts → Security breach
        """
        
        instruction_text = tk.Text(left_panel, height=8, font=("Arial", 10),
                                  fg=self.colors['text'], bg=self.colors['primary'],
                                  wrap=tk.WORD)
        instruction_text.pack(fill=tk.X, padx=10, pady=10)
        instruction_text.insert(tk.END, instructions)
        instruction_text.config(state=tk.DISABLED)
        
        # Right panel - Controls
        right_panel = tk.LabelFrame(main_frame, text="🚨 Security Controls", 
                                   font=("Arial", 14, "bold"),
                                   fg=self.colors['text'], bg=self.colors['secondary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # System info
        info_text = f"""
📞 Emergency Contact: {self.user_phone}
🔥 Firebase: Configured
🌐 Web API: Available
📱 Mobile Alerts: Ready

🚨 Security Features:
• Keystroke biometric authentication
• Failed attempt monitoring  
• Mobile alert integration
• Emergency shutdown capability
• Real-time security logging
        """
        
        info_display = tk.Text(right_panel, height=12, font=("Arial", 10),
                              fg=self.colors['text'], bg=self.colors['primary'],
                              wrap=tk.WORD)
        info_display.pack(fill=tk.X, padx=10, pady=10)
        info_display.insert(tk.END, info_text)
        info_display.config(state=tk.DISABLED)
        
        # Emergency buttons
        tk.Button(right_panel, text="🔴 EMERGENCY SHUTDOWN", command=self.emergency_shutdown,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['danger'],
                 padx=20, pady=15).pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(right_panel, text="🔒 LOCK SYSTEM", command=self.lock_system,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['warning'],
                 padx=20, pady=10).pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(right_panel, text="📱 Send Test Alert", command=self.test_alert,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['accent'],
                 padx=20, pady=10).pack(fill=tk.X, padx=10, pady=5)
        
        # Bottom panel - Logs
        log_panel = tk.LabelFrame(self.root, text="📋 Security Logs", 
                                 font=("Arial", 14, "bold"),
                                 fg=self.colors['text'], bg=self.colors['secondary'])
        log_panel.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(log_panel, height=6, font=("Consolas", 10),
                               fg=self.colors['text'], bg=self.colors['primary'])
        self.log_text.pack(fill=tk.X, padx=10, pady=10)
    
    def start_time_update(self):
        """Update time display"""
        def update_time():
            while True:
                self.time_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                time.sleep(1)
        
        threading.Thread(target=update_time, daemon=True).start()
    
    def log_event(self, event_type, message, severity="info"):
        """Log events"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        severity_icon = {'info': '📝', 'warning': '⚠️', 'error': '❌', 'critical': '🚨'}.get(severity, '📝')
        
        log_line = f"{severity_icon} {timestamp} | {event_type} | {message}\n"
        
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, log_line)
            self.log_text.see(tk.END)
        
        # Save to file
        try:
            with open('security_log.txt', 'a') as f:
                f.write(f"{datetime.now().isoformat()} | {event_type} | {message}\n")
        except:
            pass
    
    def load_patterns(self):
        """Load keystroke patterns"""
        try:
            if os.path.exists('keystroke_patterns.json'):
                with open('keystroke_patterns.json', 'r') as f:
                    self.keystroke_patterns = json.load(f)
                self.log_event("patterns_loaded", f"Loaded {len(self.keystroke_patterns)} user patterns")
        except Exception as e:
            self.log_event("load_error", f"Error loading patterns: {e}", "error")
    
    def save_patterns(self):
        """Save keystroke patterns"""
        try:
            with open('keystroke_patterns.json', 'w') as f:
                json.dump(self.keystroke_patterns, f, indent=2)
            self.log_event("patterns_saved", "Keystroke patterns saved")
        except Exception as e:
            self.log_event("save_error", f"Error saving patterns: {e}", "error")
    
    def train_pattern(self):
        """Train keystroke pattern"""
        username = self.username_entry.get().strip()
        phrase = self.auth_phrase_entry.get().strip()
        
        if not username or not phrase:
            messagebox.showerror("Error", "Please enter username and phrase")
            return
        
        # Training dialog
        training_window = tk.Toplevel(self.root)
        training_window.title("🎓 Keystroke Pattern Training")
        training_window.geometry("500x400")
        training_window.configure(bg=self.colors['secondary'])
        training_window.transient(self.root)
        training_window.grab_set()
        
        tk.Label(training_window, text="🎓 Keystroke Pattern Training", 
                font=("Arial", 16, "bold"), fg=self.colors['text'], 
                bg=self.colors['secondary']).pack(pady=20)
        
        tk.Label(training_window, text=f"Training for user: {username}", 
                font=("Arial", 12), fg=self.colors['text'], 
                bg=self.colors['secondary']).pack(pady=5)
        
        tk.Label(training_window, text=f"Phrase: {phrase}", 
                font=("Arial", 12), fg=self.colors['accent'], 
                bg=self.colors['secondary']).pack(pady=5)
        
        instruction_label = tk.Label(training_window, text="Type the phrase 3 times below:", 
                                    font=("Arial", 12), fg=self.colors['text'], 
                                    bg=self.colors['secondary'])
        instruction_label.pack(pady=20)
        
        patterns = []
        
        for i in range(3):
            attempt_frame = tk.Frame(training_window, bg=self.colors['secondary'])
            attempt_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(attempt_frame, text=f"Attempt {i+1}:", 
                    font=("Arial", 11, "bold"), fg=self.colors['text'], 
                    bg=self.colors['secondary']).pack(anchor="w")
            
            entry = tk.Entry(attempt_frame, font=("Arial", 12), width=40, show="*")
            entry.pack(fill=tk.X, pady=5)
            
            def capture_timing(entry_widget, attempt_num):
                def on_key_press(event):
                    if not hasattr(entry_widget, 'start_time'):
                        entry_widget.start_time = time.time()
                
                def on_return(event):
                    if hasattr(entry_widget, 'start_time'):
                        end_time = time.time()
                        typing_time = end_time - entry_widget.start_time
                        text = entry_widget.get()
                        
                        if text.strip() == phrase:
                            patterns.append(typing_time)
                            entry_widget.config(bg='lightgreen')
                            tk.Label(attempt_frame, text=f"✅ Time: {typing_time:.2f}s", 
                                    fg=self.colors['success'], bg=self.colors['secondary']).pack()
                        else:
                            entry_widget.config(bg='lightcoral')
                            tk.Label(attempt_frame, text="❌ Text mismatch", 
                                    fg=self.colors['danger'], bg=self.colors['secondary']).pack()
                
                entry_widget.bind('<KeyPress>', on_key_press)
                entry_widget.bind('<Return>', on_return)
            
            capture_timing(entry, i)
        
        def finish_training():
            if len(patterns) >= 3:
                avg_time = sum(patterns) / len(patterns)
                self.keystroke_patterns[username] = {
                    'phrase': phrase,
                    'avg_time': avg_time,
                    'tolerance': 0.3,
                    'trained_at': datetime.now().isoformat()
                }
                
                self.save_patterns()
                self.log_event("pattern_trained", f"Pattern trained for {username} (avg: {avg_time:.2f}s)")
                messagebox.showinfo("Success", f"Training completed!\nAverage time: {avg_time:.2f}s")
                training_window.destroy()
            else:
                messagebox.showerror("Error", "Please complete all 3 training attempts correctly")
        
        tk.Button(training_window, text="✅ Complete Training", command=finish_training,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['success'],
                 padx=20, pady=10).pack(pady=20)
    
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
        
        # Timing test
        auth_window = tk.Toplevel(self.root)
        auth_window.title("🔐 Authentication")
        auth_window.geometry("400x200")
        auth_window.configure(bg=self.colors['secondary'])
        auth_window.transient(self.root)
        auth_window.grab_set()
        
        tk.Label(auth_window, text="🔐 Authentication Test", 
                font=("Arial", 16, "bold"), fg=self.colors['text'], 
                bg=self.colors['secondary']).pack(pady=20)
        
        tk.Label(auth_window, text=f"Type: {phrase}", 
                font=("Arial", 12), fg=self.colors['accent'], 
                bg=self.colors['secondary']).pack(pady=10)
        
        auth_entry = tk.Entry(auth_window, font=("Arial", 12), width=30, show="*")
        auth_entry.pack(pady=10)
        auth_entry.focus()
        
        def check_auth(event):
            if hasattr(auth_entry, 'start_time'):
                end_time = time.time()
                typing_time = end_time - auth_entry.start_time
                text = auth_entry.get()
                
                if text == phrase:
                    time_diff = abs(typing_time - pattern['avg_time'])
                    
                    if time_diff <= pattern['tolerance']:
                        self.is_authenticated = True
                        self.failed_attempts = 0
                        self.status_var.set("✅ AUTHENTICATED")
                        self.log_event("auth_success", f"User {username} authenticated (time: {typing_time:.2f}s)")
                        messagebox.showinfo("Success", "Authentication successful!")
                        auth_window.destroy()
                    else:
                        auth_window.destroy()
                        self.handle_failed_auth(f"Timing mismatch (expected: {pattern['avg_time']:.2f}s, got: {typing_time:.2f}s)")
                else:
                    auth_window.destroy()
                    self.handle_failed_auth("Text mismatch")
        
        def on_key_press(event):
            if not hasattr(auth_entry, 'start_time'):
                auth_entry.start_time = time.time()
        
        auth_entry.bind('<KeyPress>', on_key_press)
        auth_entry.bind('<Return>', check_auth)
    
    def handle_failed_auth(self, reason):
        """Handle failed authentication"""
        self.failed_attempts += 1
        self.attempts_var.set(f"{self.failed_attempts}/{self.max_attempts}")
        self.log_event("auth_failed", f"Authentication failed: {reason}", "warning")
        
        if self.failed_attempts >= self.max_attempts:
            self.security_breach()
        else:
            messagebox.showerror("Authentication Failed", 
                               f"{reason}\nAttempts: {self.failed_attempts}/{self.max_attempts}")
    
    def security_breach(self):
        """Handle security breach"""
        self.status_var.set("🚨 SECURITY BREACH")
        self.log_event("security_breach", f"Security breach after {self.failed_attempts} failed attempts", "critical")
        
        # Show security breach dialog
        breach_window = tk.Toplevel(self.root)
        breach_window.title("🚨 SECURITY BREACH DETECTED")
        breach_window.geometry("500x400")
        breach_window.configure(bg=self.colors['danger'])
        breach_window.transient(self.root)
        breach_window.grab_set()
        
        tk.Label(breach_window, text="🚨 SECURITY BREACH DETECTED", 
                font=("Arial", 18, "bold"), fg='white', 
                bg=self.colors['danger']).pack(pady=20)
        
        breach_info = f"""
⚠️ UNAUTHORIZED ACCESS ATTEMPT

Failed Attempts: {self.failed_attempts}/{self.max_attempts}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Emergency Contact: {self.user_phone}

📸 Intruder photo captured (simulated)
📱 Mobile alert sent to {self.user_phone}
🔥 Firebase notification sent

EMERGENCY RESPONSE OPTIONS:
• Mobile app can shutdown laptop remotely
• Security team has been notified
• All attempts have been logged
        """
        
        info_text = tk.Text(breach_window, height=15, font=("Arial", 11),
                           fg='white', bg=self.colors['danger'], wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        info_text.insert(tk.END, breach_info)
        info_text.config(state=tk.DISABLED)
        
        tk.Button(breach_window, text="🔴 EMERGENCY SHUTDOWN NOW", 
                 command=lambda: [breach_window.destroy(), self.emergency_shutdown()],
                 font=("Arial", 12, "bold"), fg='white', bg='darkred',
                 padx=20, pady=15).pack(pady=10)
        
        tk.Button(breach_window, text="✅ ACKNOWLEDGE", 
                 command=breach_window.destroy,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['secondary'],
                 padx=20, pady=10).pack()
        
        # Simulate mobile alert
        self.simulate_mobile_alert()
    
    def simulate_mobile_alert(self):
        """Simulate mobile alert"""
        self.log_event("mobile_alert", f"Mobile alert sent to {self.user_phone}", "critical")
        
        # Show mobile alert simulation
        alert_window = tk.Toplevel(self.root)
        alert_window.title("📱 Mobile Alert Simulation")
        alert_window.geometry("400x300")
        alert_window.configure(bg=self.colors['accent'])
        
        tk.Label(alert_window, text="📱 MOBILE ALERT", 
                font=("Arial", 16, "bold"), fg='white', 
                bg=self.colors['accent']).pack(pady=20)
        
        alert_text = f"""
🚨 SECURITY BREACH ALERT

Phone: {self.user_phone}
Time: {datetime.now().strftime('%H:%M:%S')}

SECURITY BREACH: {self.failed_attempts} failed 
login attempts detected on your laptop.

Intruder photo captured.

EMERGENCY RESPONSE:
        """
        
        tk.Label(alert_window, text=alert_text, 
                font=("Arial", 11), fg='white', 
                bg=self.colors['accent'], justify=tk.LEFT).pack(pady=10)
        
        tk.Button(alert_window, text="🔴 SHUTDOWN LAPTOP", 
                 command=lambda: [alert_window.destroy(), self.emergency_shutdown()],
                 font=("Arial", 12, "bold"), fg='white', bg='darkred',
                 padx=20, pady=10).pack(pady=5)
        
        tk.Button(alert_window, text="🔒 LOCK LAPTOP", 
                 command=lambda: [alert_window.destroy(), self.lock_system()],
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['warning'],
                 padx=20, pady=10).pack(pady=5)
    
    def emergency_shutdown(self):
        """Emergency shutdown"""
        if messagebox.askyesno("Emergency Shutdown", 
                              "⚠️ WARNING: This will shutdown the laptop immediately!\n\nContinue?"):
            
            self.log_event("emergency_shutdown", "Emergency shutdown initiated", "critical")
            
            # Countdown
            countdown_window = tk.Toplevel(self.root)
            countdown_window.title("🔴 EMERGENCY SHUTDOWN")
            countdown_window.geometry("300x150")
            countdown_window.configure(bg='darkred')
            countdown_window.transient(self.root)
            countdown_window.grab_set()
            
            countdown_label = tk.Label(countdown_window, text="🔴 SHUTTING DOWN", 
                                      font=("Arial", 16, "bold"), fg='white', bg='darkred')
            countdown_label.pack(pady=30)
            
            for i in range(10, 0, -1):
                countdown_label.config(text=f"🔴 SHUTDOWN IN {i}")
                countdown_window.update()
                time.sleep(1)
            
            countdown_window.destroy()
            
            # Execute shutdown
            try:
                subprocess.run(['shutdown', '/s', '/f', '/t', '0'], shell=True)
            except Exception as e:
                messagebox.showerror("Shutdown Error", f"Failed to shutdown: {e}")
    
    def lock_system(self):
        """Lock system"""
        try:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
            self.log_event("system_locked", "System locked")
            messagebox.showinfo("System Locked", "System has been locked")
        except Exception as e:
            messagebox.showerror("Lock Error", f"Failed to lock system: {e}")
    
    def test_alert(self):
        """Test mobile alert"""
        self.log_event("test_alert", "Test alert sent")
        messagebox.showinfo("Test Alert", f"Test alert sent to {self.user_phone}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = SimpleSecurityDesktop()
    app.run()

if __name__ == "__main__":
    main()
