import feedparser
import logging

from time import mktime
from datetime import datetime, timedelta
from flask import request, jsonify
from .app import app, db
from .model import Feed, Article


@app.route('/feeds/refresh', methods=['GET'])
def feeds_refresh():
    for feed in Feed.query.all():
        try:
            f = feedparser.parse(feed.uri,
                                 etag=feed.etag,
                                 modified=feed.modified)
            for entry in sorted(f.entries, key=lambda e: e.published_parsed):
                publish_time = datetime.fromtimestamp(
                    mktime(entry.published_parsed))
                if feed.last_publish_time is None or feed.last_publish_time < publish_time:
                    db.session.add(
                        Article(feed_id=feed.id,
                                uri=entry.link,
                                summary=entry.summary if hasattr(entry, 'summary') else None, \
                                status='N'))
                    feed.last_publish_time = publish_time
            if hasattr(f, 'etag'):
                feed.etag = f.etag
            if hasattr(f, 'modified'):
                feed.modified = f.modified
        except:
            app.logger.exception(f'Failed to refresh RSS feed: {feed.uri}')
    db.session.commit()
    return '', 204


@app.route('/tasks/reschedule', methods=['GET'])
def tasks_reschedule():
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    for article in Article.query.filter(Article.status == 'Q'
                                        and Article.update_time < hour_ago
                                        and Article.retries < 3).all():
        article.status = 'N'
        article.retries += 1
    db.session.commit()
    return '', 204


@app.route('/tasks/next', methods=['GET'])
def tasks_next():
    article = Article.query.filter(Article.status == 'N').order_by(
        Article.create_time).first()
    if article is not None:
        article.status = 'Q'
        db.session.commit()
        return jsonify(id=article.id, uri=article.uri)
    return '', 204


@app.route('/articles/add', methods=['POST'])
def articles_add():
    article = request.json
    db.session.add(
        Article(uri=article['uri'], summary=article['summary'], status='N'))
    db.session.commit()
    return '', 201


@app.route('/articles/update', methods=['POST'])
def article_update():
    article = Article.query.get(request.json['id'])
    if 'html' not in request.json:
        article.status = 'E'
    else:
        article.html = request.json['html']
        article.title = request.json['title']
        article.status = 'D'
    db.session.commit()
    return '', 200


@app.route('/pagesaver/log', methods=['POST'])
def pagesaver_log():
    app.logger.log(
        getattr(logging, request.json['level']),
        f"<PageSaver> [{request.json['ts']}] {request.json['message']}")
    return '', 200
