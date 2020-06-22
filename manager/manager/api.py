import feedparser
import logging

from time import mktime
from datetime import datetime, timedelta
from flask import request, jsonify
from sqlalchemy import exc
from .app import app, db
from .model import Feed, Article


@app.route('/feeds/refresh', methods=['GET'])
def feeds_refresh():
    for feed in Feed.query.all():
        try:
            last_publish_time = feed.last_publish_time
            parsed_feed = feedparser.parse(feed.uri,
                                           etag=feed.etag,
                                           modified=feed.modified)
            for entry in sorted(parsed_feed.entries,
                                key=lambda e: e.published_parsed):
                publish_time = datetime.fromtimestamp(
                    mktime(entry.published_parsed))
                if last_publish_time is None or last_publish_time < publish_time:
                    try:
                        db.session.add(
                            Article(feed_id=feed.id,
                                    uri=entry.link,
                                    summary=entry.summary if hasattr(entry, 'summary') else None, \
                                    status='N'))
                        db.session.commit()
                    except exc.IntegrityError:
                        # Such URI already exists
                        db.session.rollback()
                    last_publish_time = publish_time

            feed.last_publish_time = last_publish_time
            if hasattr(parsed_feed, 'etag'):
                feed.etag = parsed_feed.etag
            if hasattr(parsed_feed, 'modified'):
                feed.modified = parsed_feed.modified
            db.session.commit()
        except:
            app.logger.exception(f'Failed to refresh RSS feed: {feed.uri}')
    return '', 204


@app.route('/tasks/reschedule', methods=['GET'])
def tasks_reschedule():
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    for article in Article.query.filter(
            Article.status == 'Q' and Article.update_time < hour_ago).all():
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
