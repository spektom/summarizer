from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

app = Flask(__name__)
db_path = Path(__file__).parent.parent.absolute()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/db.sqlite'.format(db_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from .model import init_db
from .api import *

init_db()
