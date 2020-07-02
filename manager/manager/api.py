import feedparser
import logging
import re
import requests

from time import mktime
from datetime import datetime, timedelta
from flask import request, jsonify
from sqlalchemy import exc
from sqlalchemy.sql.expression import func
from .app import app, db
from .model import Feed, Article


def is_blacklisted(uri):
    for pattern in [r'.*/www.youtube.com/.*']:
        if re.match(pattern, uri):
            return True
    return False


def publish_article(article):
    r = requests.post('http://localhost:6000/summarize',
                      json={
                          'title': article.title,
                          'html': article.html
                      })
    r.raise_for_status()
    summary = r.json()['summary']

    source = 'Anonymous'
    if article.source is not None:
        source = article.source
    elif article.feed_id is not None:
        source = Feed.query.get(article.feed_id).name

    r = requests.post('http://localhost:7000/summary',
                      json={
                          'source': source,
                          'title': article.title,
                          'uri': article.uri,
                          'summary': summary
                      })
    r.raise_for_status()


@app.route('/feeds/refresh', methods=['GET'])
def feeds_refresh():
    for feed in Feed.query.all():
        try:
            app.logger.info(f'Refreshing RSS feed: {feed.uri}')
            last_publish_time = feed.last_publish_time
            parsed_feed = feedparser.parse(feed.uri,
                                           etag=feed.etag,
                                           modified=feed.modified)

            for entry in sorted(parsed_feed.entries, key=lambda e: e.published_parsed):
                publish_time = datetime.fromtimestamp(mktime(entry.published_parsed))

                if last_publish_time is None or last_publish_time < publish_time:
                    article_uri = entry.link

                    if feed.is_aggregator:
                        # Find out the original URI to avoid duplications
                        try:
                            article_uri = requests.head(article_uri,
                                                        allow_redirects=True).url
                        except:
                            continue

                    if is_blacklisted(article_uri):
                        continue

                    article_uri = re.sub(r'[?#].*', '', article_uri)

                    # Determine source in case of aggregator
                    source = None
                    if feed.is_aggregator and hasattr(entry, 'source'):
                        source = entry.source.title

                    try:
                        app.logger.info(f'Adding new article: {article_uri}')
                        db.session.add(
                            Article(feed_id=feed.id,
                                    uri=article_uri,
                                    summary=entry.summary if hasattr(entry, 'summary') else None, \
                                    status='N',
                                    source=source))
                        db.session.commit()

                    except exc.IntegrityError:  # Existing URI
                        db.session.rollback()

                        # Increment references count
                        existing = Article.query.filter(
                            Article.uri == article_uri).first()
                        existing.refs_count += 1
                        db.session.commit()

                    last_publish_time = publish_time

            feed.last_publish_time = last_publish_time
            if hasattr(parsed_feed, 'etag'):
                feed.etag = parsed_feed.etag
            if hasattr(parsed_feed, 'modified'):
                feed.modified = parsed_feed.modified
            db.session.commit()

        except:
            db.session.rollback()
            app.logger.exception(f'Failed to refresh RSS feed: {feed.uri}')

    return '', 204


@app.route('/tasks/reschedule', methods=['GET'])
def tasks_reschedule():
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    for article in Article.query.filter(Article.status == 'Q'
                                        and Article.update_time < hour_ago).all():
        article.retries += 1
        if article.retries < 3:
            article.status = 'N'
        else:
            article.status = 'E'
    db.session.commit()
    return '', 204


@app.route('/tasks/next', methods=['GET'])
def tasks_next():
    article = Article.query.filter(Article.status == 'N').order_by(
        func.random()).first()
    if article is not None:
        article.status = 'Q'
        db.session.commit()
        return jsonify(id=article.id, uri=article.uri)
    return '', 204


@app.route('/article/<id>', methods=['POST'])
def save_article(id):
    article = Article.query.get_or_404(id)
    article.html = request.json['html']
    article.title = request.json['title']
    article.status = 'D'
    db.session.commit()

    publish_article(article)
    return '', 200


@app.route('/pagesaver/log', methods=['POST'])
def pagesaver_log():
    app.logger.log(getattr(logging, request.json['level']),
                   f"<PageSaver> [{request.json['ts']}] {request.json['message']}")
    return '', 200


@app.route('/publish/<article_id>', methods=['GET'])
def pipeline_run(article_id):
    article = Article.query.get_or_404(article_id)
    if article.status != 'D' or article.html is None:
        return f'Article #{article_id} not been fetched yet', 400

    publish_article(article)
    return '', 200
