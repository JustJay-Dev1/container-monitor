
import os
from dotenv import load_dotenv
from services.docker_service import (
    deploy_container,
    list_containers,
    stop_all_containers,
    docker_status,
    container_stats,
    docker_health
)
from database import db
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/health")
def health():

    docker_ok = docker_health()

    try:
        db.session.execute(db.text("SELECT 1"))
        database_ok = True
    except Exception:
        database_ok = False

    overall = docker_ok and database_ok

    return jsonify({
        "status": "healthy" if overall else "unhealthy",
        "docker": "connected" if docker_ok else "disconnected",
        "database": "connected" if database_ok else "disconnected"
    }), 200 if overall else 503

@app.route("/status")
def status():

    count = docker_status()

    return jsonify({
        "docker": "connected",
        "containers": count
    })

@app.route("/deploy", methods=["POST"])
def deploy():

    data = request.get_json()

    if not data or "image" not in data:
        return jsonify({
            "error": "image is required"
        }), 400

    result = deploy_container(data["image"])

    if not result["success"]:
        return jsonify({
            "error": result["error"]
        }), 500

    return jsonify({
        "message": "Container deployed",
        "container_id": result["container_id"]
    })

@app.route("/containers")
def containers():

    return jsonify({
        "containers": list_containers()
    })

@app.route("/stop", methods=["POST"])
def stop():

    ids = stop_all_containers()

    if not ids:
        return jsonify({
            "message": "No containers running"
        })

    return jsonify({
        "message": "Containers stopped",
        "stopped_containers": ids
    })

@app.route("/container-stats/<container_id>")
def stats(container_id):

    data = container_stats(container_id)

    if data is None:
        return jsonify({
            "error": "Container not found"
        }),404

    return jsonify({
        "container": data["Name"],
        "cpu": data["CPUPerc"],
        "memory": data["MemUsage"],
        "memory_percent": data["MemPerc"],
        "network": data["NetIO"]
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)