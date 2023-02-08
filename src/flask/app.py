""" A flask app to connect iNaturalist to Wikidata."""

from email.policy import default
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, RadioField, DateField
from wtforms.validators import InputRequired, Optional

import flask
from flask import Flask, redirect, render_template, request, send_from_directory
from datetime import datetime, date
from fapesp_calculator.calculate_international import *
from fapesp_calculator.por_extenso import data_por_extenso
import os
from pathlib import Path

APP = Path(__file__).parent.resolve()

app = Flask(__name__)

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


class dailyStipendForm(FlaskForm):

    event_start_date = DateField(
        "Data de Início do Evento",
        format="%Y-%m-%d",
        default=date(2023, 3, 29),
        validators=[InputRequired()],
    )
    event_end_date = DateField(
        "Data de Término do Evento",
        format="%Y-%m-%d",
        default=date(2023, 3, 31),
        validators=[InputRequired()],
    )

    plus_day = RadioField(
        "Chegada em dia anterior (ou antes) e saída em dia posterior (ou depois) ao evento?",
        default="sim",
        choices=[
            ("sim", "sim"),
            ("não", "não"),
        ],
    )


class dailyStipendNationalForm(dailyStipendForm):

    level = RadioField(
        "Posição",
        choices=[
            ("base", "IC, mestrado ou doutorado"),
            ("plus", "Pós-Doc e além"),
        ],
    )


class dailyStipendFormWithPersonalInfo(dailyStipendForm):

    name = StringField(
        "Nome completo", default="NOME COMPLETO", validators=[Optional()]
    )
    n_do_processo = StringField(
        "Número do Processo", default="NÚMERO DO PROCESSO", validators=[Optional()]
    )
    cpf = StringField("CPF", default="CPF", validators=[Optional()])
    identidade = StringField(
        "Identidade", default="IDENTIDADE", validators=[Optional()]
    )
    endereço = StringField(
        "Endereço (rua e número)", default="ENDEREÇO", validators=[Optional()]
    )
    bairro = StringField("Bairro", default="BAIRRO", validators=[Optional()])
    cidade = StringField("Cidade", default="CIDADE", validators=[Optional()])


@app.route("/internacional/", methods=["GET", "POST"])
@app.route("/internacional", methods=["GET", "POST"])
def internacional():
    form = dailyStipendForm()

    if form.validate_on_submit():
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
            filled_template_path=APP.joinpath("uploads/modelo_preenchido.docx"),
        )

        return render_template(
            "internacional.html",
            submitted=True,
            form=form,
            message_to_send=message_to_send,
        )

    return render_template("internacional.html", submitted=False, form=form)


@app.route("/nacional/", methods=["GET", "POST"])
@app.route("/nacional", methods=["GET", "POST"])
def nacional():
    form = dailyStipendNationalForm()

    if form.validate_on_submit():
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
                category="Pesquisadores, dirigentes, coordenadores, assessores, conselheiros e pós-doutorandos ",
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
