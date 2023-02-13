from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    RadioField,
    DateField,
    SelectField,
)
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired, Optional, DataRequired
from datetime import datetime, date
from values_dict import international_values_dict_computable


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


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


class dailyStipendInternationalForm(dailyStipendForm):
    country = SelectField(
        "Country",
        choices=[(a, a) for a in list(international_values_dict_computable.keys())],
        default="Albânia",
        validators=[Optional()],
    )

    location = SelectField("Location", choices=[], validators=[Optional()])


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
