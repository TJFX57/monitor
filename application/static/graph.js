const temperatureChart = document.getElementById('temperature-chart');
const pressureChart = document.getElementById('pressure-chart');
const humidityChart = document.getElementById('humidity-chart');
const lightChart = document.getElementById('light-chart');

Chart.defaults.color = 'lightgrey';
Chart.defaults.borderColor = 'lightslategray';
Chart.defaults.elements.point.pointStyle = false;
Chart.defaults.plugins.legend.display = false;

function pushAndScroll(chart, label, value, maxPoints = 1440) {
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);

    if (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update();
}

async function updateCharts() {
    try {
        const res = await fetch('/latest');
        const data = await res.json();

        pushAndScroll(temperatureChartInstance, data.time, data.temperature);
        pushAndScroll(pressureChartInstance, data.time, data.pressure);
        pushAndScroll(humidityChartInstance, data.time, data.humidity);
        pushAndScroll(lightChartInstance, data.time, data.light);

    } catch (err) {
        console.error("Live update failed:", err);
    }
}

// update every 10 seconds
setInterval(updateCharts, 10000);

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
