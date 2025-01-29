import os
import requests  # To forward data to ESP32 when hosted on Render
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ESP32 local server URL (for forwarding)
ESP32_LOCAL_URL = "http://192.168.4.2:5000/data"

# Store latest received data
latest_data = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data", methods=["POST"])
def receive_data():
    global latest_data
    try:
        sensor_data = request.get_json()
        if sensor_data:
            print(f"✅ Received data: {sensor_data}")
            latest_data = sensor_data  # Save the latest data
            
            # **Forward data to ESP32 if running on Render**
            if not request.remote_addr.startswith("192.168."):  # Check if request is external
                try:
                    response = requests.post(ESP32_LOCAL_URL, json=sensor_data, timeout=3)
                    print(f"📡 Forwarded to ESP32, Response: {response.status_code}")
                except requests.exceptions.RequestException:
                    print("⚠️ Failed to forward data to ESP32")

            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"error": "No data received"}), 400
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Failed to process data"}), 500

@app.route("/data", methods=["GET"])
def send_data():
    if latest_data:
        return jsonify(latest_data)
    else:
        return jsonify({"error": "No sensor data available"}), 404

# **Enable dynamic port for Render**
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if no PORT is found
    app.run(host='0.0.0.0', port=port, debug=True)
