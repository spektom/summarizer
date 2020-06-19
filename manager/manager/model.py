from datetime import datetime
from .app import app, db


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_publish_time = db.Column(db.DateTime)
    uri = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow)
    update_time = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow,
                            onupdate=datetime.utcnow)
    feed_id = db.Column(db.Integer, index=True)
    uri = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text)
    summary = db.Column(db.Text)
    html = db.Column(db.Text)


db.create_all()
