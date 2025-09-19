import time
import numpy as np
from pynput import keyboard
import json
import os
from datetime import datetime

class TypingPatternCollector:
    def __init__(self):
        self.key_times = []
        self.key_intervals = []
        self.key_hold_times = []
        self.current_key_down = {}
        self.is_collecting = False
        self.collected_data = []
        
    def on_key_press(self, key):
        if not self.is_collecting:
            return
            
        current_time = time.time()
        try:
            key_char = key.char if hasattr(key, 'char') and key.char else str(key)
        except AttributeError:
            key_char = str(key)
            
        self.current_key_down[key_char] = current_time
        
        # Calculate interval between keystrokes
        if len(self.key_times) > 0:
            interval = current_time - self.key_times[-1]
            self.key_intervals.append(interval)
            
        self.key_times.append(current_time)
        
    def on_key_release(self, key):
        if not self.is_collecting:
            return
            
        current_time = time.time()
        try:
            key_char = key.char if hasattr(key, 'char') and key.char else str(key)
        except AttributeError:
            key_char = str(key)
            
        if key_char in self.current_key_down:
            hold_time = current_time - self.current_key_down[key_char]
            self.key_hold_times.append(hold_time)
            del self.current_key_down[key_char]
            
        # Stop collection on ESC key
        if key == keyboard.Key.esc:
            self.stop_collection()
            return False
            
    def start_collection(self, duration=30):
        """Start collecting typing patterns for specified duration (seconds)"""
        print(f"Starting typing pattern collection for {duration} seconds...")
        print("Type naturally. Press ESC to stop early.")
        
        self.key_times = []
        self.key_intervals = []
        self.key_hold_times = []
        self.current_key_down = {}
        self.is_collecting = True
        
        # Start keyboard listener
        listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        listener.start()
        
        # Wait for duration or ESC key
        start_time = time.time()
        while self.is_collecting and (time.time() - start_time) < duration:
            time.sleep(0.1)
            
        self.stop_collection()
        listener.stop()
        
    def stop_collection(self):
        """Stop collecting typing patterns"""
        self.is_collecting = False
        print("Collection stopped.")
        
    def get_features(self):
        """Extract statistical features from collected typing data"""
        if len(self.key_intervals) == 0 or len(self.key_hold_times) == 0:
            return None
            
        features = {
            # Keystroke interval statistics
            'interval_mean': np.mean(self.key_intervals),
            'interval_std': np.std(self.key_intervals),
            'interval_median': np.median(self.key_intervals),
            'interval_min': np.min(self.key_intervals),
            'interval_max': np.max(self.key_intervals),
            
            # Key hold time statistics
            'hold_mean': np.mean(self.key_hold_times),
            'hold_std': np.std(self.key_hold_times),
            'hold_median': np.median(self.key_hold_times),
            'hold_min': np.min(self.key_hold_times),
            'hold_max': np.max(self.key_hold_times),
            
            # Typing speed
            'typing_speed': len(self.key_times) / (self.key_times[-1] - self.key_times[0]) if len(self.key_times) > 1 else 0,
            
            # Additional rhythm features
            'interval_variance': np.var(self.key_intervals),
            'hold_variance': np.var(self.key_hold_times),
            
            'timestamp': datetime.now().isoformat()
        }
        
        return features
        
    def save_training_data(self, filename='typing_patterns.json'):
        """Save collected features for training"""
        features = self.get_features()
        if features is None:
            print("No data collected to save.")
            return False
            
        # Load existing data or create new
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            data = {'training_sessions': []}
            
        data['training_sessions'].append(features)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Training data saved to {filename}")
        return True
        
    def collect_multiple_sessions(self, num_sessions=5, session_duration=30):
        """Collect multiple training sessions"""
        print(f"Collecting {num_sessions} training sessions...")
        
        for i in range(num_sessions):
            print(f"\nSession {i+1}/{num_sessions}")
            input("Press Enter when ready to start typing...")
            self.start_collection(session_duration)
            self.save_training_data()
            
            if i < num_sessions - 1:
                print("Take a short break before the next session.")
                time.sleep(2)
                
        print("All training sessions completed!")

if __name__ == "__main__":
    collector = TypingPatternCollector()
    
    print("Typing Pattern Security System - Training Mode")
    print("=" * 50)
    
    choice = input("Choose option:\n1. Single session (30s)\n2. Multiple sessions (5x30s)\nEnter choice (1/2): ")
    
    if choice == "1":
        collector.start_collection(30)
        collector.save_training_data()
    elif choice == "2":
        collector.collect_multiple_sessions()
    else:
        print("Invalid choice.")
