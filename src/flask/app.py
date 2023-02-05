""" A flask app to connect iNaturalist to Wikidata."""

from dataclasses import dataclass
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from taxon2wikipedia.render_page import get_pt_wikipage_from_qid
from wdcuration import get_statement_values, lookup_id
from wtforms import BooleanField, IntegerField, StringField
from wtforms.validators import InputRequired, Optional

import flask
from flask import Flask, redirect, render_template, request, send_from_directory
from inat2wiki.get_user_observations import get_observations_with_wiki_info
from inat2wiki.parse_observation import get_commons_url, request_observation_data

from fapesp_calculator.calculate_national import *
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
    name = StringField("Nome completo", validators=[InputRequired()])
    n_do_processo = StringField("Número do Processo", validators=[InputRequired()])
    cpf = StringField("CPF", validators=[InputRequired()])
    identidade = StringField("Identidade", validators=[InputRequired()])
    endereço = StringField("Endereço (rua e número)", validators=[InputRequired()])
    bairro = StringField("Bairro", validators=[InputRequired()])
    cidade = StringField("Cidade", validators=[InputRequired()])


@app.route("/natal/", methods=["GET", "POST"])
@app.route("/natal", methods=["GET", "POST"])
def projectlist_base():
    form = dailyStipendForm()
    if form.validate_on_submit():

        my_dict["nome_completo"] = form.name.data
        my_dict["n_do_processo"] = form.n_do_processo.data
        my_dict["cpf"] = form.cpf.data
        my_dict["identidade"] = form.identidade.data
        my_dict["endereço"] = form.endereço.data
        my_dict["bairro"] = form.bairro.data
        my_dict["cidade"] = form.cidade.data

        generate_template_for_natal(
            my_dict=my_dict,
            filled_template_path=APP.joinpath("uploads/modelo_preenchido.docx"),
        )

        return render_template("natal.html", form=form, name=form.name.data)

    return render_template("natal.html", form=form)


@app.route("/about")
def about():
    return flask.render_template("about.html")


@app.route("/uploads/<path:filename>", methods=["GET", "POST"])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"])

    # Returning file from appended path
    return send_from_directory(directory=uploads, path=filename)
