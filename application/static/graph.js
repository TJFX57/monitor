const temperatureChart = document.getElementById('temperature-chart');
const pressureChart = document.getElementById('pressure-chart');
const humidityChart = document.getElementById('humidity-chart');
const lightChart = document.getElementById('light-chart');

Chart.defaults.color = 'lightgrey';
Chart.defaults.borderColor = 'lightslategray';
Chart.defaults.elements.point.pointStyle = false;
Chart.defaults.plugins.legend.display = false;

// ---------- helpers ----------

function pushData(chart, value, maxPoints = 1440) {
    chart.data.datasets[0].data.push(value);

    if (chart.data.datasets[0].data.length > maxPoints) {
        chart.data.datasets[0].data.shift();
    }
}

function pushLabelToAll(label, maxPoints = 1440) {
    const charts = [
        temperatureChartInstance,
        pressureChartInstance,
        humidityChartInstance,
        lightChartInstance
    ];

    charts.forEach(chart => {
        chart.data.labels.push(label);

        if (chart.data.labels.length > maxPoints) {
            chart.data.labels.shift();
        }
    });
}

// ---------- live updates ----------

async function liveUpdateCharts() {
    try {
        const res = await fetch('/latest');
        const data = await res.json();

        const lastLabel = temperatureChartInstance.data.labels.at(-1);

        if (data.time !== lastLabel) {

            // update shared timeline
            pushLabelToAll(data.time);

            // update datasets
            pushData(temperatureChartInstance, data.temperature);
            pushData(pressureChartInstance, data.pressure);
            pushData(humidityChartInstance, data.humidity);
            pushData(lightChartInstance, data.light);

            // redraw charts
            [
                temperatureChartInstance,
                pressureChartInstance,
                humidityChartInstance,
                lightChartInstance
            ].forEach(chart => chart.update('none'));
        }

        // ✅ update displayed measurements
        document.getElementById('temperature').textContent =
            `Currently: ${data.temperature}°C`;

        document.getElementById('pressure').textContent =
            `Currently: ${data.pressure}HPa`;

        document.getElementById('humidity').textContent =
            `Currently: ${data.humidity}RH`;

        document.getElementById('light').textContent =
            `Currently: ${data.light}lx`;

    } catch (err) {
        console.error("Live update failed:", err);
    }
}

// update every 10 seconds
setInterval(liveUpdateCharts, 10000);

// ---------- chart creation ----------

const temperatureChartInstance = new Chart(temperatureChart, {
    type: 'line',
    data: {
        labels: [...timeData],
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
        labels: [...timeData],
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
        labels: [...timeData],
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
        labels: [...timeData],
        datasets: [{
            data: lightData,
            tension: 0.4,
            cubicInterpolationMode: 'monotone'
        }]
    }
});
