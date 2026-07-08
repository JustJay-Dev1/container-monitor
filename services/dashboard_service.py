from models import ContainerLog, ContainerMetric
from services.docker_service import docker_health

def dashboard_summary():                                                # gets the summary count of all the containers

    running = ContainerLog.query.filter_by(                             # runs "SELECT COUNT(*) FROM container_log WHERE status = 'running';" query on container_logs to get count of running containers
        status="running"
    ).count()

    stopped = ContainerLog.query.filter_by(                             # runs "SELECT COUNT(*) FROM container_log WHERE status = 'stopped';" query on container_logs to get count of stopped container  
        status="stopped"
    ).count()

    deployments = ContainerLog.query.count()                            # runs "SELECT COUNT(*) FROM monitoring-db.container_log;" query on container_log to get total rows i.e. number of deployments

    docker = docker_health()                                            # uses "docker info" command to fetch docker status

    return {
        "docker": "connected" if docker else "disconnected",
        "running": running,
        "stopped": stopped,
        "deployments": deployments
    }

def live_containers():                                                  # shows all the running containers on the dashboard

    running = ContainerLog.query.filter_by(                             # runs "SELECT * FROM container_log WHERE status = 'running';" query on container_logs to get all the running containers
        status="running"                                                
    ).all()

    containers = []

    for container in running:

        if not container.metrics:
            continue

        latest = container.metrics[-1]

        containers.append({
            "id": container.id,
            "name": container.container_name,
            "image": container.image,
            "status": container.status,
            "cpu": latest.cpu_usage,
            "memory": latest.memory_usage,
            "network_rx": latest.network_rx,
            "network_tx": latest.network_tx,
            "disk_read": latest.disk_read,
            "disk_write": latest.disk_write
        })

    return containers

def deployment_history():                                               # shows all the stopped containers on the dashboard

    containers = ContainerLog.query.order_by(                           # runs "SELECT * FROM container_logs ORDER BY created_at DESC;" on contaier_log and shows the latest created container first i.e in descending order
        ContainerLog.created_at.desc()
    ).all()

    history = []

    for container in containers:

        history.append({

            "name": container.container_name,

            "image": container.image,

            "status": container.status,

            "created_at": container.created_at,

            "stopped_at": container.stopped_at

        })

    return history

def container_metrics(container_id):                                    # shows the history of a specific container buy taking container_id as input, from container_metrics table
    metrics = (
    ContainerMetric.query                                               # runs "SELECT * FROM container_metric WHERE container_log_id = :container_id ORDER BY recorded_at ASC;" on container metrics
    .filter_by(container_log_id=container_id)
    .order_by(ContainerMetric.recorded_at.asc())                        # finds and saves the info of the specific container in ascending order 
    .all()
    )
    history = []

    for metric in metrics:

        history.append({

            "time": metric.recorded_at,

            "cpu": metric.cpu_usage,

            "memory": metric.memory_usage,

            "network_rx": metric.network_rx,

            "network_tx": metric.network_tx,

            "disk_read": metric.disk_read,

            "disk_write": metric.disk_write

        })

    return history

def latest_metrics():                                                   # shows the metric data of the latest running container

    running = ContainerLog.query.filter_by(                             # runs "SELECT * FROM container_log WHERE status = 'running';" 
        status="running"
    ).all()

    response = []

    for container in running:

        latest = (
            ContainerMetric.query                                       # runs "SELECT * FROM container_metric WHERE container_log_id = :container_id ORDER BY recorded_at DESC LIMIT 1;" on container_metrics
            .filter_by(container_log_id=container.id)                   # used first() to get the top container ie. newly inserted in the container_metrics
            .order_by(ContainerMetric.recorded_at.desc())
            .first()
        )

        if latest is None:
            continue

        response.append({

            "container_log_id": container.id,

            "container_name": container.container_name,

            "cpu": latest.cpu_usage,

            "memory": latest.memory_usage,

            "network_rx": latest.network_rx,

            "network_tx": latest.network_tx,

            "disk_read": latest.disk_read,

            "disk_write": latest.disk_write,

            "recorded_at": latest.recorded_at.isoformat()

        })

    return response