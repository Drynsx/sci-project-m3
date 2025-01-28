from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")

# Enable CORS for the entire app
CORS(app)

# Store the latest sensor data
sensor_data = {
    'temperature': 25.0,  # Dummy initial values
    'humidity': 60.0,
    'light': 300
}

# Serve the index.html page at the root
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint to receive data from the ESP32 device (POST method)
@app.route('/update', methods=['POST'])
def update_data():
    # Ensure the content type is JSON
    if not request.is_json:
        return jsonify({"error": "Invalid content type, JSON expected"}), 400

    # Parse the JSON payload
    data = request.get_json()
    
    # Extract and validate data fields
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    light = data.get('light')

    if temperature is None or humidity is None or light is None:
        return jsonify({"error": "Missing data fields"}), 400

    # Update sensor data
    sensor_data['temperature'] = temperature
    sensor_data['humidity'] = humidity
    sensor_data['light'] = light

    # Log the received data for debugging
    print(f"Received data - Temperature: {temperature}, Humidity: {humidity}, Light: {light}")
    
    return jsonify({"message": "Data received successfully"}), 200

# Endpoint to serve the data to be fetched by the client (GET method)
@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(sensor_data)

if __name__ == '__main__':
    # Run the Flask app on all available interfaces (0.0.0.0) and port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
