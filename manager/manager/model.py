from datetime import datetime
from .app import app, db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow)
    update_time = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow,
                            onupdate=datetime.utcnow)
    uri = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(1), nullable=False)


db.create_all()
