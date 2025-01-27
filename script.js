document.addEventListener("DOMContentLoaded", () => {
    initChart();

    const measureDataButton = document.getElementById("measure-data-button");
    const chatbox = document.getElementById("chatbox");
    const userInput = document.getElementById("user-input");

    // ESP32 IP Address
    const esp32Url = "http://192.168.4.1/data"; // Update this endpoint if needed

    // Function to handle measuring data
    measureDataButton.addEventListener("click", async () => {
        try {
            const data = await fetchSensorData();
            displaySensorData(data);
            const healthStatus = analyzePlantHealth(data);
            document.getElementById("health-status").innerText = healthStatus;

            // Auto-send a message to ChatGPT about the fetched data
            const autoMessage = `The current sensor data is: Temperature ${data.temperature}°C, Humidity ${data.humidity}%, and Light Intensity ${data.light} lux. What can you tell me about the plant's health?`;
            appendToChatbox("You", autoMessage);
            const chatGPTResponse = await fetchChatGPTResponse(autoMessage);
            appendToChatbox("ChatGPT", chatGPTResponse);
        } catch (error) {
            console.error("Error fetching data:", error);
            appendToChatbox("ChatGPT", "Error: Unable to fetch data from the ESP32. Please check the connection.");
        }
    });

    // Function to fetch sensor data from ESP32
    async function fetchSensorData() {
        const response = await fetch(esp32Url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json(); // Assuming the ESP32 returns JSON like { temperature: 25, humidity: 60, light: 300 }
    }

    // Function to display sensor data on the dashboard
    function displaySensorData(data) {
        document.getElementById("temp").innerText = data.temperature;
        document.getElementById("humidity").innerText = data.humidity;
        document.getElementById("light").innerText = data.light;
        updateChart(data);
    }

    // Mock function to analyze plant health based on sensor data
    function analyzePlantHealth(data) {
        if (data.temperature < 18 || data.temperature > 30) return "Warning: Temperature out of range!";
        if (data.humidity < 40 || data.humidity > 70) return "Warning: Humidity out of range!";
        if (data.light < 200) return "Warning: Low light intensity!";
        return "The plant is healthy.";
    }

    // Function to append messages to the chatbox
    function appendToChatbox(sender, message) {
        chatbox.value += `${sender}: ${message}\n\n`;
        chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll to the bottom
    }

    // Function to fetch response from ChatGPT (mocked for now)
    async function fetchChatGPTResponse(message) {
        // Replace this URL with your backend that interacts with the ChatGPT API
        const chatGPTApiUrl = "https://your-backend-api.com/chatgpt";
        const response = await fetch(chatGPTApiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.reply; // Assuming the response has { reply: "ChatGPT's response here" }
    }

    // Input event for ChatGPT interaction via search bar
    userInput.addEventListener("keydown", async (event) => {
        if (event.key === "Enter") {
            const userMessage = userInput.value.trim();
            if (!userMessage) return;

            appendToChatbox("You", userMessage);
            try {
                const chatGPTResponse = await fetchChatGPTResponse(userMessage);
                appendToChatbox("ChatGPT", chatGPTResponse);
            } catch (error) {
                console.error("Error interacting with ChatGPT:", error);
                appendToChatbox("ChatGPT", "Error: Unable to connect to ChatGPT API.");
            }

            userInput.value = ""; // Clear the input field
        }
    });

    // Function to initialize the chart (Placeholder)
    function initChart() {
        const ctx = document.getElementById("sensor-chart").getContext("2d");
        window.myChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "Temperature (°C)",
                        data: [],
                        borderColor: "rgb(255, 99, 132)",
                        tension: 0.1,
                    },
                    {
                        label: "Humidity (%)",
                        data: [],
                        borderColor: "rgb(54, 162, 235)",
                        tension: 0.1,
                    },
                    {
                        label: "Light Intensity (lux)",
                        data: [],
                        borderColor: "rgb(75, 192, 192)",
                        tension: 0.1,
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    x: { beginAtZero: true },
                    y: { beginAtZero: true },
                },
            },
        });
    }

    // Function to update chart with new data
    function updateChart(data) {
        const chart = window.myChart;
        const now = new Date().toLocaleTimeString();
        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(data.temperature);
        chart.data.datasets[1].data.push(data.humidity);
        chart.data.datasets[2].data.push(data.light);
        chart.update();
    }
    if (chart.data.labels.length > 20) {
        chart.data.labels.shift(); // Remove the oldest label
        chart.data.datasets[0].data.shift(); // Remove the oldest temperature data
        chart.data.datasets[1].data.shift(); // Remove the oldest humidity data
        chart.data.datasets[2].data.shift(); // Remove the oldest light data
    }
    
});
