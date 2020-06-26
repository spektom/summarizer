import logging

from flask import request, jsonify, Flask
from . import send_summary

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s: %(message)s')

app = Flask(__name__)


@app.route('/send_summary', methods=['POST'])
def send_summary():
    send_summary(request.json['source'], request.json['uri'], request.json['title'],
                 request.json['summary'])
    return '', 200
