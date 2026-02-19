document.addEventListener("DOMContentLoaded", () => {

    // ---------- canvas elements ----------
    const temperatureCanvas = document.getElementById('temperature-chart');
    const pressureCanvas = document.getElementById('pressure-chart');
    const humidityCanvas = document.getElementById('humidity-chart');
    const lightCanvas = document.getElementById('light-chart');

    // ---------- global chart styling ----------
    Chart.defaults.color = 'lightgrey';
    Chart.defaults.borderColor = 'lightslategray';
    Chart.defaults.elements.point.pointStyle = false;
    Chart.defaults.plugins.legend.display = false;

    // ---------- chart creation ----------
    const temperatureChartInstance = new Chart(temperatureCanvas, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], tension: 0.4, cubicInterpolationMode: 'monotone' }] }
    });

    const pressureChartInstance = new Chart(pressureCanvas, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], tension: 0.4, cubicInterpolationMode: 'monotone' }] }
    });

    const humidityChartInstance = new Chart(humidityCanvas, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], tension: 0.4, cubicInterpolationMode: 'monotone' }] }
    });

    const lightChartInstance = new Chart(lightCanvas, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], tension: 0.4, cubicInterpolationMode: 'monotone' }] }
    });

    const charts = [
        temperatureChartInstance,
        pressureChartInstance,
        humidityChartInstance,
        lightChartInstance
    ];

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
        const mapping = [
            [temperatureChartInstance, data.temperature],
            [pressureChartInstance, data.pressure],
            [humidityChartInstance, data.humidity],
            [lightChartInstance, data.light]
        ];

        mapping.forEach(([chart, values]) => {
            chart.data.labels = [...data.time];
            chart.data.datasets[0].data = [...values];
            chart.update();
        });
    }

    // ---------- timescale buttons ----------
    const buttons = document.querySelectorAll(".timescale-btn");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const range = button.dataset.range;

            // remove active from all buttons, add to clicked
            buttons.forEach(b => b.classList.remove("active"));
            button.classList.add("active");

            loadTimescale(range);
        });
    });

    // ---------- initial load ----------
    const defaultRange = "1h";
    const defaultButton = document.querySelector(`[data-range="${defaultRange}"]`);

    if (defaultButton) {
        buttons.forEach(b => b.classList.remove("active")); // clear any others
        defaultButton.classList.add("active"); // highlight default immediately
    }

    loadTimescale(defaultRange);          // load initial data
    setInterval(liveUpdateCharts, 10000); // start live updates

    // ---------- fetch initial data ----------
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
            if (!res.ok) return; // No data yet

            const data = await res.json();
            const lastLabel = temperatureChartInstance.data.labels.at(-1);

            if (!lastLabel || data.time !== lastLabel) {
                charts.forEach((chart, i) => {
                    const values = [data.temperature, data.pressure, data.humidity, data.light];
                    pushLiveData(chart, values[i], data.time);
                });

                charts.forEach(chart => chart.update('none'));
            }

        } catch (err) {
            console.error("Live update failed:", err);
        }
    }

});
