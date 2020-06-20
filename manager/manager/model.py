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


def init_db():
    db.create_all()
    if Feed.query.count() == 0:
        for feed in [
                Feed(uri='https://feeds.a.dj.com/rss/RSSWSJD.xml',
                     name='WSJ',
                     category='Technology: What\'s News'),
                Feed(uri='https://www.theverge.com/tech/rss/index.xml',
                     name='The Verge',
                     category='Tech Posts'),
                Feed(uri='https://www.zdnet.com/news/rss.xml',
                     name='ZDNet',
                     category='Latest News'),
                Feed(uri='https://venturebeat.com/feed/',
                     name='VentureBeat',
                     category='Latest News'),
                Feed(
                    uri=
                    'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
                    name='NYT',
                    category='Technology')
        ]:
            db.session.add(feed)
        db.session.commit()
