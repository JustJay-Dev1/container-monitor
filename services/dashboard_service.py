from models import ContainerLog
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