import subprocess
import json
from datetime import datetime

from database import db
from models import ContainerLog

"""  <!-- ===================== -->
    <!-- Docker Helper Function -->
    <!-- ===================== -->"""
def docker(command):
    return subprocess.run(                              # uses subprocess module single time to execut commands on terminal 
        ["docker"] + command,
        capture_output=True,
        text=True
    )

def inspect(container_id):                              # runs "docker inspect container_id" command to fetch info about specific container

    result = docker([
        "inspect",
        container_id
    ])

    if result.returncode != 0:
        return None

    return json.loads(result.stdout)[0]

def docker_health():                                    # runs "docker info" command to fetch docker status

    result = docker(["info"])

    return result.returncode == 0

def deploy_container(image):                            # runs "docker run image" command to deploy a container image. -d specifies detached mode

    result = docker(["run", "-d", image])

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip()
        }

    container_id = result.stdout.strip()

    info = inspect(container_id)                        # runs "docker inspect" to inspect deployed container

    log = ContainerLog(
        container_id=container_id,
        container_name=info["Name"].lstrip("/"),        # saves specific info about deployed container
        image=info["Config"]["Image"],
        status=info["State"]["Status"],
        created_at=datetime.now()
    )

    db.session.add(log)                                 # inserts the log into database i.e in container_log table
    db.session.commit()

    return {
        "success": True,
        "container_id": container_id
    }

def list_containers():                                  # runs "docker ps --format {{.Name}}" command which gives names of all the running containers

    result = docker([
        "ps",
        "--format",
        "{{.Names}}"
    ])

    return result.stdout.splitlines()


def stop_all_containers():                              # stops all the running containers by using "docker stop container_id" command

    running = ContainerLog.query.filter_by(             # runs "SELECT * FROM container_log WHERE status = 'running';" query on container_logs to get all running containers
        status="running"
    ).all()

    if not running:
        return []

    stopped_ids = []

    for container in running:

        result = docker(["stop", container.container_id])# fetches container ids from container_log table 

        if result.returncode == 0:

            container.status = "stopped"
            container.stopped_at = datetime.now()

            stopped_ids.append(container.container_id)

    db.session.commit()                                 # stops the containers adds the stopping time to container_logs table

    return stopped_ids

def docker_status():                                    # runs "docker ps -q" command and returns the number of containers running

    result = docker([
        "ps",
        "-q"
    ])

    return len(result.stdout.splitlines())


def container_stats(container_id):                      # runs "docker stats container_id --no-stream --format "{{json .}}"", get json output of docker stats 

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