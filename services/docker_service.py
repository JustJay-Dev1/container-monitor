import subprocess
import json

def docker(command):
    return subprocess.run(
        ["docker"] + command,
        capture_output=True,
        text=True
    )

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

    return {
        "success": True,
        "container_id": result.stdout.strip()
    }


def list_containers():

    result = docker([
        "ps",
        "--format",
        "{{.Names}}"
    ])

    return result.stdout.splitlines()


def stop_all_containers():

    result = docker([
        "container",
        "ls",
        "-q"
    ])

    ids = result.stdout.splitlines()

    if not ids:
        return []

    docker(["stop"] + ids)

    return ids


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