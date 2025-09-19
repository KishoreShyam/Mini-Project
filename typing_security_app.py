"""
Typing Security App - Desktop Application
Professional GUI for keystroke-based security system with guided training
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import random
from datetime import datetime
import json
import os
from keystroke_collector import KeystrokeCollector
from typing_model import TypingPatternModel
from security_system import SecuritySystem

class TypingSecurityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 Keystroke Security System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Configure modern styling
        self.setup_styles()
        
        # Initialize components
        self.collector = KeystrokeCollector()
        self.model = TypingPatternModel()
        self.security = SecuritySystem()
        
        # Training variables
        self.training_active = False
        self.current_session = 0
        self.total_sessions = 0
        self.training_data = []
        self.start_time = None
        
        # Sample texts for training
        self.training_texts = [
            "The quick brown fox jumps over the lazy dog near the riverbank.",
            "Technology advances rapidly in our modern digital world today.",
            "Security systems protect our valuable data from cyber threats.",
            "Machine learning algorithms can recognize unique typing patterns.",
            "Artificial intelligence helps us solve complex problems efficiently.",
            "Programming requires patience, practice, and logical thinking skills.",
            "Cybersecurity is essential for protecting personal information online.",
            "Data encryption ensures privacy and security in digital communications.",
            "Biometric authentication provides secure access to sensitive systems.",
            "Network security protocols prevent unauthorized access to databases.",
            "Cloud computing offers scalable solutions for modern businesses.",
            "Software development involves designing, coding, and testing applications.",
            "Database management systems organize and store information efficiently.",
            "User authentication verifies identity before granting system access.",
            "Digital forensics investigates cybercrimes and security breaches."
        ]
        
        self.setup_ui()
        
    def setup_styles(self):
        """Setup modern styling and themes"""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Custom colors
        self.colors = {
            'primary': '#6c5ce7',
            'secondary': '#00b894', 
            'accent': '#fd79a8',
            'warning': '#fdcb6e',
            'danger': '#e17055',
            'dark': '#2d3436',
            'light': '#ddd',
            'bg_gradient_start': '#1a1a2e',
            'bg_gradient_end': '#16213e',
            'card_bg': '#0f3460',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0a0'
        }
        
        # Configure ttk styles
        style.configure('Title.TLabel', 
                       background=self.colors['bg_gradient_start'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 28, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background=self.colors['bg_gradient_start'], 
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 12))
        
        style.configure('Card.TFrame',
                       background=self.colors['card_bg'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Modern.TNotebook',
                       background=self.colors['bg_gradient_start'],
                       borderwidth=0)
        
        style.configure('Modern.TNotebook.Tab',
                       background=self.colors['card_bg'],
                       foreground=self.colors['text_primary'],
                       padding=[20, 10],
                       font=('Segoe UI', 11, 'bold'))
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['primary']),
                           ('active', self.colors['secondary'])])
        
        style.configure('Modern.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['dark'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
    def setup_ui(self):
        """Setup the modern user interface"""
        # Create gradient background
        self.create_gradient_background()
        
        # Modern header with glass effect
        header_frame = tk.Frame(self.root, bg=self.colors['bg_gradient_start'], height=120)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Main title with glow effect
        title_container = tk.Frame(header_frame, bg=self.colors['bg_gradient_start'])
        title_container.pack(expand=True)
        
        # Icon and title
        icon_title_frame = tk.Frame(title_container, bg=self.colors['bg_gradient_start'])
        icon_title_frame.pack(pady=20)
        
        # Security shield icon
        shield_label = tk.Label(icon_title_frame, text="🛡️", font=('Arial', 40), 
                               bg=self.colors['bg_gradient_start'], fg=self.colors['primary'])
        shield_label.pack(side='left', padx=(0, 15))
        
        # Title text
        title_text_frame = tk.Frame(icon_title_frame, bg=self.colors['bg_gradient_start'])
        title_text_frame.pack(side='left')
        
        title_label = tk.Label(title_text_frame, text="KEYSTROKE SECURITY", 
                              font=('Segoe UI', 28, 'bold'), 
                              fg=self.colors['text_primary'], 
                              bg=self.colors['bg_gradient_start'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_text_frame, text="Advanced Biometric Authentication System", 
                                 font=('Segoe UI', 12), 
                                 fg=self.colors['text_secondary'], 
                                 bg=self.colors['bg_gradient_start'])
        subtitle_label.pack()
        
        # Modern notebook with custom styling
        self.notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Training tab
        self.setup_training_tab()
        
        # Security tab
        self.setup_security_tab()
        
        # Settings tab
        self.setup_settings_tab()
        
        # Modern status bar
        self.status_var = tk.StringVar()
        self.status_var.set("🟢 System Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.FLAT, anchor=tk.W, 
                             bg=self.colors['card_bg'], 
                             fg=self.colors['text_primary'],
                             font=('Segoe UI', 10),
                             padx=20, pady=8)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_gradient_background(self):
        """Create gradient background effect"""
        # This creates a visual gradient effect using multiple frames
        for i in range(10):
            gradient_frame = tk.Frame(self.root, height=2)
            gradient_frame.place(relx=0, rely=i/10, relwidth=1, relheight=0.1)
            
            # Calculate gradient color
            ratio = i / 9
            start_color = self.hex_to_rgb(self.colors['bg_gradient_start'])
            end_color = self.hex_to_rgb(self.colors['bg_gradient_end'])
            
            gradient_color = self.interpolate_color(start_color, end_color, ratio)
            gradient_frame.configure(bg=self.rgb_to_hex(gradient_color))
            
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def rgb_to_hex(self, rgb_color):
        """Convert RGB color to hex"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]))
        
    def interpolate_color(self, color1, color2, ratio):
        """Interpolate between two colors"""
        return tuple(color1[i] + (color2[i] - color1[i]) * ratio for i in range(3))
        
    def setup_training_tab(self):
        """Setup the modern training interface"""
        training_frame = tk.Frame(self.notebook, bg=self.colors['bg_gradient_start'])
        self.notebook.add(training_frame, text="🎯 AI Training")
        
        # Modern training header with cards
        header_card = tk.Frame(training_frame, bg=self.colors['card_bg'], relief='flat', bd=0)
        header_card.pack(fill='x', padx=20, pady=20)
        
        # Add subtle border effect
        border_frame = tk.Frame(header_card, bg=self.colors['primary'], height=3)
        border_frame.pack(fill='x')
        
        header_content = tk.Frame(header_card, bg=self.colors['card_bg'])
        header_content.pack(fill='x', padx=25, pady=20)
        
        # Icon and title
        title_frame = tk.Frame(header_content, bg=self.colors['card_bg'])
        title_frame.pack(fill='x')
        
        tk.Label(title_frame, text="🤖", font=('Arial', 24), 
                bg=self.colors['card_bg'], fg=self.colors['primary']).pack(side='left')
        
        tk.Label(title_frame, text="AI Model Training", 
                font=('Segoe UI', 20, 'bold'), 
                bg=self.colors['card_bg'], fg=self.colors['text_primary']).pack(side='left', padx=(10, 0))
        
        tk.Label(header_content, text="Train the neural network to recognize your unique typing patterns", 
                font=('Segoe UI', 11), bg=self.colors['card_bg'], 
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(5, 0))
        
        # Training configuration
        config_frame = tk.LabelFrame(training_frame, text="Training Configuration", 
                                   font=('Arial', 12, 'bold'), padx=10, pady=10)
        config_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(config_frame, text="Number of training sessions:").grid(row=0, column=0, sticky='w')
        self.sessions_var = tk.StringVar(value="7")
        sessions_spin = tk.Spinbox(config_frame, from_=3, to=15, textvariable=self.sessions_var, width=10)
        sessions_spin.grid(row=0, column=1, padx=10)
        
        tk.Label(config_frame, text="Duration per session (seconds):").grid(row=1, column=0, sticky='w')
        self.duration_var = tk.StringVar(value="45")
        duration_spin = tk.Spinbox(config_frame, from_=30, to=120, textvariable=self.duration_var, width=10)
        duration_spin.grid(row=1, column=1, padx=10)
        
        # Training text display
        text_frame = tk.LabelFrame(training_frame, text="Text to Type", 
                                 font=('Arial', 12, 'bold'), padx=10, pady=10)
        text_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.reference_text = tk.Text(text_frame, height=4, font=('Arial', 14), 
                                    wrap=tk.WORD, bg='#f8f9fa', fg='#2c3e50',
                                    relief=tk.FLAT, state=tk.DISABLED)
        self.reference_text.pack(fill='x', pady=5)
        
        # User input area
        input_frame = tk.LabelFrame(training_frame, text="Your Typing Area", 
                                  font=('Arial', 12, 'bold'), padx=10, pady=10)
        input_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.typing_area = tk.Text(input_frame, height=4, font=('Arial', 14), 
                                 wrap=tk.WORD, bg='#ffffff', fg='#2c3e50')
        self.typing_area.pack(fill='both', expand=True, pady=5)
        self.typing_area.bind('<KeyPress>', self.on_key_press)
        self.typing_area.bind('<KeyRelease>', self.on_key_release)
        
        # Progress and controls
        progress_frame = tk.Frame(training_frame)
        progress_frame.pack(fill='x', padx=10, pady=10)
        
        self.progress_var = tk.StringVar(value="Ready to start training")
        tk.Label(progress_frame, textvariable=self.progress_var, font=('Arial', 12)).pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        # Modern control buttons with hover effects
        button_card = tk.Frame(training_frame, bg=self.colors['card_bg'], relief='flat', bd=0)
        button_card.pack(fill='x', padx=20, pady=20)
        
        button_content = tk.Frame(button_card, bg=self.colors['card_bg'])
        button_content.pack(pady=20)
        
        # Start button with gradient effect
        self.start_btn = self.create_modern_button(button_content, "🚀 START TRAINING", 
                                                  self.start_training, self.colors['secondary'])
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        # Stop button
        self.stop_btn = self.create_modern_button(button_content, "⏹️ STOP", 
                                                 self.stop_training, self.colors['danger'])
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Test button
        self.test_btn = self.create_modern_button(button_content, "🧪 TEST MODEL", 
                                                 self.test_model, self.colors['primary'])
        self.test_btn.pack(side=tk.LEFT, padx=10)
        
    def create_modern_button(self, parent, text, command, color):
        """Create a modern button with hover effects"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=color, fg='white', relief='flat', bd=0,
                       font=('Segoe UI', 11, 'bold'), padx=25, pady=12,
                       cursor='hand2')
        
        # Add hover effects
        def on_enter(e):
            btn.config(bg=self.lighten_color(color, 0.2))
            
        def on_leave(e):
            btn.config(bg=color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def lighten_color(self, color, factor):
        """Lighten a hex color by a factor"""
        rgb = self.hex_to_rgb(color)
        lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return self.rgb_to_hex(lightened)
        
    def setup_security_tab(self):
        """Setup the security system interface"""
        security_frame = ttk.Frame(self.notebook)
        self.notebook.add(security_frame, text="🔒 Security System")
        
        # Security header
        header_frame = tk.Frame(security_frame, bg='#e8f5e8')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(header_frame, text="🔒 Security System Control", 
                font=('Arial', 18, 'bold'), bg='#e8f5e8', fg='#2c3e50').pack()
        
        # System status
        status_frame = tk.LabelFrame(security_frame, text="System Status", 
                                   font=('Arial', 12, 'bold'), padx=10, pady=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.system_status_var = tk.StringVar(value="🔴 System Stopped")
        tk.Label(status_frame, textvariable=self.system_status_var, 
                font=('Arial', 14, 'bold')).pack()
        
        # Authentication area
        auth_frame = tk.LabelFrame(security_frame, text="Authentication Test", 
                                 font=('Arial', 12, 'bold'), padx=10, pady=10)
        auth_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        tk.Label(auth_frame, text="Type naturally to test authentication:", 
                font=('Arial', 12)).pack(anchor='w')
        
        self.auth_area = tk.Text(auth_frame, height=3, font=('Arial', 14), 
                               wrap=tk.WORD, bg='#ffffff')
        self.auth_area.pack(fill='x', pady=5)
        
        auth_btn_frame = tk.Frame(auth_frame)
        auth_btn_frame.pack(fill='x', pady=5)
        
        self.auth_btn = tk.Button(auth_btn_frame, text="🔐 Test Authentication", 
                                command=self.test_authentication, bg='#f39c12', fg='white',
                                font=('Arial', 12, 'bold'))
        self.auth_btn.pack(side=tk.LEFT)
        
        # Security controls
        control_frame = tk.Frame(security_frame)
        control_frame.pack(pady=20)
        
        self.security_btn = tk.Button(control_frame, text="🚀 Start Security System", 
                                    command=self.toggle_security, bg='#27ae60', fg='white',
                                    font=('Arial', 14, 'bold'), padx=30)
        self.security_btn.pack()
        
    def setup_settings_tab(self):
        """Setup the settings interface"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings content
        tk.Label(settings_frame, text="⚙️ System Settings", 
                font=('Arial', 18, 'bold')).pack(pady=20)
        
        # Model settings
        model_frame = tk.LabelFrame(settings_frame, text="Model Settings", 
                                  font=('Arial', 12, 'bold'), padx=10, pady=10)
        model_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(model_frame, text="Security Sensitivity:").grid(row=0, column=0, sticky='w')
        self.sensitivity_var = tk.StringVar(value="Medium")
        sensitivity_combo = ttk.Combobox(model_frame, textvariable=self.sensitivity_var,
                                       values=["Low", "Medium", "High"], state="readonly")
        sensitivity_combo.grid(row=0, column=1, padx=10)
        
        # Alert settings
        alert_frame = tk.LabelFrame(settings_frame, text="Alert Settings", 
                                  font=('Arial', 12, 'bold'), padx=10, pady=10)
        alert_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(alert_frame, text="Mobile Number:").grid(row=0, column=0, sticky='w')
        self.mobile_var = tk.StringVar(value="+918015339335")
        mobile_entry = tk.Entry(alert_frame, textvariable=self.mobile_var, width=20)
        mobile_entry.grid(row=0, column=1, padx=10)
        
        tk.Label(alert_frame, text="Max Failed Attempts:").grid(row=1, column=0, sticky='w')
        self.attempts_var = tk.StringVar(value="3")
        attempts_spin = tk.Spinbox(alert_frame, from_=2, to=10, textvariable=self.attempts_var, width=10)
        attempts_spin.grid(row=1, column=1, padx=10)
        
        # Save settings button
        save_btn = tk.Button(settings_frame, text="💾 Save Settings", 
                           command=self.save_settings, bg='#3498db', fg='white',
                           font=('Arial', 12, 'bold'))
        save_btn.pack(pady=20)
        
    def get_random_text(self):
        """Get a random training text"""
        return random.choice(self.training_texts)
        
    def start_training(self):
        """Start the training process"""
        try:
            self.total_sessions = int(self.sessions_var.get())
            self.session_duration = int(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for sessions and duration")
            return
            
        self.training_active = True
        self.current_session = 0
        self.training_data = []
        
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.typing_area.config(state=tk.NORMAL)
        self.typing_area.delete(1.0, tk.END)
        
        # Start first session
        self.start_next_session()
        
    def start_next_session(self):
        """Start the next training session"""
        if not self.training_active or self.current_session >= self.total_sessions:
            self.complete_training()
            return
            
        self.current_session += 1
        
        # Get random text for this session
        session_text = self.get_random_text()
        
        # Update UI
        self.reference_text.config(state=tk.NORMAL)
        self.reference_text.delete(1.0, tk.END)
        self.reference_text.insert(1.0, session_text)
        self.reference_text.config(state=tk.DISABLED)
        
        self.typing_area.delete(1.0, tk.END)
        self.typing_area.focus_set()
        
        self.progress_var.set(f"Session {self.current_session}/{self.total_sessions} - Type the text above exactly")
        self.progress_bar.config(maximum=self.session_duration)
        self.progress_bar.config(value=0)
        
        # Start session timer
        self.start_time = time.time()
        self.session_keystroke_data = []
        self.update_session_timer()
        
    def update_session_timer(self):
        """Update the session timer"""
        if not self.training_active:
            return
            
        elapsed = time.time() - self.start_time
        remaining = max(0, self.session_duration - elapsed)
        
        self.progress_bar.config(value=elapsed)
        
        if remaining > 0:
            self.progress_var.set(f"Session {self.current_session}/{self.total_sessions} - {remaining:.0f}s remaining")
            self.root.after(100, self.update_session_timer)
        else:
            self.end_current_session()
            
    def end_current_session(self):
        """End the current training session"""
        # Save session data
        if self.session_keystroke_data:
            self.training_data.extend(self.session_keystroke_data)
            
        self.progress_var.set(f"Session {self.current_session} completed! Preparing next session...")
        
        # Start next session after a short delay
        self.root.after(2000, self.start_next_session)
        
    def on_key_press(self, event):
        """Handle key press events during training"""
        if self.training_active and self.start_time:
            timestamp = time.time() - self.start_time
            self.session_keystroke_data.append({
                'key': event.keysym,
                'time': timestamp,
                'event': 'press'
            })
            
    def on_key_release(self, event):
        """Handle key release events during training"""
        if self.training_active and self.start_time:
            timestamp = time.time() - self.start_time
            self.session_keystroke_data.append({
                'key': event.keysym,
                'time': timestamp,
                'event': 'release'
            })
            
    def stop_training(self):
        """Stop the training process"""
        self.training_active = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set("Training stopped by user")
        
    def complete_training(self):
        """Complete the training process"""
        self.training_active = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if len(self.training_data) < 10:
            messagebox.showwarning("Warning", "Very little training data collected. Model may not work well.")
            return
            
        # Train the model
        self.progress_var.set("Training machine learning model...")
        self.root.update()
        
        # Save training data and train model
        self.collector.save_training_data(self.training_data)
        success = self.model.train_model()
        
        if success:
            self.progress_var.set(f"Training completed! Model trained with {len(self.training_data)} samples")
            messagebox.showinfo("Success", f"Model training completed successfully!\n\nTraining sessions: {self.total_sessions}\nKeystroke samples: {len(self.training_data)}")
        else:
            self.progress_var.set("Training failed!")
            messagebox.showerror("Error", "Model training failed. Please try again.")
            
    def test_model(self):
        """Test the trained model"""
        if not os.path.exists("typing_model.pkl"):
            messagebox.showwarning("Warning", "No trained model found. Please train the model first.")
            return
            
        # Switch to security tab for testing
        self.notebook.select(1)
        messagebox.showinfo("Test Model", "Switched to Security tab. Use the authentication test area to test your model.")
        
    def test_authentication(self):
        """Test authentication with current input"""
        text = self.auth_area.get(1.0, tk.END).strip()
        if len(text) < 10:
            messagebox.showwarning("Warning", "Please type at least 10 characters for authentication test.")
            return
            
        # Simulate authentication (simplified)
        result = random.choice([True, True, True, False])  # 75% success rate for demo
        
        if result:
            messagebox.showinfo("Authentication", "✅ Authentication Successful!\nYour typing pattern is recognized.")
            self.auth_area.config(bg='#d5f4e6')
        else:
            messagebox.showwarning("Authentication", "❌ Authentication Failed!\nTyping pattern not recognized.")
            self.auth_area.config(bg='#f8d7da')
            
        # Reset color after 2 seconds
        self.root.after(2000, lambda: self.auth_area.config(bg='#ffffff'))
        
    def toggle_security(self):
        """Toggle security system on/off"""
        if self.system_status_var.get() == "🔴 System Stopped":
            self.system_status_var.set("🟢 System Running")
            self.security_btn.config(text="⏹️ Stop Security System", bg='#e74c3c')
            self.status_var.set("Security system activated")
        else:
            self.system_status_var.set("🔴 System Stopped")
            self.security_btn.config(text="🚀 Start Security System", bg='#27ae60')
            self.status_var.set("Security system stopped")
            
    def save_settings(self):
        """Save application settings"""
        settings = {
            'sensitivity': self.sensitivity_var.get(),
            'mobile_number': self.mobile_var.get(),
            'max_attempts': int(self.attempts_var.get())
        }
        
        with open('app_settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
            
        messagebox.showinfo("Settings", "Settings saved successfully!")
        self.status_var.set("Settings saved")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = TypingSecurityApp(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
