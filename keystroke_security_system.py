"""
Keystroke Biometric Security System
- System provides text for user to type during training
- Learns user's unique typing patterns (timing, rhythm)
- Blocks system access until proper authentication
- Activates security alerts after 3 failed attempts
- No security controls visible until authenticated
"""

import tkinter as tk
from tkinter import messagebox
import time
import json
import os
import threading
import subprocess
from datetime import datetime
import hashlib

class KeystrokeSecuritySystem:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Security configuration
        self.user_phone = "8015339335"
        self.firebase_url = "https://security-control-demo-default-rtdb.firebaseio.com"
        
        # Training texts - system provides these
        self.training_texts = [
            "The quick brown fox jumps over the lazy dog",
            "Security is not a product but a process",
            "Biometric authentication using keystroke dynamics",
            "Advanced cybersecurity requires multiple layers",
            "Machine learning enhances security systems"
        ]
        
        # Security state
        self.keystroke_patterns = {}
        self.failed_attempts = 0
        self.max_attempts = 3
        self.is_authenticated = False
        self.current_user = None
        
        # Keystroke timing data
        self.key_timings = []
        self.last_key_time = 0
        
        self.load_patterns()
        self.setup_login_interface()
        
        # Start with system locked
        self.log_event("system_started", "Keystroke security system started - SYSTEM LOCKED")
    
    def setup_window(self):
        """Setup main window as security barrier"""
        self.root.title("🔒 System Security - Authentication Required")
        self.root.geometry("800x600")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(False, False)
        
        # Make window stay on top and capture focus
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Colors for security theme
        self.colors = {
            'bg': '#0a0a0a',
            'panel': '#1a1a1a', 
            'accent': '#ff4444',
            'success': '#44ff44',
            'warning': '#ffaa44',
            'text': '#ffffff',
            'input': '#2a2a2a'
        }
    
    def setup_login_interface(self):
        """Setup the login interface - no security controls visible"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header - Security barrier
        header_frame = tk.Frame(main_frame, bg=self.colors['accent'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔒 SYSTEM ACCESS DENIED", 
                font=("Arial", 24, "bold"), fg='white', bg=self.colors['accent']).pack(pady=25)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.colors['panel'], height=50)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="🚫 AUTHENTICATION REQUIRED TO ACCESS SYSTEM", 
                                    font=("Arial", 14, "bold"), fg=self.colors['accent'], bg=self.colors['panel'])
        self.status_label.pack(pady=15)
        
        # Failed attempts display
        self.attempts_label = tk.Label(status_frame, text=f"Failed Attempts: {self.failed_attempts}/{self.max_attempts}", 
                                      font=("Arial", 12), fg=self.colors['warning'], bg=self.colors['panel'])
        self.attempts_label.pack()
        
        # Authentication section
        auth_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        auth_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        # Check if user exists
        if os.path.exists('keystroke_patterns.json') and self.keystroke_patterns:
            self.show_authentication_interface(auth_frame)
        else:
            self.show_setup_interface(auth_frame)
    
    def show_setup_interface(self, parent):
        """Show initial setup interface"""
        setup_frame = tk.LabelFrame(parent, text="🎓 INITIAL SYSTEM SETUP", 
                                   font=("Arial", 16, "bold"), fg=self.colors['text'], 
                                   bg=self.colors['panel'], bd=2, relief=tk.RAISED)
        setup_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(setup_frame, text="System requires initial biometric training", 
                font=("Arial", 14), fg=self.colors['text'], bg=self.colors['panel']).pack(pady=20)
        
        # Username entry
        tk.Label(setup_frame, text="👤 Create Username:", 
                font=("Arial", 12, "bold"), fg=self.colors['text'], bg=self.colors['panel']).pack(pady=(20, 5))
        
        self.setup_username_entry = tk.Entry(setup_frame, font=("Arial", 14), width=30, 
                                            bg=self.colors['input'], fg=self.colors['text'], 
                                            insertbackground=self.colors['text'])
        self.setup_username_entry.pack(pady=10)
        
        tk.Button(setup_frame, text="🎓 BEGIN BIOMETRIC TRAINING", command=self.start_biometric_training,
                 font=("Arial", 14, "bold"), fg='white', bg=self.colors['success'],
                 padx=30, pady=15).pack(pady=30)
        
        # Instructions
        instructions = """
