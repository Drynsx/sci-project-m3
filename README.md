Plant Health Monitoring System
This project is a real-time plant health monitoring system that uses an ESP32 to collect environmental data (temperature, humidity, and light intensity) and sends it to a Flask-based server. The server processes this data and displays it on a web dashboard, which provides an interactive interface to monitor the plant's health. Additionally, the system uses AI (like ChatGPT) to provide health suggestions based on the collected data.

Features
ESP32 Sensor Data Collection: Collects data from sensors (temperature, humidity, light) using an ESP32 microcontroller.
Flask Backend: Serves as the API to receive and provide sensor data.
Web Interface: A user-friendly dashboard to visualize sensor data in real-time.
Health Analysis: Based on the sensor data, the system gives insights about the plant's health and suggests improvements.
ChatGPT Integration: Automatically sends sensor data to a mock ChatGPT API to get plant health feedback and other suggestions.
