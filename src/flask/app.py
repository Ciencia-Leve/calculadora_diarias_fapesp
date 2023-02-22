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

import flask
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
from werkzeug.urls import url_parse
from datetime import date, datetime
from fapesp_calculator.calculate_international import *
from fapesp_calculator.calculate_national import *
from config import Config
from fapesp_calculator.por_extenso import data_por_extenso
import os
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    current_user,
    login_user,
    LoginManager,
    UserMixin,
    login_required,
)
from forms import *

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = "login"

APP = Path(__file__).parent.resolve()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User {}>".format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<Post {}>".format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


international_values_dict = json.loads(
    RESULTS.joinpath("fapesp_international_values.json").read_text(encoding="UTF-8")
)

international_values_dict_computable = {}

for country_for_dict, country_data in international_values_dict.items():
    international_values_dict_computable[country_for_dict] = dict()

    for location_for_dict, value in country_data.items():
        international_values_dict_computable[country_for_dict][
            location_for_dict
        ] = Money(value.replace(",", "."), Currency.USD)

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


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/faq")
def faq():
    return flask.render_template("faq.html")


@app.route("/pr35")
def pr35():
    return flask.render_template("pr35.html")


@app.route("/internacional/", methods=["GET", "POST"])
@app.route("/internacional", methods=["GET", "POST"])
def internacional():
    form = dailyStipendInternationalForm()
    form.location.choices = [
        (a, a) for a in list(international_values_dict_computable["Albânia"].keys())
    ]

    if request.method == "POST" and form.validate():
        print("RUNNING CODE")
        my_dict = {}
        if form.plus_day.data == "sim":
            extra_day = True
        else:
            extra_day = False

        message_to_send = generate_template_for_international_event(
            my_dict=my_dict,
            event_start_date_time=form.event_start_date.data,
            event_end_date_time=form.event_end_date.data,
            extra_day=extra_day,
            country=form.country.data,
            subnational_location=form.location.data,
            filled_template_path=APP.joinpath("uploads/modelo_preenchido.docx"),
        )

        return render_template(
            "internacional.html",
            submitted=True,
            form=form,
            message_to_send=message_to_send,
            location=form.location.data,
            country=form.country.data,
            daily_stipend=international_values_dict_computable[form.country.data][
                form.location.data
            ],
        )

    return render_template("internacional.html", submitted=False, form=form)


@app.route("/location/<country>")
def location(country):
    locations = [
        {"name": a} for a in list(international_values_dict_computable[country].keys())
    ]
    return jsonify({"locations": locations})


@app.route("/nacional/", methods=["GET", "POST"])
@app.route("/nacional", methods=["GET", "POST"])
@login_required
def nacional():
    form = dailyStipendNationalForm()
    print("HERE")

    if request.method == "POST" and form.validate():
        print("VALIDATED")
        my_dict = {}
        if form.plus_day.data == "sim":
            extra_day = True
        else:
            extra_day = False

        if form.level.data == "base":
            message_to_send = generate_template_for_national_event(
                my_dict=my_dict,
                event_start_date_time=form.event_start_date.data,
                event_end_date_time=form.event_end_date.data,
                extra_day=extra_day,
                filled_template_path=APP.joinpath("uploads/modelo_preenchido.docx"),
            )
        if form.level.data == "plus":
            message_to_send = generate_template_for_national_event(
                my_dict=my_dict,
                event_start_date_time=form.event_start_date.data,
                event_end_date_time=form.event_end_date.data,
                category="Pesquisadores, dirigentes, coordenadores, assessores, conselheiros e pós-doutorandos",
                subcategory="Com pernoite (em capitais de Estado, Angra dos Reis (RJ), Brasília (DF), Búzios (RJ) e Guarujá (SP)",
                extra_day=extra_day,
                filled_template_path=APP.joinpath("uploads/modelo_preenchido.docx"),
            )

        return render_template(
            "nacional.html",
            submitted=True,
            form=form,
            message_to_send=message_to_send,
        )

    return render_template("nacional.html", submitted=False, form=form)


@app.route("/about")
def about():
    return flask.render_template("about.html")


@app.route("/uploads/<path:filename>", methods=["GET", "POST"])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"])

    # Returning file from appended path
    return send_from_directory(directory=uploads, path=filename)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
