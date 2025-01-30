import os
import requests
import openai
from flask import Flask, render_template, jsonify, request
import logging
import time

app = Flask(__name__)

# Load OpenAI API Key from environment variables (DO NOT hardcode API key)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY  # Set API key globally

# Global variable for ESP32 IP and latest sensor data
ESP32_LOCAL_IP = None
latest_data = None  # Initialize latest_data here

def detect_esp32():
    """Finds the correct ESP32 IP address dynamically with retries."""
    global ESP32_LOCAL_IP
    known_ips = ["192.168.1.11", "192.168.1.101", "192.168.4.1", "192.168.4.2"]
    
    retries = 3
    for attempt in range(retries):
        for ip in known_ips:
            test_url = f"http://{ip}:5000/data"
            try:
                logging.info(f"🔍 Trying to detect ESP32 at {ip} (Attempt {attempt + 1}/{retries})...")
                response = requests.get(test_url, timeout=10)  # Increased timeout to 10 seconds
                if response.status_code == 200:
                    ESP32_LOCAL_IP = ip
                    logging.info(f"✅ ESP32 detected at {ESP32_LOCAL_IP}")
                    return
            except requests.exceptions.RequestException as e:
                logging.warning(f"⚠️ Failed to connect to {ip}: {str(e)}")
                time.sleep(2)  # Wait 2 seconds before retrying
        
    logging.error("❌ ESP32 not found after retries! Using last known IP.")
    if not ESP32_LOCAL_IP:
        ESP32_LOCAL_IP = "192.168.4.1"  # Default AP Mode IP

@app.route("/")
def index():
    """Render frontend page."""
    return render_template("index.html")

@app.route("/data", methods=["POST"])
def receive_data():
    """Receives sensor data from ESP32 and stores it."""
    global latest_data
    try:
        sensor_data = request.get_json()
        if sensor_data:
            logging.info(f"✅ Received data: {sensor_data}")
            latest_data = sensor_data  # Save the latest data
            return jsonify({"status": "success"}), 200
        else:
            logging.error("❌ No data received.")
            return jsonify({"error": "No data received"}), 400
    except Exception as e:
        logging.error(f"❌ Error processing data: {str(e)}")
        return jsonify({"error": "Failed to process data"}), 500

@app.route("/data", methods=["GET"])
def send_data():
    """Sends the latest sensor data to the frontend."""
    if latest_data:
        return jsonify(latest_data)
    else:
        logging.warning("⚠️ No sensor data available.")
        return jsonify({"error": "No sensor data available"}), 404

@app.route("/forward", methods=["POST"])
def forward_data():
    """Forwards latest data to ESP32 when running externally."""
    if not ESP32_LOCAL_IP:
        detect_esp32()

    if ESP32_LOCAL_IP:
        esp32_url = f"http://{ESP32_LOCAL_IP}:5000/data"
        try:
            logging.info(f"📡 Forwarding data to ESP32 at {esp32_url}...")
            response = requests.post(esp32_url, json=latest_data, timeout=10)  # Increased timeout
            logging.info(f"✅ Forwarded data to ESP32 with response: {response.status_code}")
            return jsonify({"status": "forwarded", "esp32_response": response.status_code})
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Error forwarding data to ESP32: {str(e)}")
            return jsonify({"error": "Failed to forward data to ESP32"}), 500

    logging.error("❌ ESP32 IP not detected.")
    return jsonify({"error": "ESP32 IP not detected"}), 500

@app.route("/chatgpt", methods=["POST"])
def chatgpt():
    """Handles ChatGPT API requests securely."""
    if not OPENAI_API_KEY:
        logging.error("❌ OpenAI API key is missing!")
        return jsonify({"reply": "❌ Error: OpenAI API key is missing!"}), 500

    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        logging.warning("⚠️ Empty message received from user.")
        return jsonify({"reply": "⚠️ Error: Empty message received."}), 400

    try:
        logging.info(f"🗣 Sending user message to ChatGPT: {user_message}")
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
        )
        return jsonify({"reply": response["choices"][0]["message"]["content"]})

    except openai.error.OpenAIError as e:
        logging.error(f"❌ OpenAI API Error: {str(e)}")
        return jsonify({"reply": f"Error calling ChatGPT API: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"❌ Unexpected Error: {str(e)}")
        return jsonify({"reply": "An unexpected error occurred."}), 500

# Enable dynamic port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    detect_esp32()  # Detect ESP32 before running Flask
    app.run(host="0.0.0.0", port=port, debug=True)
