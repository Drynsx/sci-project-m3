from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_folder="static", template_folder="templates")

# Serve the index.html page at the root
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint to receive data from the ESP32 device (POST method)
@app.route('/update', methods=['POST'])
def update_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400  # Return error if no data is provided

    # Extract data from the JSON payload
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    light = data.get('light')

    # Check if all required data fields are present
    if temperature is None or humidity is None or light is None:
        return jsonify({"error": "Missing data fields"}), 400

    # Print the received data for debugging
    print(f"Received data - Temperature: {temperature}, Humidity: {humidity}, Light: {light}")
    
    # You can store the data in a global variable or a database here if needed

    return jsonify({"message": "Data received successfully"}), 200  # Acknowledge successful reception of data

# Endpoint to serve the data to be fetched by the client (GET method)
@app.route('/data', methods=['GET'])
def get_data():
    # Here you should return actual sensor data; for now, returning dummy values
    # Replace this with actual data if required (e.g., from a database or in-memory storage)
    temperature = 25.0  # Dummy data
    humidity = 60.0     # Dummy data
    light = 300         # Dummy data

    print(f"Sending data - Temperature: {temperature}, Humidity: {humidity}, Light: {light}")
    
    # Return the data as a JSON response
    return jsonify({
        'temperature': temperature,
        'humidity': humidity,
        'light': light
    })

if __name__ == '__main__':
    # Run the Flask app on all available network interfaces (0.0.0.0) and on port 5000
    app.run(host='0.0.0.0', port=5000)
