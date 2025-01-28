from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_folder="static", template_folder="templates")

# Serve the index.html
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint to receive data
@app.route('/update', methods=['POST'])
def update_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    temperature = data.get('temperature')
    humidity = data.get('humidity')
    light = data.get('light')

    print(f"Received data - Temperature: {temperature}, Humidity: {humidity}, Light: {light}")
    return jsonify({"message": "Data received successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
