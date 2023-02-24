from app import app, db
from flask import (
    render_template,
    flash,
    redirect,
    request,
    url_for,
    send_from_directory,
    jsonify,
)
from app.forms import (
    RegistrationForm,
    LoginForm,
    dailyStipendForm,
    dailyStipendInternationalForm,
    dailyStipendNationalForm,
)
from fapesp_calculator.por_extenso import data_por_extenso
from fapesp_calculator.calculate_national import generate_template_for_national_event
from fapesp_calculator.calculate_international import (
    generate_template_for_international_event,
)
from app.values_dict import international_values_dict_computable
import os
from flask_login import logout_user
from werkzeug.urls import url_parse
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    current_user,
    login_user,
    LoginManager,
    UserMixin,
    login_required,
)
from app.models import User, Post

from pathlib import Path
from datetime import datetime
from app.forms import EditProfileForm

HERE = Path(__file__).parent.resolve()


login = LoginManager(app)
login.login_view = "login"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
    db.session.commit()


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.full_name = form.full_name.data

        current_user.advisor_full_name = form.advisor_full_name.data
        current_user.fapesp_process_number = form.fapesp_process_number.data

        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.fapesp_process_number.data = current_user.fapesp_process_number
        form.full_name.data = current_user.full_name
        form.advisor_full_name.data = current_user.advisor_full_name

    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/pr35")
def pr35():
    return render_template("pr35.html")


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
            filled_template_path=HERE.joinpath("uploads/modelo_preenchido.docx"),
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
                filled_template_path=HERE.joinpath("uploads/modelo_preenchido.docx"),
            )
        if form.level.data == "plus":
            message_to_send = generate_template_for_national_event(
                my_dict=my_dict,
                event_start_date_time=form.event_start_date.data,
                event_end_date_time=form.event_end_date.data,
                category="Pesquisadores, dirigentes, coordenadores, assessores, conselheiros e pós-doutorandos",
                subcategory="Com pernoite (em capitais de Estado, Angra dos Reis (RJ), Brasília (DF), Búzios (RJ) e Guarujá (SP)",
                extra_day=extra_day,
                filled_template_path=HERE.joinpath("uploads/modelo_preenchido.docx"),
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {"author": user, "body": "Test post #1"},
        {"author": user, "body": "Test post #2"},
    ]
    return render_template("user.html", user=user, posts=posts)
