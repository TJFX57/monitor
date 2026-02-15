function captureImage() {
    fetch('/capture_image', { method: 'POST' })
        .then(response => {
            if (!response.ok) throw new Error('Capture failed');
            return response.json(); // This reads the { "image_captured": "..." } data
        })
        .then(data => {
            if (data.status === 'success') {
                // Refresh the image
                document.getElementById('captured-image').src = '/get_image?t=' + Date.now();
                
                // Update the timestamp text
                const timeLabel = document.getElementById('image-captured');
                if (timeLabel) {
                    timeLabel.textContent = 'Image captured: ' + data.image_captured;
                }
            }
        })
        .catch(error => console.error('Error:', error));
}
