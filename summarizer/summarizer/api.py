from flask import request, jsonify, Flask
from . import create_summarizer

app = Flask(__name__)

make_summary = create_summarizer()


@app.route('/summarize', methods=['POST'])
def summarize():
    title = request.json['title']
    text = request.json['text']
    return jsonify({'summary': make_summary(text, title)})
