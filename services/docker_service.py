import subprocess
import json
from datetime import datetime

from database import db
from models import ContainerLog

def docker(command):
    return subprocess.run(
        ["docker"] + command,
        capture_output=True,
        text=True
    )

def inspect(container_id):

    result = docker([
        "inspect",
        container_id
    ])

    if result.returncode != 0:
        return None

    return json.loads(result.stdout)[0]

def docker_health():

    result = docker(["info"])

    return result.returncode == 0

def deploy_container(image):

    result = docker(["run", "-d", image])

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip()
        }

    container_id = result.stdout.strip()

    info = inspect(container_id)

    log = ContainerLog(
        container_id=container_id,
        container_name=info["Name"].lstrip("/"),
        image=info["Config"]["Image"],
        status=info["State"]["Status"],
        created_at=datetime.now()
    )

    db.session.add(log)
    db.session.commit()

    return {
        "success": True,
        "container_id": container_id
    }

def list_containers():

    result = docker([
        "ps",
        "--format",
        "{{.Names}}"
    ])

    return result.stdout.splitlines()


def stop_all_containers():

    running = ContainerLog.query.filter_by(
        status="running"
    ).all()

    if not running:
        return []

    stopped_ids = []

    for container in running:

        result = docker(["stop", container.container_id])

        if result.returncode == 0:

            container.status = "stopped"
            container.stopped_at = datetime.now()

            stopped_ids.append(container.container_id)

    db.session.commit()

    return stopped_ids

def docker_status():

    result = docker([
        "ps",
        "-q"
    ])

    return len(result.stdout.splitlines())


def container_stats(container_id):

    result = docker([
        "stats",
        container_id,
        "--no-stream",
        "--format",
        "{{json .}}"
    ])

    if result.returncode != 0:
        return None

    return json.loads(result.stdout.strip())