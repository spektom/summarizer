import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s: %(message)s')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/manager.db'.format(
    Path(__file__).parent.parent.absolute())
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from .model import init_db
from .api import *
from .views import *

init_db()
