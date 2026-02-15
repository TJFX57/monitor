function captureImage() {
    fetch('/capture_image_api', { method: 'POST' })
        .then(response => {
            if (response.ok) {
                // Refresh just the image by adding a timestamp to bust cache
                document.getElementById('captured-image').src = '/get_image?t=' + Date.now();
            }
        })
        .catch(error => console.error('Error:', error));
}