🎯 BIOMETRIC TRAINING PROCESS:

1. Enter your username above
2. System will provide 5 different texts to type
3. Type each text naturally at your normal speed
4. System learns your unique keystroke patterns
5. After training, only your typing style will grant access

⚠️ Important: Type naturally and consistently
🔒 Your typing rhythm becomes your biometric key
        """
        
        instruction_text = tk.Text(setup_frame, height=10, font=("Arial", 11),
                                  fg=self.colors['text'], bg=self.colors['input'], 
                                  wrap=tk.WORD, bd=0)
        instruction_text.pack(fill=tk.X, padx=20, pady=20)
        instruction_text.insert(tk.END, instructions)
        instruction_text.config(state=tk.DISABLED)
    
    def show_authentication_interface(self, parent):
        """Show authentication interface for existing users"""
        auth_frame = tk.LabelFrame(parent, text="🔐 BIOMETRIC AUTHENTICATION", 
                                  font=("Arial", 16, "bold"), fg=self.colors['text'], 
                                  bg=self.colors['panel'], bd=2, relief=tk.RAISED)
        auth_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # User selection
        users = list(self.keystroke_patterns.keys())
        if users:
            tk.Label(auth_frame, text="👤 Select User:", 
                    font=("Arial", 12, "bold"), fg=self.colors['text'], bg=self.colors['panel']).pack(pady=(20, 5))
            
            self.user_var = tk.StringVar(value=users[0])
            user_menu = tk.OptionMenu(auth_frame, self.user_var, *users)
            user_menu.config(font=("Arial", 12), bg=self.colors['input'], fg=self.colors['text'])
            user_menu.pack(pady=10)
        
        # Authentication text display
        tk.Label(auth_frame, text="📝 Type the following text exactly:", 
                font=("Arial", 12, "bold"), fg=self.colors['text'], bg=self.colors['panel']).pack(pady=(30, 10))
        
        # Random text for authentication
        import random
        self.auth_text = random.choice(self.training_texts)
        
        text_display = tk.Text(auth_frame, height=3, font=("Arial", 14, "bold"),
                              fg=self.colors['accent'], bg=self.colors['input'], 
                              wrap=tk.WORD, bd=2, relief=tk.SUNKEN)
        text_display.pack(fill=tk.X, padx=20, pady=10)
        text_display.insert(tk.END, self.auth_text)
        text_display.config(state=tk.DISABLED)
        
        # Typing area
        tk.Label(auth_frame, text="⌨️ Type here:", 
                font=("Arial", 12, "bold"), fg=self.colors['text'], bg=self.colors['panel']).pack(pady=(20, 5))
        
        self.auth_entry = tk.Text(auth_frame, height=3, font=("Arial", 14),
                                 bg=self.colors['input'], fg=self.colors['text'], 
                                 insertbackground=self.colors['text'], wrap=tk.WORD)
        self.auth_entry.pack(fill=tk.X, padx=20, pady=10)
        self.auth_entry.focus()
        
        # Bind keystroke capture
        self.auth_entry.bind('<KeyPress>', self.capture_keystroke)
        self.auth_entry.bind('<KeyRelease>', self.on_key_release)
        
        tk.Button(auth_frame, text="🔓 AUTHENTICATE", command=self.authenticate_user,
                 font=("Arial", 14, "bold"), fg='white', bg=self.colors['success'],
                 padx=30, pady=15).pack(pady=20)
        
        # Status
        self.auth_status = tk.Label(auth_frame, text="⏳ Waiting for input...", 
                                   font=("Arial", 11), fg=self.colors['warning'], bg=self.colors['panel'])
        self.auth_status.pack(pady=10)
    
    def start_biometric_training(self):
        """Start the biometric training process"""
        username = self.setup_username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        self.current_user = username
        self.show_training_interface()
    
    def show_training_interface(self):
        """Show training interface with system-provided texts"""
        # Clear interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Training interface
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['success'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🎓 BIOMETRIC TRAINING IN PROGRESS", 
                font=("Arial", 20, "bold"), fg='white', bg=self.colors['success']).pack(pady=25)
        
        # Training content
        training_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        training_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.training_index = 0
        self.training_data = []
        
        self.show_training_text(training_frame)
    
    def show_training_text(self, parent):
        """Show current training text"""
        # Clear previous widgets
        for widget in parent.winfo_children():
            widget.destroy()
        
        if self.training_index >= len(self.training_texts):
            self.complete_training()
            return
        
        current_text = self.training_texts[self.training_index]
        
        # Progress
        progress_frame = tk.Frame(parent, bg=self.colors['panel'])
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(progress_frame, text=f"Training Progress: {self.training_index + 1}/{len(self.training_texts)}", 
                font=("Arial", 14, "bold"), fg=self.colors['text'], bg=self.colors['panel']).pack(pady=10)
        
        # Text to type
        text_frame = tk.LabelFrame(parent, text="📝 Type this text exactly:", 
                                  font=("Arial", 14, "bold"), fg=self.colors['text'], 
                                  bg=self.colors['panel'])
        text_frame.pack(fill=tk.X, pady=20)
        
        text_display = tk.Text(text_frame, height=4, font=("Arial", 14, "bold"),
                              fg=self.colors['accent'], bg=self.colors['input'], 
                              wrap=tk.WORD, bd=2, relief=tk.SUNKEN)
        text_display.pack(fill=tk.X, padx=20, pady=15)
        text_display.insert(tk.END, current_text)
        text_display.config(state=tk.DISABLED)
        
        # Typing area
        typing_frame = tk.LabelFrame(parent, text="⌨️ Your typing area:", 
                                    font=("Arial", 14, "bold"), fg=self.colors['text'], 
                                    bg=self.colors['panel'])
        typing_frame.pack(fill=tk.X, pady=20)
        
        self.training_entry = tk.Text(typing_frame, height=4, font=("Arial", 14),
                                     bg=self.colors['input'], fg=self.colors['text'], 
                                     insertbackground=self.colors['text'], wrap=tk.WORD)
        self.training_entry.pack(fill=tk.X, padx=20, pady=15)
        self.training_entry.focus()
        
        # Reset timing data
        self.key_timings = []
        self.last_key_time = 0
        self.training_start_time = time.time()
        
        # Bind keystroke capture
        self.training_entry.bind('<KeyPress>', self.capture_training_keystroke)
        
        # Instructions
        tk.Label(parent, text="💡 Type naturally at your normal speed. Press Enter when finished.", 
                font=("Arial", 12), fg=self.colors['warning'], bg=self.colors['bg']).pack(pady=10)
        
        # Bind Enter to complete current training
        self.training_entry.bind('<Return>', lambda e: self.complete_current_training(current_text))
    
    def capture_training_keystroke(self, event):
        """Capture keystroke timing during training"""
        current_time = time.time()
        
        if self.last_key_time > 0:
            interval = current_time - self.last_key_time
            self.key_timings.append({
                'char': event.char,
                'interval': interval,
                'timestamp': current_time
            })
        
        self.last_key_time = current_time
    
    def capture_keystroke(self, event):
        """Capture keystroke timing during authentication"""
        current_time = time.time()
        
        if self.last_key_time > 0:
            interval = current_time - self.last_key_time
            self.key_timings.append({
                'char': event.char,
                'interval': interval,
                'timestamp': current_time
            })
        
        self.last_key_time = current_time
    
    def on_key_release(self, event):
        """Handle key release during authentication"""
        typed_text = self.auth_entry.get("1.0", tk.END).strip()
        
        # Update status based on typing progress
        if len(typed_text) == 0:
            self.auth_status.config(text="⏳ Start typing...", fg=self.colors['warning'])
        elif typed_text == self.auth_text[:len(typed_text)]:
            progress = len(typed_text) / len(self.auth_text) * 100
            self.auth_status.config(text=f"✅ Typing correctly... {progress:.0f}%", fg=self.colors['success'])
        else:
            self.auth_status.config(text="❌ Text mismatch detected", fg=self.colors['accent'])
    
    def complete_current_training(self, expected_text):
        """Complete current training text"""
        typed_text = self.training_entry.get("1.0", tk.END).strip()
        
        if typed_text == expected_text:
            # Calculate typing metrics
            total_time = time.time() - self.training_start_time
            avg_interval = sum(t['interval'] for t in self.key_timings) / len(self.key_timings) if self.key_timings else 0
            
            training_data = {
                'text': expected_text,
                'total_time': total_time,
                'avg_interval': avg_interval,
                'key_timings': self.key_timings.copy(),
                'char_count': len(expected_text),
                'wpm': (len(expected_text) / 5) / (total_time / 60) if total_time > 0 else 0
            }
            
            self.training_data.append(training_data)
            self.training_index += 1
            
            # Show next training text
            self.show_training_text(self.training_entry.master)
        else:
            messagebox.showerror("Training Error", "Text doesn't match. Please type exactly as shown.")
            self.training_entry.delete("1.0", tk.END)
            self.training_entry.focus()
    
    def complete_training(self):
        """Complete the training process"""
        # Calculate user's biometric profile
        avg_wpm = sum(t['wpm'] for t in self.training_data) / len(self.training_data)
        avg_interval = sum(t['avg_interval'] for t in self.training_data) / len(self.training_data)
        
        # Create user profile
        user_profile = {
            'username': self.current_user,
            'avg_wpm': avg_wpm,
            'avg_interval': avg_interval,
            'training_data': self.training_data,
            'created_at': datetime.now().isoformat(),
            'tolerance': 0.25  # 25% tolerance for authentication
        }
        
        self.keystroke_patterns[self.current_user] = user_profile
        self.save_patterns()
        
        # Show completion message
        messagebox.showinfo("Training Complete", 
                           f"Biometric training completed!\n\n"
                           f"User: {self.current_user}\n"
                           f"Average WPM: {avg_wpm:.1f}\n"
                           f"Typing Profile: Created\n\n"
                           f"System will now require your unique typing pattern for access.")
        
        self.log_event("training_completed", f"Biometric training completed for {self.current_user}")
        
        # Return to authentication interface
        self.setup_login_interface()
    
    def authenticate_user(self):
        """Authenticate user based on keystroke biometrics"""
        if not hasattr(self, 'user_var'):
            messagebox.showerror("Error", "No user selected")
            return
        
        selected_user = self.user_var.get()
        typed_text = self.auth_entry.get("1.0", tk.END).strip()
        
        if typed_text != self.auth_text:
            self.handle_failed_authentication("Text mismatch")
            return
        
        # Analyze keystroke pattern
        if not self.key_timings:
            self.handle_failed_authentication("No keystroke data captured")
            return
        
        user_profile = self.keystroke_patterns[selected_user]
        
        # Calculate current typing metrics
        current_avg_interval = sum(t['interval'] for t in self.key_timings) / len(self.key_timings)
        
        # Compare with stored profile
        stored_avg_interval = user_profile['avg_interval']
        tolerance = user_profile['tolerance']
        
        difference = abs(current_avg_interval - stored_avg_interval) / stored_avg_interval
        
        if difference <= tolerance:
            # Authentication successful
            self.is_authenticated = True
            self.current_user = selected_user
            self.failed_attempts = 0
            
            self.log_event("auth_success", f"User {selected_user} authenticated successfully")
            self.grant_system_access()
        else:
            self.handle_failed_authentication(f"Keystroke pattern mismatch (difference: {difference:.2%})")
    
    def handle_failed_authentication(self, reason):
        """Handle failed authentication attempt"""
        self.failed_attempts += 1
        self.attempts_label.config(text=f"Failed Attempts: {self.failed_attempts}/{self.max_attempts}")
        
        self.log_event("auth_failed", f"Authentication failed: {reason}", "warning")
        
        if self.failed_attempts >= self.max_attempts:
            self.activate_security_breach()
        else:
            messagebox.showerror("Authentication Failed", 
                               f"Access Denied: {reason}\n\n"
                               f"Attempts remaining: {self.max_attempts - self.failed_attempts}")
            
            # Reset for next attempt
            self.auth_entry.delete("1.0", tk.END)
            self.key_timings = []
            self.last_key_time = 0
            self.auth_entry.focus()
    
    def activate_security_breach(self):
        """Activate security breach protocol"""
        self.log_event("security_breach", f"SECURITY BREACH: {self.failed_attempts} failed attempts", "critical")
        
        # Show security breach interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        breach_frame = tk.Frame(self.root, bg=self.colors['accent'])
        breach_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(breach_frame, text="🚨 SECURITY BREACH DETECTED", 
                font=("Arial", 24, "bold"), fg='white', bg=self.colors['accent']).pack(pady=50)
        
        breach_info = f"""
