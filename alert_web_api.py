"""
Web API for Mobile Alert System
Provides REST endpoints for the web frontend to trigger alerts
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import json
import os
from mobile_alert_backend import MobileAlertSystem

app = Flask(__name__)
CORS(app)  # Enable CORS for web frontend

# Initialize alert system
alert_system = MobileAlertSystem()

@app.route('/')
def serve_index():
    """Serve the main web application"""
    return send_from_directory('web_app', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('web_app', filename)

@app.route('/api/alert/test', methods=['POST'])
def test_alert():
    """Test the alert system"""
    try:
        data = request.get_json() or {}
        alert_type = data.get('type', 'all')
        
        if alert_type == 'alarm':
            # Test alarm in background
            alarm_thread = threading.Thread(target=alert_system.play_emergency_alarm, args=(5,))
            alarm_thread.daemon = True
            alarm_thread.start()
            return jsonify({"success": True, "message": "Alarm test started"})
            
        elif alert_type == 'sms':
            result = alert_system.send_sms_alert("🧪 Test SMS from security system")
            return jsonify({"success": result, "message": "SMS test completed"})
            
        elif alert_type == 'email':
            result = alert_system.send_email_alert("🧪 Test Email", "This is a test email from your security system")
            return jsonify({"success": result, "message": "Email test completed"})
            
        elif alert_type == 'call':
            result = alert_system.make_emergency_call()
            return jsonify({"success": result, "message": "Emergency call test completed"})
            
        elif alert_type == 'camera':
            photo_path = alert_system.capture_intruder_photo()
            return jsonify({"success": bool(photo_path), "photo_path": photo_path, "message": "Camera test completed"})
            
        else:  # Test all systems
            def run_full_test():
                return alert_system.test_alert_system()
            
            test_thread = threading.Thread(target=run_full_test)
            test_thread.daemon = True
            test_thread.start()
            
            return jsonify({"success": True, "message": "Full system test started"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alert/breach', methods=['POST'])
def trigger_security_breach():
    """Trigger full security breach alert"""
    try:
        data = request.get_json() or {}
        breach_details = data.get('details', {})
        
        def run_breach_alert():
            return alert_system.trigger_security_breach_alert(breach_details)
        
        # Run in background to avoid blocking
        breach_thread = threading.Thread(target=run_breach_alert)
        breach_thread.daemon = True
        breach_thread.start()
        
        return jsonify({
            "success": True, 
            "message": "Security breach alert triggered",
            "mobile_number": alert_system.mobile_number,
            "timestamp": alert_system.config.get('timestamp', 'now')
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alert/config', methods=['GET'])
def get_alert_config():
    """Get current alert configuration"""
    try:
        return jsonify({
            "success": True,
            "config": {
                "mobile_number": alert_system.mobile_number,
                "preferences": alert_system.config["alert_preferences"],
                "services_configured": {
                    "twilio": bool(alert_system.config["twilio"]["account_sid"]),
                    "fast2sms": bool(alert_system.config["fast2sms"]["api_key"]),
                    "email": bool(alert_system.config["email"]["email"]),
                    "pushbullet": bool(alert_system.config["pushbullet"]["api_key"])
                }
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alert/config', methods=['POST'])
def update_alert_config():
    """Update alert configuration"""
    try:
        data = request.get_json()
        
        # Update preferences
        if 'preferences' in data:
            alert_system.config["alert_preferences"].update(data['preferences'])
            
        # Update mobile number
        if 'mobile_number' in data:
            alert_system.config["mobile_number"] = data['mobile_number']
            alert_system.mobile_number = data['mobile_number']
            
        # Save updated config
        with open('alert_config.json', 'w') as f:
            json.dump(alert_system.config, f, indent=2)
            
        return jsonify({"success": True, "message": "Configuration updated"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alert/status', methods=['GET'])
def get_alert_status():
    """Get current alert system status"""
    try:
        return jsonify({
            "success": True,
            "status": {
                "mobile_number": alert_system.mobile_number,
                "pygame_available": alert_system.pygame_available,
                "services_ready": {
                    "alarm": alert_system.pygame_available,
                    "camera": True,  # Assume camera is available
                    "twilio": bool(alert_system.config["twilio"]["account_sid"]),
                    "sms": bool(alert_system.config["fast2sms"]["api_key"]),
                    "email": bool(alert_system.config["email"]["email"]),
                    "push": bool(alert_system.config["pushbullet"]["api_key"])
                }
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alert/incidents', methods=['GET'])
def get_security_incidents():
    """Get security incident log"""
    try:
        incidents_file = "security_incidents.json"
        if os.path.exists(incidents_file):
            with open(incidents_file, 'r') as f:
                incidents = json.load(f)
        else:
            incidents = []
            
        return jsonify({
            "success": True,
            "incidents": incidents[-10:]  # Return last 10 incidents
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 MOBILE ALERT WEB API")
    print("=" * 30)
    print(f"📱 Target Mobile: {alert_system.mobile_number}")
    print("🌐 Server: http://localhost:5000")
    print("📋 API Endpoints:")
    print("  • POST /api/alert/test - Test alerts")
    print("  • POST /api/alert/breach - Trigger security breach")
    print("  • GET /api/alert/config - Get configuration")
    print("  • POST /api/alert/config - Update configuration")
    print("  • GET /api/alert/status - Get system status")
    print("  • GET /api/alert/incidents - Get incident log")
    print("=" * 30)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
