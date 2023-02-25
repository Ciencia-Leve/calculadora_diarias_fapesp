""" A flask app to connect iNaturalist to Wikidata."""

from email.policy import default
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    StringField,
    RadioField,
    DateField,
    SelectField,
)
from wtforms.validators import InputRequired, Optional, DataRequired
from flask import (
    Flask,
    jsonify,
    flash,
    url_for,
    redirect,
    render_template,
    request,
    send_from_directory,
)

from fapesp_calculator.calculate_international import *
from fapesp_calculator.calculate_national import *
from app.config import Config
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models, errors

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Bootstrap5(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "uploads"


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
