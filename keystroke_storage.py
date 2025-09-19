"""
Persistent Keystroke Data Storage System
Saves and loads typing patterns for long-term authentication
"""

import json
import os
import pickle
import numpy as np
from datetime import datetime
import hashlib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

class KeystrokeStorage:
    def __init__(self, user_id="default_user"):
        self.user_id = user_id
        self.data_dir = "keystroke_data"
        self.user_dir = os.path.join(self.data_dir, user_id)
        self.profile_file = os.path.join(self.user_dir, "profile.json")
        self.keystroke_file = os.path.join(self.user_dir, "keystrokes.json")
        self.model_file = os.path.join(self.user_dir, "typing_model.pkl")
        self.scaler_file = os.path.join(self.user_dir, "scaler.pkl")
        
        self.ensure_directories()
        self.load_profile()
        
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.user_dir, exist_ok=True)
        
    def load_profile(self):
        """Load user profile or create new one"""
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                self.profile = json.load(f)
        else:
            self.profile = {
                "user_id": self.user_id,
                "created_date": datetime.now().isoformat(),
                "last_training": None,
                "training_sessions": 0,
                "total_keystrokes": 0,
                "model_accuracy": 0.0,
                "is_trained": False,
                "typing_statistics": {
                    "avg_typing_speed": 0.0,
                    "avg_dwell_time": 0.0,
                    "avg_flight_time": 0.0,
                    "common_patterns": []
                }
            }
            self.save_profile()
            
    def save_profile(self):
        """Save user profile to file"""
        with open(self.profile_file, 'w') as f:
            json.dump(self.profile, f, indent=2)
            
    def save_keystroke_session(self, session_data):
        """Save a complete keystroke training session"""
        # Load existing sessions
        sessions = self.load_all_sessions()
        
        # Add new session
        session_entry = {
            "session_id": len(sessions) + 1,
            "timestamp": datetime.now().isoformat(),
            "text_typed": session_data.get("text", ""),
            "keystrokes": session_data.get("keystrokes", []),
            "typing_speed": session_data.get("typing_speed", 0),
            "accuracy": session_data.get("accuracy", 0),
            "session_duration": session_data.get("duration", 0),
            "features": self.extract_features(session_data.get("keystrokes", []))
        }
        
        sessions.append(session_entry)
        
        # Save updated sessions
        with open(self.keystroke_file, 'w') as f:
            json.dump(sessions, f, indent=2)
            
        # Update profile
        self.profile["training_sessions"] += 1
        self.profile["total_keystrokes"] += len(session_data.get("keystrokes", []))
        self.profile["last_training"] = datetime.now().isoformat()
        self.save_profile()
        
        print(f"✅ Session {session_entry['session_id']} saved for user {self.user_id}")
        return session_entry["session_id"]
        
    def load_all_sessions(self):
        """Load all keystroke sessions"""
        if os.path.exists(self.keystroke_file):
            with open(self.keystroke_file, 'r') as f:
                return json.load(f)
        return []
        
    def extract_features(self, keystrokes):
        """Extract typing pattern features from keystroke data"""
        if len(keystrokes) < 2:
            return {}
            
        features = {
            "dwell_times": [],  # Time key is held down
            "flight_times": [], # Time between key releases
            "typing_rhythm": [],
            "pressure_patterns": [],
            "key_intervals": {}
        }
        
        for i in range(len(keystrokes) - 1):
            current = keystrokes[i]
            next_key = keystrokes[i + 1]
            
            # Dwell time (key down to key up)
            if current.get('type') == 'down' and i + 1 < len(keystrokes):
                for j in range(i + 1, len(keystrokes)):
                    if keystrokes[j].get('key') == current.get('key') and keystrokes[j].get('type') == 'up':
                        dwell_time = keystrokes[j]['timestamp'] - current['timestamp']
                        features["dwell_times"].append(dwell_time)
                        break
            
            # Flight time (key up to next key down)
            if current.get('type') == 'up' and next_key.get('type') == 'down':
                flight_time = next_key['timestamp'] - current['timestamp']
                features["flight_times"].append(flight_time)
                
            # Key pair intervals
            if current.get('type') == 'down' and next_key.get('type') == 'down':
                key_pair = f"{current.get('key', '')}-{next_key.get('key', '')}"
                interval = next_key['timestamp'] - current['timestamp']
                if key_pair not in features["key_intervals"]:
                    features["key_intervals"][key_pair] = []
                features["key_intervals"][key_pair].append(interval)
        
        # Calculate statistics
        if features["dwell_times"]:
            features["avg_dwell_time"] = np.mean(features["dwell_times"])
            features["std_dwell_time"] = np.std(features["dwell_times"])
            
        if features["flight_times"]:
            features["avg_flight_time"] = np.mean(features["flight_times"])
            features["std_flight_time"] = np.std(features["flight_times"])
            
        return features
        
    def prepare_training_data(self):
        """Prepare feature vectors for machine learning"""
        sessions = self.load_all_sessions()
        
        if len(sessions) < 3:
            print("❌ Need at least 3 training sessions to build a model")
            return None, None
            
        feature_vectors = []
        labels = []
        
        for session in sessions:
            features = session.get("features", {})
            
            # Create feature vector
            vector = [
                features.get("avg_dwell_time", 0),
                features.get("std_dwell_time", 0),
                features.get("avg_flight_time", 0),
                features.get("std_flight_time", 0),
                len(features.get("dwell_times", [])),
                len(features.get("flight_times", [])),
                session.get("typing_speed", 0),
                session.get("accuracy", 0),
                session.get("session_duration", 0)
            ]
            
            # Add common key pair timings
            key_intervals = features.get("key_intervals", {})
            common_pairs = ["th", "he", "er", "an", "in", "on", "at", "ed", "nd", "to"]
            
            for pair in common_pairs:
                if pair in key_intervals:
                    vector.append(np.mean(key_intervals[pair]))
                else:
                    vector.append(0)
                    
            feature_vectors.append(vector)
            labels.append(1)  # All training data is from legitimate user
            
        return np.array(feature_vectors), np.array(labels)
        
    def train_model(self):
        """Train machine learning model on user's typing patterns"""
        print(f"🤖 Training typing pattern model for user {self.user_id}...")
        
        X, y = self.prepare_training_data()
        
        if X is None:
            return False
            
        try:
            # Use Isolation Forest for anomaly detection
            # This will learn what "normal" typing looks like for this user
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train isolation forest (contamination = expected % of outliers)
            self.model = IsolationForest(
                contamination=0.1,  # Expect 10% outliers
                random_state=42,
                n_estimators=100
            )
            
            self.model.fit(X_scaled)
            
            # Save model and scaler
            joblib.dump(self.model, self.model_file)
            joblib.dump(self.scaler, self.scaler_file)
            
            # Update profile
            self.profile["is_trained"] = True
            self.profile["model_accuracy"] = self.evaluate_model(X_scaled)
            self.save_profile()
            
            print(f"✅ Model trained successfully! Accuracy: {self.profile['model_accuracy']:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ Model training failed: {e}")
            return False
            
    def load_model(self):
        """Load trained model from file"""
        try:
            if os.path.exists(self.model_file) and os.path.exists(self.scaler_file):
                self.model = joblib.load(self.model_file)
                self.scaler = joblib.load(self.scaler_file)
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
            
    def evaluate_model(self, X_scaled):
        """Evaluate model performance"""
        try:
            # Predict on training data (should mostly be 1 for inliers)
            predictions = self.model.predict(X_scaled)
            accuracy = np.sum(predictions == 1) / len(predictions)
            return accuracy
        except:
            return 0.0
            
    def authenticate_typing(self, keystroke_data):
        """Authenticate user based on typing pattern"""
        if not self.profile["is_trained"]:
            print("❌ No trained model available. Please complete training first.")
            return False, 0.0
            
        if not self.load_model():
            print("❌ Failed to load authentication model")
            return False, 0.0
            
        try:
            # Extract features from current typing
            features = self.extract_features(keystroke_data.get("keystrokes", []))
            
            # Create feature vector (same format as training)
            vector = [
                features.get("avg_dwell_time", 0),
                features.get("std_dwell_time", 0),
                features.get("avg_flight_time", 0),
                features.get("std_flight_time", 0),
                len(features.get("dwell_times", [])),
                len(features.get("flight_times", [])),
                keystroke_data.get("typing_speed", 0),
                keystroke_data.get("accuracy", 0),
                keystroke_data.get("duration", 0)
            ]
            
            # Add common key pair timings
            key_intervals = features.get("key_intervals", {})
            common_pairs = ["th", "he", "er", "an", "in", "on", "at", "ed", "nd", "to"]
            
            for pair in common_pairs:
                if pair in key_intervals:
                    vector.append(np.mean(key_intervals[pair]))
                else:
                    vector.append(0)
            
            # Scale and predict
            vector_scaled = self.scaler.transform([vector])
            prediction = self.model.predict(vector_scaled)[0]
            confidence = self.model.decision_function(vector_scaled)[0]
            
            # Convert to probability-like score
            confidence_score = max(0, min(1, (confidence + 0.5) / 1.0))
            
            is_authentic = prediction == 1 and confidence_score > 0.3
            
            print(f"🔍 Authentication result: {'✅ AUTHENTIC' if is_authentic else '❌ SUSPICIOUS'}")
            print(f"📊 Confidence score: {confidence_score:.3f}")
            
            return is_authentic, confidence_score
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False, 0.0
            
    def get_user_stats(self):
        """Get comprehensive user statistics"""
        sessions = self.load_all_sessions()
        
        stats = {
            "profile": self.profile,
            "total_sessions": len(sessions),
            "model_status": "Trained" if self.profile["is_trained"] else "Not Trained",
            "data_files": {
                "profile_exists": os.path.exists(self.profile_file),
                "keystrokes_exists": os.path.exists(self.keystroke_file),
                "model_exists": os.path.exists(self.model_file)
            }
        }
        
        if sessions:
            typing_speeds = [s.get("typing_speed", 0) for s in sessions]
            accuracies = [s.get("accuracy", 0) for s in sessions]
            
            stats["performance"] = {
                "avg_typing_speed": np.mean(typing_speeds),
                "best_typing_speed": max(typing_speeds),
                "avg_accuracy": np.mean(accuracies),
                "best_accuracy": max(accuracies),
                "improvement_trend": "Improving" if len(typing_speeds) > 1 and typing_speeds[-1] > typing_speeds[0] else "Stable"
            }
            
        return stats
        
    def export_data(self, export_path=None):
        """Export all user data for backup"""
        if not export_path:
            export_path = f"{self.user_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        export_data = {
            "user_id": self.user_id,
            "export_date": datetime.now().isoformat(),
            "profile": self.profile,
            "sessions": self.load_all_sessions(),
            "model_trained": self.profile["is_trained"]
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        print(f"📦 Data exported to: {export_path}")
        return export_path
        
    def import_data(self, import_path):
        """Import user data from backup"""
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
                
            # Restore profile
            self.profile = import_data["profile"]
            self.save_profile()
            
            # Restore sessions
            with open(self.keystroke_file, 'w') as f:
                json.dump(import_data["sessions"], f, indent=2)
                
            print(f"📥 Data imported successfully from: {import_path}")
            return True
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False

