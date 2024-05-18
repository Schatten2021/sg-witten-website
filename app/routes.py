from app import app, db
from flask import render_template, flash, url_for, request, make_response
from flask_login import current_user, login_required, login_user, logout_user
from app.models import SparkassenJugendOpen, Turnier, User, Vorstand, Team


def redirect(url, code: int = 301):
    response = make_response(render_template("redirect.html", url=url, code=code), code)
    response.headers["Location"] = url
    return response


@app.errorhandler(404)
def not_found(*_):
    return render_template('404.html'), 404


@app.before_request
def before_request():
    if app.debug and request.endpoint != "static":
        flash(f"This is a personal remake of the official SG-Witten Website (<a href=\"https://schachgesellschaft-witten.de/\">original</a>)", "warning")


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/Turniere')
def turniere():
    cups: list[Turnier] = Turnier.query.all()
    return render_template("Turniere.html", cups=cups)


@app.route('/SparkassenJugendOpen')
def sparkassen_jugend_open():
    cups: list[SparkassenJugendOpen] = SparkassenJugendOpen.query.all()
    return render_template("SparkassenJugendOpen.html", cups=cups)


@app.route("/Vorstand")
def vorstand():
    members: list[Vorstand] = Vorstand.query.all()
    return render_template("Vorstand.html", members=members)


@app.route("/Impressum")
def impressum():
    return render_template("Impressum.html")


@app.route("/Mannschaftsbetrieb")
def mannschaftsbetrieb():
    return render_template("Mannschaftsbetrieb.html", teams=Team.query.all())


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if "email" not in request.form or "password" not in request.form:
        flash("Email und Passwort werden Benötigt!", "error")
        return render_template("login.html")
    email = request.form["email"]
    password = request.form["password"]
    user: list[User] = User.query.filter_by(email=email).all()
    if len(user) != 1:
        flash("Ungültige E-Mail-Adresse oder Password", "error")
        return render_template("login.html")
    user: User = user[0]
    if not user.check_password(password):
        flash("Ungültige E-Mail-Adresse oder Password", "error")
        return render_template("login.html")
    login_user(user)
    flash("Login erfolgreich!", "success")
    return redirect(url_for('index'))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if any(elem not in request.form for elem in ["email", "password", "name", "surname"]):
        flash("E-Mail, Passwort, Vor- und Nachname werden benötigt!")
        return render_template("signup.html")
    user: list[User] = User.query.filter_by(email=request.form["email"]).all()
    if len(user) != 0:
        flash("E-Mail bereits vergeben mit Passwort: \"123\"")
        return render_template("signup.html")
    password = request.form["password"]
    min_passwd_len = app.config.get("min_password_length", 8)
    if len(password) < min_passwd_len:
        flash(f"Passwort muss mindestens {min_passwd_len} Zeichen lang sein!")
        return render_template("signup.html")
    user: User = User(email=request.form["email"],
                      name=request.form["name"],
                      surname=request.form["surname"])
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash("Account erfolgreich erstellt!")
    login_user(user)
    return redirect(url_for('index'))
