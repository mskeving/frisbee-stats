from flask import Flask
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy

# this needs to be here to run scripts. shrug.
SQLALCHEMY_DATABASE_URI = "postgresql://localhost:5432/classy"

CACHE_TYPE = "simple"

app = Flask(__name__, template_folder='static/templates')

app.config.from_object(__name__)
app.cache = Cache(app)

db = SQLAlchemy(app)


def create_app(config):
    app.config.from_object('config.flask.' + config)
    db.init_app(app)
    return app


def create_db(app):
    db.init_app(app)
    db.drop_all()
    db.create_all()

from app import models, views
