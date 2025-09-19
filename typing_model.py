import numpy as np
import json
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import matplotlib.pyplot as plt

class TypingPatternModel:
    def __init__(self, model_path="typing_model.pkl", scaler_path="scaler.pkl"):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.is_trained = False
        self.feature_names = [
            'avg_dwell_time', 'std_dwell_time', 'avg_flight_time', 
            'std_flight_time', 'typing_speed', 'rhythm_consistency', 'pressure_pattern'
        ]
        
    def load_training_data(self, filename="training_data.json"):
        """Load training data from JSON file"""
        if not os.path.exists(filename):
            print(f"Training data file {filename} not found!")
            return None, None
            
        with open(filename, 'r') as f:
            data = json.load(f)
            
        if not data:
            print("No training data available!")
            return None, None
            
        # Extract features
        features = []
        for session in data:
            feature_vector = []
            for feature_name in self.feature_names:
                feature_vector.append(session['features'].get(feature_name, 0))
            features.append(feature_vector)
            
        return np.array(features), len(data)
        
    def train_model(self, training_file="training_data.json", contamination=0.1):
        """Train the typing pattern recognition model"""
        print("Loading training data...")
        X, num_sessions = self.load_training_data(training_file)
        
        if X is None or len(X) < 3:
            print("Insufficient training data! Need at least 3 sessions.")
            return False
            
        print(f"Training with {num_sessions} sessions...")
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Use Isolation Forest for anomaly detection (one-class classification)
        # This treats the user's typing pattern as "normal" and everything else as anomalous
        self.model = IsolationForest(
            contamination=contamination,  # Expected proportion of outliers
            random_state=42,
            n_estimators=100
        )
        
        # Train the model
        self.model.fit(X_scaled)
        
        # Calculate training accuracy
        predictions = self.model.predict(X_scaled)
        normal_predictions = np.sum(predictions == 1)
        accuracy = normal_predictions / len(predictions)
        
        print(f"Training completed!")
        print(f"Training accuracy: {accuracy:.2%}")
        print(f"Model considers {normal_predictions}/{len(predictions)} training samples as normal")
        
        self.is_trained = True
        return True
        
    def save_model(self):
        """Save the trained model and scaler"""
        if not self.is_trained:
            print("Model not trained yet!")
            return False
            
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print(f"Model saved to {self.model_path}")
        print(f"Scaler saved to {self.scaler_path}")
        return True
        
    def load_model(self):
        """Load a previously trained model"""
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            print("Model files not found!")
            return False
            
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            self.is_trained = True
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
            
    def authenticate(self, features_dict, threshold=0.0):
        """Authenticate user based on typing pattern"""
        if not self.is_trained:
            print("Model not trained! Please train the model first.")
            return False, 0.0
            
        # Convert features dict to vector
        feature_vector = []
        for feature_name in self.feature_names:
            feature_vector.append(features_dict.get(feature_name, 0))
            
        feature_vector = np.array(feature_vector).reshape(1, -1)
        
        # Scale features
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Get prediction and decision score
        prediction = self.model.predict(feature_vector_scaled)[0]
        decision_score = self.model.decision_function(feature_vector_scaled)[0]
        
        # Convert decision score to confidence (0-1 scale)
        confidence = max(0, min(1, (decision_score + 0.5) / 1.0))
        
        is_authentic = prediction == 1 and decision_score >= threshold
        
        return is_authentic, confidence
        
    def get_model_info(self):
        """Get information about the trained model"""
        if not self.is_trained:
            return "Model not trained"
            
        info = {
            'model_type': 'Isolation Forest',
            'features': self.feature_names,
            'is_trained': self.is_trained,
            'model_path': self.model_path,
            'scaler_path': self.scaler_path
        }
        
        return info
        
    def visualize_training_data(self, training_file="training_data.json"):
        """Visualize the training data distribution"""
        X, num_sessions = self.load_training_data(training_file)
        
        if X is None:
            return
            
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.ravel()
        
        for i, feature_name in enumerate(self.feature_names):
            if i < len(axes):
                axes[i].hist(X[:, i], bins=10, alpha=0.7, edgecolor='black')
                axes[i].set_title(f'{feature_name}')
                axes[i].set_xlabel('Value')
                axes[i].set_ylabel('Frequency')
                
        # Remove empty subplot
        if len(self.feature_names) < len(axes):
            fig.delaxes(axes[-1])
            
        plt.tight_layout()
        plt.savefig('training_data_distribution.png')
        plt.show()
        print("Training data visualization saved as 'training_data_distribution.png'")

def main():
    model = TypingPatternModel()
    
    print("Typing Pattern Recognition Model")
    print("=" * 35)
    
    while True:
        print("\n1. Train new model")
        print("2. Load existing model")
        print("3. Test authentication")
        print("4. View model info")
        print("5. Visualize training data")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            if model.train_model():
                save_choice = input("Save the trained model? (y/n): ").strip().lower()
                if save_choice == 'y':
                    model.save_model()
                    
        elif choice == '2':
            model.load_model()
            
        elif choice == '3':
            if not model.is_trained:
                print("Please train or load a model first!")
                continue
                
            print("Please provide typing features for authentication test:")
            print("(You can get these from the keystroke collector)")
            
            # Example test with dummy data
            test_features = {
                'avg_dwell_time': float(input("Average dwell time: ") or "0.1"),
                'std_dwell_time': float(input("Std dwell time: ") or "0.05"),
                'avg_flight_time': float(input("Average flight time: ") or "0.2"),
                'std_flight_time': float(input("Std flight time: ") or "0.1"),
                'typing_speed': float(input("Typing speed: ") or "5.0"),
                'rhythm_consistency': float(input("Rhythm consistency: ") or "0.8"),
                'pressure_pattern': float(input("Pressure pattern: ") or "0.5")
            }
            
            is_authentic, confidence = model.authenticate(test_features)
            print(f"\nAuthentication Result: {'AUTHENTIC' if is_authentic else 'NOT AUTHENTIC'}")
            print(f"Confidence: {confidence:.2%}")
            
        elif choice == '4':
            info = model.get_model_info()
            if isinstance(info, dict):
                for key, value in info.items():
                    print(f"{key}: {value}")
            else:
                print(info)
                
        elif choice == '5':
            model.visualize_training_data()
            
        elif choice == '6':
            break
            
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
