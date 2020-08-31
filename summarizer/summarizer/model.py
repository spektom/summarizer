from datetime import datetime
from .app import db


class RecentArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False)


def init_db():
    db.create_all()
