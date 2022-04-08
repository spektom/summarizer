import logging

from flask import request, jsonify, Flask
from . import send_to_editors, send_directly

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(module)s: %(message)s"
)

app = Flask(__name__)

CURATED = False


@app.route("/summary", methods=["POST"])
def summary():
    if CURATED:
        send_to_editors(
            request.json["source"],
            request.json["uri"],
            request.json["title"],
            request.json["summary"],
            request.json.get("importance", 0),
        )
    else:
        send_directly(
            request.json["source"],
            request.json["uri"],
            request.json["title"],
            request.json["summary"],
        )
    return "", 200
