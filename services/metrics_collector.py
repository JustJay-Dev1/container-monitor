import os
import json
import re
import threading
import time

from datetime import datetime

from database import db
from models import ContainerLog, ContainerMetric
from services.docker_service import docker
from dotenv import load_dotenv
load_dotenv()

METRICS_INTERVAL = int(os.getenv("METRICS_INTERVAL", 5))

def parse_cpu(cpu):
    return float(cpu.replace("%", ""))

def convert_to_mb(value):

    value = value.strip()

    if value.startswith("0B"):
        return 0.0

    number = float(re.findall(r"[\d.]+", value)[0])

    if "GiB" in value or "GB" in value:
        return number * 1024

    elif "MiB" in value or "MB" in value:
        return number

    elif "KiB" in value or "kB" in value:
        return number / 1024

    elif value.endswith("B"):
        return number / (1024 * 1024)

    return number

def parse_memory(memory):

    used = memory.split("/")[0].strip()

    return convert_to_mb(used)

def parse_network(network):

    rx, tx = network.split("/")

    return (
        convert_to_mb(rx.strip()),
        convert_to_mb(tx.strip())
    )

def parse_disk(disk):

    read, write = disk.split("/")

    return (
        convert_to_mb(read.strip()),
        convert_to_mb(write.strip())
    )

def collect_metrics():

    running = ContainerLog.query.filter_by(
        status="running"
    ).all()

    if not running:
        return

    running_map = {
        c.container_id: c
        for c in running
    }

    result = docker([
        "stats",
        "--no-stream",
        "--format",
        "{{json .}}"
    ])

    if result.returncode != 0:
        return

    metrics = []

    for line in result.stdout.splitlines():

        stats = json.loads(line)

        container = running_map.get(stats["Container"])

        if container is None:
            continue

        cpu = parse_cpu(stats["CPUPerc"])

        memory = parse_memory(stats["MemUsage"])

        network_rx, network_tx = parse_network(
            stats["NetIO"]
        )

        disk_read, disk_write = parse_disk(
            stats["BlockIO"]
        )

        metric = ContainerMetric(

            container_log_id=container.id,

            cpu_usage=cpu,

            memory_usage=memory,

            network_rx=network_rx,

            network_tx=network_tx,

            disk_read=disk_read,

            disk_write=disk_write,

            recorded_at=datetime.now()

        )

        metrics.append(metric)

    if metrics:

        db.session.add_all(metrics)

        db.session.commit()

def collector_loop():

    while True:

        try:

            collect_metrics()

        except Exception as e:

            print(f"[Collector Error] {e}")

        time.sleep(METRICS_INTERVAL)

def start_metrics_collector(app):

    def collector():

        with app.app_context():

            collector_loop()

    thread = threading.Thread(
        target=collector,
        daemon=True
    )

    thread.start()