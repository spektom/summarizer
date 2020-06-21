from datetime import datetime
from .app import app, db


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_publish_time = db.Column(db.DateTime)
    uri = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    etag = db.Column(db.Text)
    modified = db.Column(db.Text)


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
                Feed(uri='https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml', \
                     name='NYT',
                     category='Technology'),
                Feed(uri='https://feeds.feedburner.com/TheHackersNews',
                     name='THN',
                     category='Latest News'),
                Feed(uri='https://thenewstack.io/blog/feed',
                     name='The New Stack',
                     category='Recent Stories'),
                Feed(uri='https://www.techradar.com/rss',
                     name='TechRadar',
                     category='All News'),
                Feed(uri='https://feeds.feedburner.com/TechCrunch',
                     name='TechCrunch',
                     category='All Content'),
                Feed(uri='https://www.thewrap.com/category/tech/feed/',
                     name='TheWrap',
                     category='TheWrapTech'),
                Feed(uri='https://www.techrepublic.com/rssfeeds/articles/',
                     name='TechRepublic',
                     category='Articles'),
                Feed(uri='https://www.businessinsider.com/sai/rss',
                     name='Business Insider',
                     category='Tech Insider'),
                Feed(uri='https://www.wired.com/feed/category/business/latest/rss', \
                     name='Wired',
                     category='Business'),
                Feed(uri='https://www.wired.com/feed/category/security/latest/rss', \
                     name='Wired',
                     category='Security'),
                Feed(uri='https://www.technologyreview.com/feed/',
                     name='MIT Technology Review',
                     category='All Stories'),
                Feed(uri='http://feeds.washingtonpost.com/rss/rss_innovations',
                     name='Washington Post',
                     category='Innovations'),
                Feed(uri='http://feeds.bbci.co.uk/news/technology/rss.xml',
                     name='BBC',
                     category='Technology')
        ]:
            db.session.add(feed)
        db.session.commit()
