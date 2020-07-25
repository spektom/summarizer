import logging

from flask import request, jsonify, Flask
from . import create_summarizer, news_score

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s: %(message)s')

app = Flask(__name__)

make_summary = create_summarizer()


@app.route('/summarize', methods=['POST'])
def summarize():
    return jsonify({
        'summary': make_summary(request.json['title'], request.json['html'],
                                request.json.get('top_n', 4))
    })


@app.route('/newsscore', methods=['POST'])
def newsscore():
    return jsonify({'score': news_score(request.json['title'])})
