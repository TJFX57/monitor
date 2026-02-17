const temperatureChart = document.getElementById('temperature-chart');
const pressureChart = document.getElementById('pressure-chart');
const humidityChart = document.getElementById('humidity-chart');
const lightChart = document.getElementById('light-chart');

// ------------------- Chart.js defaults -------------------
Chart.defaults.color = 'lightgrey';
Chart.defaults.borderColor = 'lightslategray';
Chart.defaults.elements.point.pointStyle = false;
Chart.defaults.plugins.legend.display = false;

// ------------------- helpers -------------------
function pushData(chart, value, maxPoints = 1440) {
    chart.data.datasets[0].data.push(value);
    if (chart.data.datasets[0].data.length > maxPoints) chart.data.datasets[0].data.shift();
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
        if (chart.data.labels.length > maxPoints) chart.data.labels.shift();
    });
}

function replaceChartData(data, range) {
    const charts = [
        [temperatureChartInstance, data.temperature],
        [pressureChartInstance, data.pressure],
        [humidityChartInstance, data.humidity],
        [lightChartInstance, data.light]
    ];

    charts.forEach(([chart, values]) => {
        chart.data.labels = [...data.time];
        chart.data.datasets[0].data = [...values];

        // Update x-axis label format dynamically based on range
        chart.options.scales.x.time.displayFormats.minute = getTimeDisplayFormat(range);

        chart.update();
    });
}

// Choose display format based on range
function getTimeDisplayFormat(range) {
    switch(range) {
        case '15m':
        case '1h': return 'HH:mm';
        case '6h':
        case '24h': return 'MMM D HH:mm';
        case '7d':
        case '30d': return 'MMM D';
        default: return 'HH:mm';
    }
}

// ------------------- live updates -------------------
async function liveUpdateCharts() {
    try {
        const res = await fetch('/latest');
        const data = await res.json();
        const lastLabel = temperatureChartInstance.data.labels.at(-1);

        if (data.time !== lastLabel) {
            pushLabelToAll(data.time);
            pushData(temperatureChartInstance, data.temperature);
            pushData(pressureChartInstance, data.pressure);
            pushData(humidityChartInstance, data.humidity);
            pushData(lightChartInstance, data.light);

            [
                temperatureChartInstance,
                pressureChartInstance,
                humidityChartInstance,
                lightChartInstance
            ].forEach(chart => chart.update('none'));
        }

    } catch (err) {
        console.error("Live update failed:", err);
    }
}

// Poll live data every minute (matches your 1-min logging)
setInterval(liveUpdateCharts, 60000);

// ------------------- timescale buttons -------------------
document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".timescale-btn");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const range = button.dataset.range;

            buttons.forEach(b => b.classList.remove("active"));
            button.classList.add("active");

            loadTimescale(range);
        });
    });
});

// ------------------- load historical data -------------------
async function loadTimescale(range) {
    try {
        const res = await fetch(`/data?range=${range}`);
        const data = await res.json();
        replaceChartData(data, range);
    } catch (err) {
        console.error("Failed to load timescale:", err);
    }
}

// ------------------- common Chart.js options -------------------
const commonOptions = {
    scales: {
        x: {
            type: 'time',
            time: {
                parser: 'YYYY-MM-DD HH:mm:ss.SSS',
                tooltipFormat: 'MMM D, HH:mm',
                displayFormats: {
                    millisecond: 'HH:mm:ss',
                    second: 'HH:mm:ss',
                    minute: 'HH:mm',
                    hour: 'MMM D HH:mm',
                    day: 'MMM D',
                    month: 'MMM YYYY'
                }
            },
            title: { display: true, text: 'Time' },
            ticks: { autoSkip: true, maxTicksLimit: 12, maxRotation: 45, minRotation: 0 }
        },
        y: { beginAtZero: false }
    },
    plugins: { legend: { display: false } }
};

// ------------------- create charts -------------------
function createChart(element, dataSet, yLabel) {
    return new Chart(element, {
        type: 'line',
        data: { labels: [...timeData], datasets: [{ data: dataSet, tension: 0.4, cubicInterpolationMode: 'monotone' }] },
        options: JSON.parse(JSON.stringify(commonOptions))
    });
}

const temperatureChartInstance = createChart(temperatureChart, temperatureData, 'Temperature (°C)');
const pressureChartInstance    = createChart(pressureChart, pressureData, 'Pressure (hPa)');
const humidityChartInstance    = createChart(humidityChart, humidityData, 'Humidity (%)');
const lightChartInstance       = createChart(lightChart, lightData, 'Light (lx)');
