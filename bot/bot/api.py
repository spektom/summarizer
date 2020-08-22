import logging

from flask import request, jsonify, Flask
from . import send_to_editors

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s: %(message)s')

app = Flask(__name__)


@app.route('/summary', methods=['POST'])
def summary():
    send_to_editors(request.json['source'], request.json['uri'], request.json['title'],
                    request.json['summary'], request.json.get('importance', 0))
    return '', 200
