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
    is_aggregator = db.Column(db.Boolean, nullable=False, default=False)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_time = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow,
                            onupdate=datetime.utcnow)
    feed_id = db.Column(db.Integer, index=True)
    uri = db.Column(db.Text, nullable=False, unique=True)
    status = db.Column(db.Text, nullable=False)
    retries = db.Column(db.Integer, nullable=False, default=0)
    title = db.Column(db.Text)
    summary = db.Column(db.Text)
    html = db.Column(db.Text)
    refs_count = db.Column(db.Integer, nullable=False, default=1)
    source = db.Column(db.Text)


def init_db():
    db.create_all()
    if Feed.query.count() == 0:
        for feed in [ \
                Feed(uri='https://api.axios.com/feed/', name='Axios', category='Top'),
                Feed(uri='http://feeds.foxnews.com/foxnews/tech', name='Fox News', category='Tech'),
                Feed(uri='http://feeds.nbcnews.com/nbcnews/public/tech', name='NBC News', category='Technology'),
                Feed(uri='http://feeds.skynews.com/feeds/rss/technology.xml', name='Sky News', category='Technology'),
                Feed(uri='http://feeds.washingtonpost.com/rss/rss_innovations', name='Washington Post', category='Innovations'),
                Feed(uri='https://feeds.a.dj.com/rss/RSSWSJD.xml', name='WSJ', category='Technology: What\'s News'),
                Feed(uri='https://feeds.feedburner.com/TechCrunch', name='TechCrunch', category='All Content', is_aggregator=True),
                Feed(uri='https://feeds.feedburner.com/TheHackersNews', name='THN', category='Latest News', is_aggregator=True),
                Feed(uri='https://feeds.npr.org/1019/rss.xml', name='NPR', category='Technology'),
                Feed(uri='https://gizmodo.com/rss', name='Gizmodo', category='All News'),
                Feed(uri='https://news.crunchbase.com/feed/', name='CrunchBase', category='News'),
                Feed(uri='https://news.google.com/news/rss/headlines/section/topic/TECHNOLOGY', name='Google News', category='Technology', is_aggregator=True),
                Feed(uri='https://news.google.com/news/rss/headlines/section/topic/BUSINESS', name='Google News', category='Business', is_aggregator=True),
                Feed(uri='https://nypost.com/tech/feed/', name='NYPost', category='Tech'),
                Feed(uri='https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml', name='NYT', category='Technology'),
                Feed(uri='https://thenewstack.io/blog/feed', name='The New Stack', category='Recent Stories'),
                Feed(uri='https://venturebeat.com/feed/', name='VentureBeat', category='Latest News'),
                Feed(uri='https://www.businessinsider.com/sai/rss', name='Business Insider', category='Tech Insider'),
                Feed(uri='https://www.buzzfeed.com/tech.xml', name='BuzzFeed News', category='Tech'),
                Feed(uri='https://www.cnbc.com/id/19854910/device/rss/rss.html', name='CNBC', category='Technology'),
                Feed(uri='https://www.cnet.com/rss/news/', name='CNET', category='News'),
                Feed(uri='https://www.computerweekly.com/rss/All-Computer-Weekly-content.xml', name='ComputerWeekly', category='All Content'),
                Feed(uri='https://www.economist.com/business/rss.xml', name='The Economist', category='Business'),
                Feed(uri='https://www.economist.com/science-and-technology/rss.xml', name='The Economist', category='Science and Technology'),
                Feed(uri='https://www.engadget.com/rss.xml', name='Engadget', category='All News'),
                Feed(uri='https://www.eweek.com/rss.xml', name='eWEEK', category='Last Articles'),
                Feed(uri='https://www.digitaltrends.com/news/feed/', name='Digital Trends', category='Tech News'),
                Feed(uri='https://www.geekwire.com/feed/', name='GeekWire', category='News'),
                Feed(uri='https://www.infotech.com/rss/infotech.xml', name='Info-Tech', category='All'),
                Feed(uri='https://www.infoworld.com/news/index.rss', name='InfoWorld', category='News'),
                Feed(uri='https://www.itworld.com/index.rss', name='ITworld', category='All News'),
                Feed(uri='https://www.jpost.com/rss/rssfeedsjposttech', name='JPost.com', category='Hi-Tech News'),
                Feed(uri='https://www.jpost.com/rss/rssfeedsjposttechbusinessandinnovation', name='JPost.com', category='Business & Tech'),
                Feed(uri='https://www.technologyreview.com/feed/', name='MIT Technology Review', category='All Stories'),
                Feed(uri='https://www.techradar.com/rss', name='TechRadar', category='All News'),
                Feed(uri='https://www.techrepublic.com/rssfeeds/articles/', name='TechRepublic', category='Articles'),
                Feed(uri='https://www.techtimes.com/rss/sections/personaltech.xml', name='Tech Times', category='Tech'),
                Feed(uri='https://www.theguardian.com/uk/technology/rss', name='The Guardian', category='Technology'),
                Feed(uri='https://www.telegraph.co.uk/technology/rss.xml', name='The Telegraph', category='Tech'),
                Feed(uri='https://www.theverge.com/tech/rss/index.xml', name='The Verge', category='Tech Posts'),
                Feed(uri='https://www.thewrap.com/category/tech/feed/', name='TheWrap', category='TheWrapTech'),
                Feed(uri='https://www.washingtontimes.com/rss/headlines/culture/technology/', name='The Washington Times', category='Technology'),
                Feed(uri='https://www.wired.com/feed/category/business/latest/rss', name='Wired', category='Business'),
                Feed(uri='https://www.wired.com/feed/category/security/latest/rss', name='Wired', category='Security'),
                Feed(uri='https://www.zdnet.com/news/rss.xml', name='ZDNet', category='Latest News')
        ]:
            db.session.add(feed)
        db.session.commit()
