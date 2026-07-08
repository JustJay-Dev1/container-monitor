// =========================================
// Wait until HTML is fully loaded
// =========================================

document.addEventListener("DOMContentLoaded", () => {

    // ============================
    // CPU Chart
    // ============================

    const cpuChart = new Chart(
        document.getElementById("cpuChart"),
        {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "CPU Usage (%)",
                        data: [],
                        borderColor: "#3b82f6",
                        backgroundColor: "rgba(59,130,246,.2)",
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        }
    );

    // ============================
    // Memory Chart
    // ============================

    const memoryChart = new Chart(
        document.getElementById("memoryChart"),
        {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "Memory Usage (MB)",
                        data: [],
                        borderColor: "#22c55e",
                        backgroundColor: "rgba(34,197,94,.2)",
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        }
    );

    // =====================================
    // Dashboard Cards
    // =====================================

    async function loadDashboard() {

        const response = await fetch("/dashboard");
        const data = await response.json();

        document.getElementById("running-count").textContent = data.running;
        document.getElementById("stopped-count").textContent = data.stopped;
        document.getElementById("deployment-count").textContent = data.deployments;

        document.getElementById("docker-status").innerHTML =
            data.docker === "connected"
                ? '<span class="running">🟢 Connected</span>'
                : '<span class="stopped">🔴 Disconnected</span>';
    }

    // =====================================
    // Containers
    // =====================================

    async function loadContainers() {

        const response = await fetch("/containers/live");
        const containers = await response.json();

        const tbody = document.querySelector("#container-table tbody");

        tbody.innerHTML = "";

        containers.forEach(container => {

            tbody.innerHTML += `
                <tr>

                    <td>${container.name}</td>

                    <td>${container.image}</td>

                    <td>${container.cpu.toFixed(2)} %</td>

                    <td>${container.memory.toFixed(2)} MB</td>

                    <td>${container.network_rx.toFixed(2)} MB</td>

                    <td>${container.disk_read.toFixed(2)} MB</td>

                    <td>

                        ${
                            container.status === "running"

                            ?

                            '<span class="running">🟢 Running</span>'

                            :

                            '<span class="stopped">🔴 Stopped</span>'
                        }

                    </td>

                </tr>
            `;
        });

        if (containers.length > 0) {

            loadCharts(containers[0].id);

        }

    }

    // =====================================
    // History
    // =====================================

    async function loadHistory() {

        const response = await fetch("/history");
        const history = await response.json();

        const tbody = document.querySelector("#history-table tbody");

        tbody.innerHTML = "";

        history.forEach(container => {

            tbody.innerHTML += `

                <tr>

                    <td>${container.name}</td>

                    <td>${container.image}</td>

                    <td>${new Date(container.created_at).toLocaleString()}</td>

                    <td>

                        ${
                            container.stopped_at

                            ?

                            new Date(container.stopped_at).toLocaleString()

                            :

                            "-"
                        }

                    </td>

                    <td>${container.status}</td>

                </tr>

            `;

        });

    }

    // =====================================
    // Charts
    // =====================================

    async function loadCharts(containerId) {

        const response = await fetch(`/metrics/${containerId}`);

        const metrics = await response.json();

        const labels = [];
        const cpu = [];
        const memory = [];

        metrics.forEach(metric => {

            labels.push(
                new Date(metric.time).toLocaleTimeString()
            );

            cpu.push(metric.cpu);
            memory.push(metric.memory);

        });

        cpuChart.data.labels = labels;
        cpuChart.data.datasets[0].data = cpu;
        cpuChart.update();

        memoryChart.data.labels = labels;
        memoryChart.data.datasets[0].data = memory;
        memoryChart.update();

    }

    // =====================================
    // Refresh
    // =====================================

    async function refresh() {

        await loadDashboard();

        await loadContainers();

        await loadHistory();

    }

    refresh();

    setInterval(refresh, 5000);

});