⚠️ UNAUTHORIZED ACCESS ATTEMPT DETECTED

Failed Authentication Attempts: {self.failed_attempts}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Emergency Contact: {self.user_phone}

🔒 SYSTEM LOCKED
📱 Mobile alert sent to {self.user_phone}
📸 Security photo captured
🚨 Authorities notified

EMERGENCY RESPONSE ACTIVATED
        """
        
        tk.Label(breach_frame, text=breach_info, 
                font=("Arial", 14), fg='white', bg=self.colors['accent'], 
                justify=tk.CENTER).pack(pady=30)
        
        # Simulate mobile alert
        self.send_mobile_alert()
        
        # Show mobile response simulation
        self.show_mobile_response()
    
    def send_mobile_alert(self):
        """Send mobile alert (simulated)"""
        self.log_event("mobile_alert", f"Security breach alert sent to {self.user_phone}", "critical")
        
        # In real implementation, this would send to Firebase
        print(f"🚨 MOBILE ALERT SENT TO {self.user_phone}")
        print(f"SECURITY BREACH: {self.failed_attempts} failed login attempts")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    def show_mobile_response(self):
        """Show mobile response simulation"""
        mobile_window = tk.Toplevel(self.root)
        mobile_window.title("📱 Mobile Security Alert")
        mobile_window.geometry("400x500")
        mobile_window.configure(bg=self.colors['accent'])
        mobile_window.attributes('-topmost', True)
        
        tk.Label(mobile_window, text="📱 SECURITY ALERT", 
                font=("Arial", 18, "bold"), fg='white', bg=self.colors['accent']).pack(pady=20)
        
        alert_text = f"""
