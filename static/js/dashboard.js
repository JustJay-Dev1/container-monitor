async function loadDashboard(){
    const response = await fetch("/dashboard");

    const data = await response.json();

    document.getElementById("running-count").textContent =
        data.running;

    document.getElementById("stopped-count").textContent =
        data.stopped;

    document.getElementById("deployment-count").textContent =
        data.deployments;

    document.getElementById("docker-status").textContent =
        data.docker;
}

async function loadContainers(){

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

            <td>${container.status}</td>

        </tr>

        `;

    });

}

async function loadHistory(){

    const response = await fetch("/history");

    const history = await response.json();

    const tbody = document.querySelector("#history-table tbody");

    tbody.innerHTML = "";

    history.forEach(container=>{

        tbody.innerHTML += `

        <tr>

            <td>${container.name}</td>

            <td>${container.image}</td>

            <td>${container.created_at}</td>

            <td>${container.stopped_at ?? "-"}</td>

            <td>${container.status}</td>

        </tr>

        `;

    });

}

function refresh(){

    loadDashboard();

    loadContainers();

    loadHistory();

}

refresh();

setInterval(refresh,5000);
