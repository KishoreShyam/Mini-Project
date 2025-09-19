import time
import threading
from pynput import keyboard
import numpy as np
from collections import defaultdict
import json
import os

class KeystrokeCollector:
    def __init__(self):
        self.keystroke_data = []
        self.current_session = []
        self.start_time = None
        self.last_key_time = None
        self.is_collecting = False
        self.key_press_times = {}
        self.dwell_times = []  # Time key is held down
        self.flight_times = []  # Time between key releases and next key press
        
    def on_key_press(self, key):
        if not self.is_collecting:
            return
            
        current_time = time.time()
        
        try:
            key_char = key.char if hasattr(key, 'char') and key.char else str(key)
        except AttributeError:
            key_char = str(key)
            
        # Record key press time
        self.key_press_times[key_char] = current_time
        
        # Calculate flight time (time between previous key release and current key press)
        if self.last_key_time is not None:
            flight_time = current_time - self.last_key_time
            self.flight_times.append(flight_time)
            
        if self.start_time is None:
            self.start_time = current_time
            
    def on_key_release(self, key):
        if not self.is_collecting:
            return
            
        current_time = time.time()
        
        try:
            key_char = key.char if hasattr(key, 'char') and key.char else str(key)
        except AttributeError:
            key_char = str(key)
            
        # Calculate dwell time (how long key was held)
        if key_char in self.key_press_times:
            dwell_time = current_time - self.key_press_times[key_char]
            self.dwell_times.append(dwell_time)
            del self.key_press_times[key_char]
            
        self.last_key_time = current_time
        
        # Stop collection on ESC key
        if key == keyboard.Key.esc:
            self.stop_collection()
            return False
            
    def start_collection(self, duration=None):
        """Start collecting keystroke data"""
        self.is_collecting = True
        self.keystroke_data = []
        self.current_session = []
        self.dwell_times = []
        self.flight_times = []
        self.start_time = None
        self.last_key_time = None
        
        print("Starting keystroke collection... Press ESC to stop or wait for duration to complete.")
        
        # Start keyboard listener
        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.listener.start()
        
        # If duration is specified, stop after that time
        if duration:
            threading.Timer(duration, self.stop_collection).start()
            
    def stop_collection(self):
        """Stop collecting keystroke data"""
        self.is_collecting = False
        if hasattr(self, 'listener'):
            self.listener.stop()
        print("Keystroke collection stopped.")
        
    def get_typing_features(self):
        """Extract typing pattern features"""
        if not self.dwell_times or not self.flight_times:
            return None
            
        features = {
            'avg_dwell_time': np.mean(self.dwell_times),
            'std_dwell_time': np.std(self.dwell_times),
            'avg_flight_time': np.mean(self.flight_times),
            'std_flight_time': np.std(self.flight_times),
            'typing_speed': len(self.dwell_times) / (time.time() - self.start_time) if self.start_time else 0,
            'rhythm_consistency': 1 / (1 + np.std(self.flight_times)) if self.flight_times else 0,
            'pressure_pattern': np.mean(self.dwell_times) / np.mean(self.flight_times) if self.flight_times else 0
        }
        
        return features
        
    def save_training_data(self, filename="training_data.json"):
        """Save collected data for training"""
        features = self.get_typing_features()
        if features is None:
            print("No data to save!")
            return False
            
        # Load existing data if file exists
        training_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    training_data = json.load(f)
            except:
                training_data = []
                
        # Add new session data
        session_data = {
            'timestamp': time.time(),
            'features': features,
            'raw_dwell_times': self.dwell_times,
            'raw_flight_times': self.flight_times
        }
        
        training_data.append(session_data)
        
        # Save updated data
        with open(filename, 'w') as f:
            json.dump(training_data, f, indent=2)
            
        print(f"Training data saved to {filename}")
        return True
        
    def collect_training_session(self, session_duration=30):
        """Collect a single training session"""
        print(f"Please type naturally for {session_duration} seconds...")
        print("You can type anything - sentences, passwords, or random text.")
        print("Focus on typing at your normal speed and rhythm.")
        
        self.start_collection(duration=session_duration)
        
        # Wait for collection to complete
        time.sleep(session_duration + 1)
        
        return self.save_training_data()

if __name__ == "__main__":
    collector = KeystrokeCollector()
    
    print("Keystroke Pattern Collector")
    print("=" * 30)
    
    while True:
        print("\n1. Collect training session (30 seconds)")
        print("2. Collect custom duration session")
        print("3. View current features")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            collector.collect_training_session()
        elif choice == '2':
            try:
                duration = int(input("Enter duration in seconds: "))
                collector.collect_training_session(duration)
            except ValueError:
                print("Invalid duration!")
        elif choice == '3':
            collector.start_collection()
            input("Press Enter to stop and view features...")
            collector.stop_collection()
            features = collector.get_typing_features()
            if features:
                print("\nCurrent Typing Features:")
                for key, value in features.items():
                    print(f"{key}: {value:.4f}")
        elif choice == '4':
            break
        else:
            print("Invalid choice!")
