from database import db

class ContainerLog(db.Model):
    __tablename__ = "container_logs"

    id = db.Column(db.Integer, primary_key=True)

    container_id = db.Column(db.String(64), nullable=False)

    container_name = db.Column(db.String(100))

    image = db.Column(db.String(100), nullable=False)

    status = db.Column(db.String(20), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False)

    stopped_at = db.Column(db.DateTime)

    metrics = db.relationship("ContainerMetric", backref="container", lazy=True, cascade="all, delete-orphan")

class ContainerMetric(db.Model):

    __tablename__ = "container_metrics"

    id = db.Column(db.Integer, primary_key=True)

    container_log_id = db.Column(
        db.Integer,
        db.ForeignKey("container_logs.id"),
        nullable=False
    )

    cpu_usage = db.Column(db.Float, nullable=False)

    memory_usage = db.Column(db.Float, nullable=False)

    network_rx = db.Column(db.Float)

    network_tx = db.Column(db.Float)

    disk_read = db.Column(db.Float)

    disk_write = db.Column(db.Float)

    recorded_at = db.Column(
        db.DateTime,
        nullable=False
    )
