// ---------- live updates ----------

async function updateLiveMeasurements() {
    try {
        const res = await fetch('/status');
        const data = await res.json();

        // update displayed sensor measurements
        document.getElementById('temperature').textContent =
            `Currently: ${data.temperature}°C`;
        document.getElementById('pressure').textContent =
            `Currently: ${data.pressure}HPa`;
        document.getElementById('humidity').textContent =
            `Currently: ${data.humidity}RH`;
        document.getElementById('light').textContent =
            `Currently: ${data.light}lx`;

        // update WiFi
        document.getElementById('wifi-quality').textContent =
            `${data.wifi_quality}/70`;
        document.getElementById('wifi-strength').textContent =
            `${data.wifi_strength}dBm`;

    } catch (err) {
        console.error("Live measurements update failed:", err);
    }
}

// run every 10 seconds
setInterval(updateLiveMeasurements, 10000);

// ---------- image capture ----------

function captureImage() {
    fetch('/capture_image', { method: 'POST' })
        .then(response => {
            if (!response.ok) throw new Error('Capture failed');
            return response.json(); // reads { "image_captured": "..." }
        })
        .then(data => {
            if (data.status === 'success') {
                // Refresh the image immediately
                document.getElementById('captured-image').src = '/get_image?t=' + Date.now();
                
                // Update the timestamp text
                const timeLabel = document.getElementById('image-captured');
                if (timeLabel) {
                    timeLabel.textContent = 'Captured: ' + data.image_captured;
                }
            }
        })
        .catch(error => console.error('Error:', error));
}
