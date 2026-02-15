const temperatureChart = document.getElementById('temperature-chart');
const pressureChart = document.getElementById('pressure-chart');
const humidityChart = document.getElementById('humidity-chart');
const lightChart = document.getElementById('light-chart');

Chart.defaults.color = 'lightgrey';
Chart.defaults.borderColor = 'lightslategray';
Chart.defaults.elements.point.pointStyle = false;
Chart.defaults.plugins.legend.display = false;

const temperatureChartInstance = new Chart(temperatureChart, {
	type: 'line',
	data: {
		labels: timeData,
		datasets: [{
			data: temperatureData,
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
			data: pressureData,
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
			data: humidityData,
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
			data: lightData,
			tension: 0.4,
			cubicInterpolationMode: 'monotone'

		}]
	}
});
