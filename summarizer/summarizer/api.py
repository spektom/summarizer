from datetime import datetime
from flask import request, jsonify

from .app import app
from .nlp import create_summarizer, is_news_title
from .html import html_to_clean_text
from .recent import create_similar_articles_scorer

make_summary = create_summarizer()
similar_articles_score = create_similar_articles_scorer()


@app.route('/summarize', methods=['POST'])
def summarize():
    id = request.json['id']
    title = request.json['title']
    html = request.json['html']
    topN = request.json.get('top_n', 4)
    create_time = datetime.strptime(
        request.json.get('create_time',
                         datetime.utcnow().isoformat()), '%Y-%m-%dT%H:%M:%S.%f')
    summary = make_summary(title, html, topN)
    return jsonify({
        'summary': summary,
        'similar_articles': similar_articles_score(id, title, create_time)
    })


@app.route('/isnewstitle', methods=['POST'])
def newsscore():
    return jsonify({'value': is_news_title(request.json['title'])})
