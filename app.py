import os
import requests
import openai
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ESP32 local server URL
ESP32_LOCAL_URL = "http://192.168.4.2:5000/data"

# Store latest received data
latest_data = {}

# Load OpenAI API Key from environment variables (DO NOT hardcode API key)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY  # Set API key globally


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data", methods=["POST"])
def receive_data():
    """Receives sensor data from ESP32 and forwards it if needed."""
    global latest_data
    try:
        sensor_data = request.get_json()
        if sensor_data:
            print(f"✅ Received data: {sensor_data}")
            latest_data = sensor_data  # Save the latest data

            # Forward data to ESP32 if hosted externally (on Render)
            if not request.remote_addr.startswith("192.168."):
                try:
                    response = requests.post(ESP32_LOCAL_URL, json=sensor_data, timeout=3)
                    print(f"📡 Forwarded to ESP32, Response: {response.status_code}")
                except requests.exceptions.RequestException:
                    print("⚠️ Failed to forward data to ESP32")

            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"error": "No data received"}), 400
    except Exception as e:
        print(f"❌ Error processing data: {str(e)}")
        return jsonify({"error": "Failed to process data"}), 500


@app.route("/data", methods=["GET"])
def send_data():
    """Sends the latest sensor data to the frontend."""
    if latest_data:
        return jsonify(latest_data)
    else:
        return jsonify({"error": "No sensor data available"}), 404


@app.route("/chatgpt", methods=["POST"])
def chatgpt():
    """Handles ChatGPT API requests securely."""
    if not OPENAI_API_KEY:
        return jsonify({"reply": "❌ Error: OpenAI API key is missing!"}), 500

    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "⚠️ Error: Empty message received."}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Use "gpt-3.5-turbo" if needed
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
        )
        return jsonify({"reply": response["choices"][0]["message"]["content"]})

    except openai.error.OpenAIError as e:
        print(f"❌ ChatGPT API Error: {str(e)}")
        return jsonify({"reply": f"Error calling ChatGPT API: {str(e)}"}), 500
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return jsonify({"reply": "An unexpected error occurred."}), 500


# Enable dynamic port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
