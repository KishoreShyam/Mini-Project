"""
Simple Model Training Script
Focus on training the typing pattern model without security features
"""

from keystroke_collector import KeystrokeCollector
from typing_model import TypingPatternModel
import os

def train_typing_model():
    """Train the typing pattern model"""
    print("🎯 TYPING PATTERN MODEL TRAINING")
    print("=" * 40)
    print("This will train your security system to recognize your typing pattern.")
    print()
    
    # Initialize components
    collector = KeystrokeCollector()
    model = TypingPatternModel()
    
    # Get number of training sessions
    while True:
        try:
            num_sessions = input("How many training sessions? (recommended: 5-10): ").strip()
            num_sessions = int(num_sessions)
            if num_sessions > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\n📝 Starting {num_sessions} training sessions...")
    print("=" * 50)
    
    all_training_data = []
    
    for session in range(1, num_sessions + 1):
        print(f"\n🔄 TRAINING SESSION {session}/{num_sessions}")
        print("-" * 30)
        print("Instructions:")
        print("• Type naturally for 30 seconds")
        print("• You can type anything (sentences, stories, etc.)")
        print("• Don't worry about mistakes")
        print("• Focus on your normal typing speed and rhythm")
        print()
        
        input("Press Enter when ready to start typing...")
        
        print("\n⏱️  Starting keystroke collection...")
        print("Type anything for 30 seconds:")
        print("-" * 40)
        
        # Collect keystroke data for this session
        session_data = collector.collect_training_data(duration=30)
        
        if session_data:
            all_training_data.extend(session_data)
            print(f"✅ Session {session} completed! Collected {len(session_data)} keystroke patterns.")
        else:
            print(f"❌ Session {session} failed - no data collected.")
            
        if session < num_sessions:
            print("\n💤 Take a short break before the next session...")
            input("Press Enter to continue to next session...")
    
    print(f"\n📊 TRAINING DATA SUMMARY")
    print("=" * 30)
    print(f"Total sessions completed: {num_sessions}")
    print(f"Total keystroke patterns: {len(all_training_data)}")
    
    if len(all_training_data) < 10:
        print("⚠️  Warning: Very little training data collected.")
        print("   The model may not work well with so few samples.")
        choice = input("Continue anyway? (y/n): ").strip().lower()
        if choice != 'y':
            print("Training cancelled.")
            return False
    
    # Save training data
    print("\n💾 Saving training data...")
    collector.save_training_data(all_training_data)
    print("✅ Training data saved!")
    
    # Train the model
    print("\n🤖 Training machine learning model...")
    print("This may take a few moments...")
    
    success = model.train_model()
    
    if success:
        print("✅ Model training completed successfully!")
        print("\n📋 TRAINING RESULTS:")
        print(f"• Model type: Isolation Forest (Anomaly Detection)")
        print(f"• Training samples: {len(all_training_data)}")
        print(f"• Model saved: ✅")
        print(f"• Ready for authentication: ✅")
        
        # Test the trained model
        print("\n🧪 Testing the trained model...")
        test_choice = input("Would you like to test authentication now? (y/n): ").strip().lower()
        
        if test_choice == 'y':
            test_authentication(model, collector)
            
        return True
    else:
        print("❌ Model training failed!")
        print("Please try training again with more data.")
        return False

def test_authentication(model, collector):
    """Test the trained model"""
    print("\n🧪 AUTHENTICATION TEST")
    print("=" * 25)
    print("Type naturally to test if the model recognizes you.")
    print("Duration: 15 seconds")
    print()
    
    input("Press Enter when ready to start authentication test...")
    
    print("\n⏱️  Type for authentication (15 seconds):")
    print("-" * 40)
    
    # Collect test data
    test_data = collector.collect_training_data(duration=15)
    
    if test_data:
        # Extract features and test
        features = collector.extract_features(test_data)
        if features:
            is_authentic = model.authenticate(features)
            
            print(f"\n📊 AUTHENTICATION RESULT:")
            print("=" * 30)
            if is_authentic:
                print("✅ AUTHENTICATION SUCCESSFUL!")
                print("🔓 The model recognizes your typing pattern!")
                print("🎉 Your security system is ready to use!")
            else:
                print("❌ AUTHENTICATION FAILED!")
                print("🔒 The model doesn't recognize this typing pattern.")
                print("💡 You may need more training data or to retrain the model.")
        else:
            print("❌ Could not extract features from test data.")
    else:
        print("❌ No test data collected.")

def main():
    """Main training function"""
    print("🔒 KEYSTROKE SECURITY SYSTEM")
    print("🎯 Model Training Module")
    print("=" * 40)
    
    # Check if model already exists
    if os.path.exists("typing_model.pkl"):
        print("⚠️  A trained model already exists!")
        choice = input("Do you want to retrain? (y/n): ").strip().lower()
        if choice != 'y':
            print("Training cancelled. Existing model preserved.")
            return
    
    success = train_typing_model()
    
    if success:
        print("\n🎉 TRAINING COMPLETE!")
        print("=" * 25)
        print("Your typing pattern model is now trained and ready!")
        print("You can now run the full security system:")
        print("• python main.py (choose option 1 for GUI)")
        print("• python security_system.py (command line)")
    else:
        print("\n❌ Training failed. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
    except Exception as e:
        print(f"\nError during training: {e}")
        print("Please check your setup and try again.")
