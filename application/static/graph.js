document.addEventListener("DOMContentLoaded", () => {

    // ---------- canvas elements ----------
    const temperatureCanvas = document.getElementById('temperature-chart');
    const pressureCanvas = document.getElementById('pressure-chart');
    const humidityCanvas = document.getElementById('humidity-chart');
    const lightCanvas = document.getElementById('light-chart');

    // ---------- track active range ----------
    let currentRange = "1h";

    // ---------- global chart styling ----------
    Chart.defaults.color = 'lightgrey';
    Chart.defaults.borderColor = 'lightslategray';
    Chart.defaults.elements.point.pointStyle = false;
    Chart.defaults.plugins.legend.display = false;

    // ---------- chart creation ----------
    function createChart(canvas) {
        return new Chart(canvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    tension: 0.4,
                    cubicInterpolationMode: 'monotone'
                }]
            }
        });
    }

    const charts = {
        temperature: createChart(temperatureCanvas),
        pressure: createChart(pressureCanvas),
        humidity: createChart(humidityCanvas),
        light: createChart(lightCanvas)
    };

    const chartKeys = Object.keys(charts);

    // ---------- statistics ----------
    function calculateStats(values) {
        if (!values.length) {
            return { min: '-', max: '-', avg: '-' };
        }

        const min = Math.min(...values);
        const max = Math.max(...values);
        const avg = values.reduce((a, b) => a + b, 0) / values.length;

        return {
            min: min.toFixed(1),
            max: max.toFixed(1),
            avg: avg.toFixed(1)
        };
    }

    function updateStats(key, values) {
        const stats = calculateStats(values);

        document.getElementById(`${key}-min`).textContent = stats.min;
        document.getElementById(`${key}-max`).textContent = stats.max;
        document.getElementById(`${key}-avg`).textContent = stats.avg;
    }

    function updateAllStats() {
        chartKeys.forEach(key => {
            const values = charts[key].data.datasets[0].data;
            updateStats(key, values);
        });
    }

    // ---------- helpers ----------
    function pushLiveData(chart, value, label, maxPoints = 60) {
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);

        while (chart.data.labels.length > maxPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
    }

    function replaceChartData(data) {
        chartKeys.forEach(key => {
            charts[key].data.labels = [...data.time];
            charts[key].data.datasets[0].data = [...data[key]];
            charts[key].update('none');
        });

        updateAllStats();
    }

    // ---------- timescale buttons ----------
    const buttons = document.querySelectorAll(".timescale-btn");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const range = button.dataset.range;

            currentRange = range;   // Track selected range

            buttons.forEach(b => b.classList.remove("active"));
            button.classList.add("active");

            loadTimescale(range);
        });
    });

    // ---------- initial load ----------
    const defaultRange = "1h";
    currentRange = defaultRange;

    const defaultButton = document.querySelector(`[data-range="${defaultRange}"]`);

    if (defaultButton) {
        buttons.forEach(b => b.classList.remove("active"));
        defaultButton.classList.add("active");
    }

    loadTimescale(defaultRange);

    // Run live updates every 10 seconds
    setInterval(liveUpdateCharts, 10000);

    // ---------- fetch timescale data ----------
    async function loadTimescale(range) {
        try {
            const res = await fetch(`/data?range=${range}`);
            if (!res.ok) return;

            const data = await res.json();
            replaceChartData(data);

        } catch (err) {
            console.error("Failed to load timescale:", err);
        }
    }

    // ---------- live updates ----------
    async function liveUpdateCharts() {

        try {
            const res = await fetch('/latest');
            if (!res.ok) return;

            const data = await res.json();

            const lastLabel = charts.temperature.data.labels.at(-1);

            if (!lastLabel || data.time !== lastLabel) {

                chartKeys.forEach(key => {
                    pushLiveData(charts[key], data[key], data.time);
                });

                chartKeys.forEach(key => {
                    charts[key].update('none');
                });

                updateAllStats();
            }

        } catch (err) {
            console.error("Live update failed:", err);
        }
    }

});