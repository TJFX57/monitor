const temperatureChart = document.getElementById('temperature-chart');
const pressureChart = document.getElementById('pressure-chart');
const humidityChart = document.getElementById('humidity-chart');
const lightChart = document.getElementById('light-chart');

Chart.defaults.color = 'lightgrey';
Chart.defaults.borderColor = 'lightslategray';
Chart.defaults.elements.point.pointStyle = false;
Chart.defaults.plugins.legend.display = false;

// Moving average function to smooth data
function movingAverage(data, windowSize = 60) {
	return data.map((_, i) => {
		const start = Math.max(0, i - Math.floor(windowSize / 2));
		const end = Math.min(data.length, i + Math.ceil(windowSize / 2));
		const subset = data.slice(start, end);
		return subset.reduce((a, b) => a + b) / subset.length;
	});
}

// Apply moving average to all datasets
const smoothedTemperatureData = movingAverage(temperatureData);
const smoothedPressureData = movingAverage(pressureData);
const smoothedHumidityData = movingAverage(humidityData);
const smoothedLightData = movingAverage(lightData, 120);

const temperatureChartInstance = new Chart(temperatureChart, {
	type: 'line',
	data: {
		labels: timeData,
		datasets: [{
			data: smoothedTemperatureData,
			tension: 0.4,
			cubicInterpolationMode: 'monotone'
		}]
	}
});

const pressureChartInstance = new Chart(pressureChart, {
	type: 'line',
	data: {
		labels: timeData,
		datasets: [{
			data: smoothedPressureData,
			tension: 0.4,
			cubicInterpolationMode: 'monotone'
		}]
	}
});

const humidityChartInstance = new Chart(humidityChart, {
	type: 'line',
	data: {
		labels: timeData,
		datasets: [{
			data: smoothedHumidityData,
			tension: 0.4,
			cubicInterpolationMode: 'monotone'

		}]
	}
});

const lightChartInstance = new Chart(lightChart, {
	type: 'line',
	data: {
		labels: timeData,
		datasets: [{
			data: smoothedLightData,
			tension: 0.4,
			cubicInterpolationMode: 'monotone'

		}]
	}
});
