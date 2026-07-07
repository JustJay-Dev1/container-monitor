# Container Monitoring & Resource Analytics

A cloud-native backend application for monitoring Docker containers using Flask, PostgreSQL, and Docker.

## Features

- Deploy Docker containers
- Stop all running containers
- Restart containers
- Inspect container details
- View CPU, Memory, Network and Disk usage
- Store deployment history in PostgreSQL
- Store historical resource metrics
- REST API based architecture

## Tech Stack

- Python
- Flask
- PostgreSQL
- SQLAlchemy
- Docker
- Linux
- HTML/CSS/JavaScript

## Project Structure

```
container_monitor/

├── app.py
├── database.py
├── models.py
├── services/
├── templates/
├── static/
```

## Architecture

Browser

↓

Flask REST API

↓

Docker Engine

↓

PostgreSQL

## Future Improvements

- Authentication
- Prometheus Integration
- Grafana Dashboard
- Kubernetes Support

## Author

Jayesh Jachak