from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint to receive data
@app.route('/update', methods=['POST'])
def update_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract sensor data
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    light = data.get('light')

    # Log the data
    print(f"Received data - Temperature: {temperature}, Humidity: {humidity}, Light: {light}")

    # Respond to ESP32
    return jsonify({"message": "Data received successfully"}), 200

if __name__ == '__main__':
    # No need to specify the host and port for Render
    app.run()
