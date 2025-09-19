# 🔒 Security Control System

A professional-grade cybersecurity system with biometric authentication, cross-network communication, and remote shutdown capabilities using Firebase Cloud infrastructure.

## 🚀 Features

- **🔐 Biometric Authentication**: Advanced keystroke pattern analysis for user identification
- **📊 Real-time Monitoring**: Continuous system monitoring and threat detection
- **📱 Cross-Network Control**: Mobile app works across different networks (college WiFi + mobile data)
- **🔥 Firebase Integration**: Cloud-based communication for global accessibility
- **🌐 Web Interface**: Browser-based control panel with modern UI
- **⚡ Emergency Shutdown**: Instant remote shutdown capability
- **📞 Alert System**: Immediate mobile alerts and phone call notifications

## 🏗️ Architecture

```
Mobile App (Mobile Data) → Firebase Cloud → Laptop Service (College WiFi)
```

- **Cross-Network Communication**: Works when devices are on different networks
- **Firebase Realtime Database**: Cloud relay for commands and status
- **REST API Integration**: Direct HTTP calls for reliable communication
- **Professional Security**: Industry-standard Firebase platform by Google

## 📁 Project Structure
- Email account (for notifications)
- All dependencies listed in `requirements.txt`

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the system**:
   ```bash
   # GUI Version (Recommended)
   python security_gui.py
   
   # Command Line Version
   python security_system.py
   ```

## 📖 Usage Guide

### First Time Setup

1. **Launch the GUI**: Run `python security_gui.py`
2. **Setup User Profile**: Click "Setup User Profile" and complete 5 training sessions
3. **Configure Notifications**: Go to Settings and configure email/SMS alerts
4. **Start Security System**: Click "Start Security System"

### Training Sessions

- Each training session lasts 30 seconds
- Type naturally during training - sentences, passwords, or random text
- Focus on your normal typing speed and rhythm
- Complete at least 5 sessions for best accuracy

### Authentication Process

- When the system is locked, you'll be prompted to type for authentication
- Type the displayed text naturally
- The system analyzes your typing pattern in real-time
- Authentication succeeds if your pattern matches the trained model

### Security Features

- **Failed Attempt Tracking**: System tracks consecutive failed authentication attempts
- **Intruder Detection**: After 3-4 failed attempts (configurable):
  - Webcam captures intruder photo
  - Audio alarm activates for 15 seconds
  - Alert notifications sent via email/SMS
  - System locks for 5 minutes
- **Alert Logging**: All security incidents are logged with timestamps

## ⚙️ Configuration

### Email Notifications

1. Open Settings in the GUI or run `python notification_system.py`
2. Configure email settings:
   - **Gmail Users**: Enable 2-factor authentication and use an app password
   - **Other Providers**: Use regular email credentials
3. Test notifications to ensure they work

### SMS Notifications

1. Sign up for an SMS API service (TextLocal, Twilio, etc.)
2. Configure SMS settings with your API credentials
3. Test SMS functionality

### Security Settings

- **Max Failed Attempts**: Adjust the number of failed attempts before triggering security response
- **Authentication Timeout**: Configure how long users have to complete authentication
- **Lockout Duration**: Set how long the system remains locked after a security breach

## 📁 File Structure

```
Mini Project/
├── security_gui.py          # Main GUI application
├── security_system.py       # Core security system logic
├── keystroke_collector.py   # Typing pattern data collection
├── typing_model.py          # Machine learning model for pattern recognition
├── notification_system.py   # Email/SMS alert system
├── requirements.txt         # Python dependencies
├── README.md               # This documentation
└── Generated Files:
    ├── training_data.json      # Collected typing pattern data
    ├── typing_model.pkl        # Trained ML model
    ├── scaler.pkl             # Feature scaling model
    ├── security_config.json   # System configuration
    ├── security_alerts.json   # Security incident logs
    └── intruder_*.jpg         # Captured intruder photos
```

## 🔧 Technical Details

### Machine Learning Approach

- **Algorithm**: Isolation Forest (anomaly detection)
- **Features Analyzed**:
  - Average dwell time (how long keys are held)
  - Dwell time standard deviation
  - Average flight time (time between keystrokes)
  - Flight time standard deviation
  - Typing speed (characters per second)
  - Rhythm consistency
  - Pressure patterns

### Security Measures

- **One-Class Classification**: Treats authorized user's typing as "normal" and everything else as anomalous
- **Confidence Scoring**: Authentication requires minimum 70% confidence
- **Progressive Security**: Escalating responses to repeated failed attempts
- **Tamper Resistance**: System locks and alerts on suspicious activity

## 🚨 Security Considerations

### Strengths
- **Behavioral Biometrics**: Difficult to replicate typing patterns
- **Non-Intrusive**: No special hardware required
- **Continuous Authentication**: Can be used for ongoing verification
- **Multi-Factor**: Combines something you know (what to type) with something you are (how you type)

### Limitations
- **Environmental Factors**: Stress, fatigue, or injury can affect typing patterns
- **Learning Period**: Requires initial training and may need periodic retraining
- **Keyboard Dependency**: Different keyboards may affect accuracy
- **Not Foolproof**: Determined attackers might attempt to mimic typing patterns

### Best Practices
- **Regular Retraining**: Periodically retrain the model to account for natural changes
- **Backup Authentication**: Have alternative authentication methods available
- **Secure Storage**: Keep model files and configuration secure
- **Network Security**: Protect notification credentials and API keys

## 🐛 Troubleshooting

### Common Issues

**Authentication Always Fails**
- Retrain the model with more sessions
- Check if you're typing on a different keyboard
- Ensure you're typing naturally, not too fast or slow

**Camera Not Working**
- Check camera permissions
- Ensure no other applications are using the camera
- Try different camera indices in the code

**Notifications Not Sending**
- Verify email/SMS credentials
- Check internet connection
- For Gmail, ensure you're using an app password

**GUI Not Responding**
- Close and restart the application
- Check for Python/dependency version conflicts

### Getting Help

1. Check the system logs in the GUI
2. Review configuration files for errors
3. Test individual components (typing collector, model, notifications)
4. Ensure all dependencies are properly installed

## 📝 License

This project is for educational and personal use. Please ensure compliance with local laws and regulations when implementing biometric security systems.

## 🤝 Contributing

Feel free to improve the system by:
- Adding new typing pattern features
- Implementing additional notification methods
- Enhancing the GUI interface
- Improving security measures
- Adding support for multiple users

## ⚠️ Disclaimer

This system is designed for educational purposes and personal use. While it provides a reasonable level of security, it should not be the sole security measure for highly sensitive applications. Always implement multiple layers of security and follow cybersecurity best practices.
