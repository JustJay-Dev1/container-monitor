import subprocess
import os
from datetime import datetime
from dotenv import load_dotenv

from database import db
from models import ContainerLog
from flask import Flask, jsonify, request, json

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/health")
def healthcheck():
    return jsonify({
        "status": "healthy",
        "service": "mini-orchestrator"
    })

@app.route("/status")
def status():
    result = subprocess.run(
        ["docker", "ps", "-q"],
        capture_output=True,
        text=True
    )
    # Safely counts containers even if output is empty
    count = len(result.stdout.splitlines())
    return jsonify({
        "docker": "connected",
        "containers": count
    })

@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.json
    if not data or "image" not in data:
        return jsonify({"error": "image is required"}), 400
        
    image = data["image"]
    result = subprocess.run(
        ["docker", "run", "-d", image],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return jsonify({"error": "Failed to deploy image", "details": result.stderr.strip()}), 500
    container_id = result.stdout.strip()

    inspect = subprocess.run(
    ["docker", "inspect", container_id],
    capture_output=True,
    text=True
    )

    info = json.loads(inspect.stdout)[0]
    log = ContainerLog(
    container_id=container_id,
    container_name=info["Name"].lstrip("/"),
    image=info["Config"]["Image"],
    status=info["State"]["Status"],
    created_at=datetime.now(),
    cpu_usage=0.0,
    memory_usage=0.0
    )
    return jsonify({
        "container_id": result.stdout.strip()
    })

@app.route("/containers")
def dockerps():
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    # OPTIMIZATION: Returns a clean list ['worker1', 'worker2'] instead of raw text with \n
    return jsonify({
        "containers": result.stdout.splitlines()
    })

@app.route("/stop", methods=["POST"])
def dockerstop():
    list_cont = subprocess.run(
        ["docker", "container", "ls", "-q"],
        capture_output=True,
        text=True
    )

    ids = list_cont.stdout.splitlines()
    
    # OPTIMIZATION: Check if empty BEFORE running the docker stop command to avoid a crash
    if not ids:
        return jsonify({
            "message": "no containers to be removed"
        }), 200

    subprocess.run(
        ["docker", "stop"] + ids,
        capture_output=True,
        text=True
    )

    return jsonify({
        "message": "successfully stopped containers",
        "stopped_containers": ids
    }), 200

@app.route("/restart", methods=["POST"])
def restart():
    data = request.json
    if not data or "container_id" not in data:
        return jsonify({"error": "container_id is required"}), 400

    container_id = data["container_id"]
    result = subprocess.run(
        ["docker", "restart", container_id],
        capture_output=True,
        text=True
    )
    
    # OPTIMIZATION: Handle non-existent container IDs
    if result.returncode != 0:
        return jsonify({"error": f"Container '{container_id}' not found"}), 404

    return jsonify({
        "message": "container restarted",
        "container_id": container_id
    })

@app.route("/container/<container_id>")
def inspect_container(container_id):
    result = subprocess.run(
        ["docker", "inspect", container_id],
        capture_output=True,
        text=True
    )
    
    # OPTIMIZATION: Check if container exists before parsing JSON
    if result.returncode != 0:
        return jsonify({"error": f"Container '{container_id}' not found"}), 404

    data = json.loads(result.stdout)
    container_info = data[0]
    
    response = {
        "name": container_info["Name"].lstrip("/"),
        "status": container_info["State"]["Status"],
        "image": container_info["Config"]["Image"]
    }
    return jsonify(response)

@app.route("/container-stats/<container_id>")
def container_stats(container_id):
    result = subprocess.run(
        [
            "docker",
            "stats",
            container_id,
            "--no-stream",
            "--format",
            "{{json .}}"
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return jsonify({"error": f"Could not fetch stats for container '{container_id}'"}), 404

    data = json.loads(result.stdout.strip())
    response = {
        "container": data["Name"],
        "cpu": data["CPUPerc"],
        "memory": data["MemUsage"],
        "memory_percent": data["MemPerc"],
        "network": data["NetIO"]
    }
    return jsonify(response)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)