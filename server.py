from flask import Flask, jsonify, request
import os
import subprocess

app = Flask(__name__)

@app.route('/status')
def status():
    return jsonify({"status": "online", "message": "Laptop is connected!"})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        # Shutdown the laptop
        os.system("shutdown /s /f /t 0")
        return jsonify({"status": "success", "message": "Shutdown command executed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/lock', methods=['POST'])
def lock():
    try:
        # Lock the laptop
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return jsonify({"status": "success", "message": "System locked"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/test', methods=['POST'])
def test():
    return jsonify({"status": "success", "message": "Test command received"})

if __name__ == '__main__':
    print("🚀 Security Server Started!")
    print("📡 Listening on: http://0.0.0.0:3000")
    print("📱 Connect from mobile app with your laptop IP")
    print("IP Address: 192.168.29.43:3000")
    app.run(host='0.0.0.0', port=3000, debug=True)