🚨 CRITICAL SECURITY BREACH

Phone: {self.user_phone}
Time: {datetime.now().strftime('%H:%M:%S')}

UNAUTHORIZED ACCESS DETECTED
{self.failed_attempts} failed login attempts

Intruder photo captured
System automatically locked

EMERGENCY RESPONSE OPTIONS:
        """
        
        tk.Label(mobile_window, text=alert_text, 
                font=("Arial", 12), fg='white', bg=self.colors['accent'], 
                justify=tk.LEFT).pack(pady=20)
        
        tk.Button(mobile_window, text="🔴 SHUTDOWN LAPTOP IMMEDIATELY", 
                 command=self.execute_remote_shutdown,
                 font=("Arial", 12, "bold"), fg='white', bg='darkred',
                 padx=20, pady=15).pack(pady=10)
        
        tk.Button(mobile_window, text="🔒 KEEP SYSTEM LOCKED", 
                 command=mobile_window.destroy,
                 font=("Arial", 12, "bold"), fg='white', bg=self.colors['panel'],
                 padx=20, pady=10).pack(pady=5)
    
    def execute_remote_shutdown(self):
        """Execute remote shutdown command"""
        if messagebox.askyesno("Remote Shutdown", 
                              "Execute emergency shutdown from mobile?\n\nThis will shutdown the laptop immediately!"):
            
            self.log_event("remote_shutdown", "Emergency shutdown executed from mobile", "critical")
            
            # Countdown
            for i in range(10, 0, -1):
                self.status_label.config(text=f"🔴 EMERGENCY SHUTDOWN IN {i} SECONDS")
                self.root.update()
                time.sleep(1)
            
            # Execute shutdown
            try:
                subprocess.run(['shutdown', '/s', '/f', '/t', '0'], shell=True)
            except Exception as e:
                messagebox.showerror("Shutdown Error", f"Failed to shutdown: {e}")
    
    def grant_system_access(self):
        """Grant access to system after successful authentication"""
        # Show success message
        for widget in self.root.winfo_children():
            widget.destroy()
        
        success_frame = tk.Frame(self.root, bg=self.colors['success'])
        success_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(success_frame, text="✅ ACCESS GRANTED", 
                font=("Arial", 28, "bold"), fg='white', bg=self.colors['success']).pack(pady=50)
        
        tk.Label(success_frame, text=f"Welcome back, {self.current_user}!", 
                font=("Arial", 18), fg='white', bg=self.colors['success']).pack(pady=20)
        
        tk.Label(success_frame, text="System unlocked successfully\nBiometric authentication verified", 
                font=("Arial", 14), fg='white', bg=self.colors['success']).pack(pady=30)
        
        # Auto-close after 3 seconds
        self.root.after(3000, self.close_security_system)
    
    def close_security_system(self):
        """Close security system and allow normal system access"""
        self.log_event("system_unlocked", f"System access granted to {self.current_user}")
        self.root.destroy()
    
    def on_closing(self):
        """Handle window closing - prevent unauthorized closing"""
        if not self.is_authenticated:
            messagebox.showwarning("Access Denied", "System is locked. Authentication required to close.")
            return
        
        self.root.destroy()
    
    def load_patterns(self):
        """Load keystroke patterns"""
        try:
            if os.path.exists('keystroke_patterns.json'):
                with open('keystroke_patterns.json', 'r') as f:
                    self.keystroke_patterns = json.load(f)
        except Exception as e:
            self.log_event("load_error", f"Error loading patterns: {e}", "error")
    
    def save_patterns(self):
        """Save keystroke patterns"""
        try:
            with open('keystroke_patterns.json', 'w') as f:
                json.dump(self.keystroke_patterns, f, indent=2)
        except Exception as e:
            self.log_event("save_error", f"Error saving patterns: {e}", "error")
    
    def log_event(self, event_type, message, severity="info"):
        """Log security events"""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {severity.upper()} | {event_type} | {message}\n"
        
        try:
            with open('security_system.log', 'a') as f:
                f.write(log_entry)
        except:
            pass
        
        print(f"🔒 {event_type}: {message}")
    
    def run(self):
        """Run the security system"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🔒 Starting Keystroke Biometric Security System...")
    print("📞 Emergency Contact: 8015339335")
    print("🚫 System access blocked until authentication")
    
    app = KeystrokeSecuritySystem()
    app.run()

if __name__ == "__main__":
    main()
