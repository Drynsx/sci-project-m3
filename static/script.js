document.addEventListener("DOMContentLoaded", () => {
    initChart();

    const measureDataButton = document.getElementById("measure-data-button");
    const chatbox = document.getElementById("chatbox");
    const userInput = document.getElementById("user-input");

    // Flask server URL (Uses relative URL to avoid local network issues)
    const flaskUrl = "/data";

    // Handle button click for measuring sensor data
    measureDataButton.addEventListener("click", async () => {
        try {
            console.log("📡 Fetching sensor data...");
            const data = await fetchSensorData();
            console.log("✅ Data received:", data);

            displaySensorData(data);
            const healthStatus = analyzePlantHealth(data);
            document.getElementById("health-status").innerText = healthStatus;
        } catch (error) {
            console.error("❌ Error fetching data:", error);
            appendToChatbox("Error: Unable to fetch data. Please check the connection.");
        }
    });

    // Fetch sensor data from Flask server
    async function fetchSensorData() {
        try {
            const response = await fetch(flaskUrl);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error("❌ Fetch error:", error);
            throw error;
        }
    }

    // Display sensor data on the dashboard
    function displaySensorData(data) {
        document.getElementById("temp").innerText = data.temperature;
        document.getElementById("humidity").innerText = data.humidity;
        document.getElementById("light").innerText = data.light;
        updateChart(data);
    }

    // Analyze plant health based on sensor data
    function analyzePlantHealth(data) {
        if (data.temperature < 18 || data.temperature > 30) return "⚠️ Warning: Temperature out of range!";
        if (data.humidity < 40 || data.humidity > 70) return "⚠️ Warning: Humidity out of range!";
        if (data.light < 200) return "⚠️ Warning: Low light intensity!";
        return "✅ The plant is healthy.";
    }

    // Append messages to the chatbox (if you still want a log of the health status or errors)
    function appendToChatbox(message) {
        chatbox.value += `${message}\n\n`;
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    // Handle user input via Enter key (removed ChatGPT functionality)
    userInput.addEventListener("keydown", async (event) => {
        if (event.key === "Enter") {
            const userMessage = userInput.value.trim();
            if (!userMessage) return;

            appendToChatbox("You: " + userMessage);
            userInput.value = ""; // Clear the input field
        }
    });

    // Initialize the chart
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

    // Update chart with new data
    function updateChart(data) {
        const chart = window.myChart;
        const now = new Date().toLocaleTimeString();
        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(data.temperature);
        chart.data.datasets[1].data.push(data.humidity);
        chart.data.datasets[2].data.push(data.light);

        // Keep only the latest 20 data points
        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets.forEach(dataset => dataset.data.shift());
        }

        chart.update();
    }
});
