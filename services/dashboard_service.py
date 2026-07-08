from models import ContainerLog, ContainerMetric
from services.docker_service import docker_health

def dashboard_summary():

    running = ContainerLog.query.filter_by(
        status="running"
    ).count()

    stopped = ContainerLog.query.filter_by(
        status="stopped"
    ).count()

    deployments = ContainerLog.query.count()

    docker = docker_health()

    return {
        "docker": "connected" if docker else "disconnected",
        "running": running,
        "stopped": stopped,
        "deployments": deployments
    }

def live_containers():

    running = ContainerLog.query.filter_by(
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

def deployment_history():

    containers = ContainerLog.query.order_by(
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

def container_metrics(container_id):
    metrics = (
    ContainerMetric.query
    .filter_by(container_log_id=container_id)
    .order_by(ContainerMetric.recorded_at.asc())
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

def latest_metrics():

    running = ContainerLog.query.filter_by(
        status="running"
    ).all()

    response = []

    for container in running:

        latest = (
            ContainerMetric.query
            .filter_by(container_log_id=container.id)
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