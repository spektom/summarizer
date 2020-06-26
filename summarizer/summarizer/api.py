from flask import request, jsonify, Flask
from . import create_summarizer

app = Flask(__name__)

make_summary = create_summarizer()


@app.route('/summarize', methods=['POST'])
def summarize():
    return jsonify({
        'summary': make_summary(request.json['text'], request.json['title'],
                                request.json.get('top_n', 4))
    })