def main():
    """Test the keystroke storage system"""
    print("🔒 KEYSTROKE STORAGE SYSTEM TEST")
    print("=" * 40)
    
    # Create storage instance
    storage = KeystrokeStorage("test_user")
    
    # Show current stats
    stats = storage.get_user_stats()
    print(f"👤 User: {stats['profile']['user_id']}")
    print(f"📊 Sessions: {stats['total_sessions']}")
    print(f"🤖 Model: {stats['model_status']}")
    print(f"📁 Data files: {stats['data_files']}")
    
    # Simulate some training sessions
    if stats['total_sessions'] < 3:
        print("\n🎯 Adding sample training sessions...")
        
        for i in range(3):
            sample_session = {
                "text": f"This is training session number {i+1}",
                "keystrokes": [
                    {"key": "t", "type": "down", "timestamp": 1000 + i*100},
                    {"key": "t", "type": "up", "timestamp": 1050 + i*100},
                    {"key": "h", "type": "down", "timestamp": 1100 + i*100},
                    {"key": "h", "type": "up", "timestamp": 1150 + i*100},
                ],
                "typing_speed": 45 + i*5,
                "accuracy": 0.95 + i*0.01,
                "duration": 30 + i*2
            }
            
            session_id = storage.save_keystroke_session(sample_session)
            print(f"  ✅ Session {session_id} saved")
    
    # Train model if enough data
    if stats['total_sessions'] >= 3 and not stats['profile']['is_trained']:
        print("\n🤖 Training authentication model...")
        success = storage.train_model()
        if success:
            print("✅ Model training completed!")
        else:
            print("❌ Model training failed!")
    
    # Test authentication
    if storage.profile["is_trained"]:
        print("\n🔍 Testing authentication...")
        
        test_data = {
            "keystrokes": [
                {"key": "t", "type": "down", "timestamp": 2000},
                {"key": "t", "type": "up", "timestamp": 2050},
                {"key": "e", "type": "down", "timestamp": 2100},
                {"key": "e", "type": "up", "timestamp": 2150},
            ],
            "typing_speed": 47,
            "accuracy": 0.96,
            "duration": 32
        }
        
        is_authentic, confidence = storage.authenticate_typing(test_data)
        print(f"Result: {'✅ Authentic' if is_authentic else '❌ Suspicious'} (confidence: {confidence:.3f})")
    
    # Export data
    print("\n📦 Exporting user data...")
    export_file = storage.export_data()
    
    print(f"\n📈 Final Stats:")
    final_stats = storage.get_user_stats()
    print(f"  • Total sessions: {final_stats['total_sessions']}")
    print(f"  • Model trained: {final_stats['profile']['is_trained']}")
    print(f"  • Total keystrokes: {final_stats['profile']['total_keystrokes']}")

if __name__ == "__main__":
    main()
