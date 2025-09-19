# 🔒 Security Control Mobile App

A real native Android app for remote laptop security control.

## 📱 Features
- Emergency remote shutdown
- System lock control
- Real-time connection monitoring
- Firebase push notifications
- Professional UI with Material Design
- Haptic feedback and animations

## 🚀 Installation Steps

### Prerequisites
1. Install Flutter SDK: https://flutter.dev/docs/get-started/install
2. Install Android Studio
3. Enable Developer Options on your Android phone
4. Enable USB Debugging

### Build & Install

1. **Navigate to mobile app directory:**
   ```bash
   cd "e:\Mini Project\mobile_app"
   ```

2. **Get Flutter dependencies:**
   ```bash
   flutter pub get
   ```

3. **Connect your Android phone via USB**

4. **Check connected devices:**
   ```bash
   flutter devices
   ```

5. **Build and install the app:**
   ```bash
   flutter run --release
   ```

### Alternative: Build APK for manual installation

1. **Build APK:**
   ```bash
   flutter build apk --release
   ```

2. **APK location:**
   ```
   build/app/outputs/flutter-apk/app-release.apk
   ```

3. **Transfer APK to phone and install**

## ⚙️ Configuration

1. **Update laptop IP in the app:**
   - Open app settings
   - Enter your laptop's IP address
   - Default: Auto-detect from same network

2. **Firebase Setup (Optional for push notifications):**
   - Create Firebase project
   - Add Android app
   - Download google-services.json
   - Place in android/app/ directory

## 🧪 Testing

1. Ensure laptop server is running on port 8080
2. Phone and laptop on same WiFi network
3. Test connection in app
4. Try emergency shutdown (with confirmation)

## 📋 Troubleshooting

- **Connection issues:** Check firewall settings
- **Build errors:** Run `flutter doctor` to check setup
- **APK install fails:** Enable "Install from unknown sources"
