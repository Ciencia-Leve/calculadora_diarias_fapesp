from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    RadioField,
    DateField,
    SelectField,
    TextAreaField,
)
from wtforms.validators import (
    InputRequired,
    Optional,
    DataRequired,
    ValidationError,
    DataRequired,
    Email,
    EqualTo,
    Length,
)
from datetime import datetime, date
from app.values_dict import international_values_dict_computable
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    full_name = TextAreaField("Nome completo", validators=[Length(min=0, max=140)])
    advisor_full_name = TextAreaField(
        "Nome do orientador/a", validators=[Length(min=0, max=140)]
    )
    fapesp_process_number = TextAreaField(
        "Número do processo FAPESP", validators=[Length(min=0, max=140)]
    )
    id_number = StringField(
        "Número de identificação", validators=[Length(min=0, max=140)]
    )
    cpf_number = StringField("Número de CPF", validators=[Length(min=0, max=140)])
    address_number = StringField(
        "Logradouro e número de endereço", validators=[Length(min=0, max=140)]
    )
    address_complement = StringField(
        "Complemento de endereço", validators=[Length(min=0, max=140)]
    )
    neighbourhood = StringField("Bairro", validators=[Length(min=0, max=140)])
    city = StringField("Cidade", validators=[Length(min=0, max=140)])
    state = StringField("Estado", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def populate_obj(self, user):
        user.username = self.username.data
        user.email = self.email.data
        user.full_name = self.full_name.data
        user.advisor_full_name = self.advisor_full_name.data
        user.fapesp_process_number = self.fapesp_process_number.data
        user.id_number = self.id_number.data
        user.cpf_number = self.cpf_number.data
        user.address_number = self.address_number.data
        user.address_complement = self.address_complement.data
        user.neighbourhood = self.neighbourhood.data
        user.city = self.city.data
        user.state = self.state.data


class RegistrationForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    password2 = PasswordField(
        "Repita a senha", validators=[DataRequired(), EqualTo("password")]
    )
    full_name = TextAreaField(
        "Nome completo", validators=[Length(min=0, max=140), DataRequired()]
    )
    advisor_full_name = TextAreaField(
        "Nome do orientador/a", validators=[Length(min=0, max=140), DataRequired()]
    )
    fapesp_process_number = TextAreaField(
        "Número do processo FAPESP", validators=[Length(min=0, max=140), DataRequired()]
    )
    submit = SubmitField("Registre-se")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Por favor escolha um nome de usuário diferente.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Por favor use um endereço de email diferente.")


class LoginForm(FlaskForm):
    username = StringField("Nome de usuário:", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember_me = BooleanField("Se lembre de mim")
    submit = SubmitField("Entre")


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
    submit = SubmitField("Calcular")


class dailyStipendNationalForm(dailyStipendForm):
    level = RadioField(
        "Posição",
        choices=[
            ("base", "IC, mestrado ou doutorado"),
            ("plus", "Pós-Doc e além"),
        ],
    )
    submit = SubmitField("Calcular")
