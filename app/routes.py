import random
import string
from urllib.parse import quote

from flask import render_template, flash, request, make_response
from flask_login import current_user, login_user
from flask_mail import Message

from app import app, db, mail
from app.models import Account, Person, AuthenticationRequest, Mannschaft, VorstandsRolle, Turnier, \
    SparkassenJugendOpen, Stadtmeisterschaft
from app.admin_routes import *


# general flask stuff
def redirect(url, code: int = 301):
    response = make_response(render_template("Flask internals/redirect.html", url=url, code=code), code)
    response.headers["Location"] = url
    return response


@app.errorhandler(404)
def not_found(*_):
    return render_template('Flask internals/404.html'), 404


@app.before_request
def before_request():
    if request.endpoint != "static" and "Location" not in request.headers:
        flash(
            f"This is a personal remake of the official SG-Witten Website (<a href=\"https://schachgesellschaft-witten.de/\">original</a>). "
            f"Alle Daten auf dieser Seite sind dem Original entnommen. "
            f"Source code available on <a href=\"https://github.com/Schatten2021/sg-witten-website\">github</a>",
            "warning")


@app.route('/')
@app.route('/index')
def index():
    return render_template('sites/index.html')


@app.route("/Impressum")
def impressum():
    return render_template("sites/Impressum.html")


# accounts
@app.route("/login", methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous:
        return redirect(request.args.get("next", "/"))
    # verify request
    if request.method == 'GET':
        return render_template("Account/login.html")
    if "email" not in request.form or "password" not in request.form:
        flash("Email und Passwort werden Benötigt!", "error")
        return render_template("Account/login.html")

    # get account
    email = request.form["email"]
    password = request.form["password"]
    account: list[Account] = Account.query.filter_by(email=email).all()

    # verify login
    if len(account) != 1:
        flash("Ungültige E-Mail-Adresse oder Password", "error")
        return render_template("Account/login.html")
    account: Account = account[0]
    if not account.check_password(password):
        flash("Ungültige E-Mail-Adresse oder Password", "error")
        return render_template("Account/login.html")

    # login
    login_user(account)
    flash("Login erfolgreich!", "success")
    return redirect(request.args.get('next', "/"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # validate request
    if not current_user.is_anonymous:
        return redirect(request.args.get("next", "/"))
    if request.method == 'GET':
        return render_template("Account/signup.html")
    if any(elem not in request.form for elem in ["email", "password", "name", "surname"]):
        flash("E-Mail, Passwort, Vor- und Nachname werden benötigt!")
        return render_template("Account/signup.html")

    # check if user doesn't already exist
    account: list[Account] = Account.query.filter_by(email=request.form["email"]).all()
    if len(account) != 0:
        flash("E-Mail bereits vergeben mit Passwort: \"123\"")
        return render_template("Account/signup.html")
    password = request.form["password"]
    min_passwd_len = app.config.get("min_password_length", 8)
    if len(password) < min_passwd_len:
        flash(f"Passwort muss mindestens {min_passwd_len} Zeichen lang sein!")
        return render_template("Account/signup.html")

    # find/create person
    person: Person = Person.query.filter_by(name=request.form["name"],
                                            surname=request.form["surname"]).first()
    if person is None:
        person = Person(name=request.form["name"], surname=request.form["surname"])
    elif Account.query.filter_by(person=person).first() is not None:
        flash(f"Sie haben bereits einen Account.")
        return redirect("/login")

    # create account
    account: Account = Account(email=request.form["email"],
                               person=person)
    account.set_password(password)
    db.session.add(account)

    # send email validation
    authentication_id: str = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                                     for _ in range(64))
    authentication_request: AuthenticationRequest = AuthenticationRequest(id=authentication_id,
                                                                          account=account)
    db.session.add(authentication_request)
    email_content: str = render_template("Account/verification email.html",
                                         authentication_request=authentication_request)

    email = Message(subject="Bitte bestätigen sie Ihre E-Mail Adresse", recipients=[request.form["email"]],
                    html=email_content)
    mail.send(email)
    db.session.commit()

    flash("Account erfolgreich erstellt!", "success")
    flash(
        f"Verifizierungsmail an {account.email} geschickt! "
        f"Bitte bestätigen sie ihre E-Mail-Adresse so zeitnah wie möglich.",
        "success")
    login_user(account)
    return redirect(request.args.get("next", "/"))


@app.route("/verify_email")
def verify_email():
    if current_user.is_anonymous:
        flash("Sie müssen eingeloggt sein, damit sie ihre E-Mail verifizieren können.")
        return redirect(f"/login?next={quote(request.url, safe='')}")
    verification_request: AuthenticationRequest = AuthenticationRequest.query.filter_by(
        id=request.args.get("id")).first()
    if verification_request is None or verification_request.account != current_user:
        flash("E-Mail verifizierung fehlgeschlagen. "
              "Eventuell wurde die E-Mail Adresse bereits verifiziert oder die ID ist ungültig.")
        return redirect("/")

    db.session.delete(verification_request)
    current_user.is_authenticated = True
    db.session.add(current_user)
    db.session.commit()
    flash("E-Mail erfolgreich verifiziert.")
    return redirect("/")


# Turniere
@app.route("/Turniere")
def turniere():
    cups: list[Turnier] = Turnier.query.all()
    return render_template("Turniere/Alle.html", cups=cups)


@app.route("/Turniere/SparkassenJugendOpen")
def sparkassen_jugend_open():
    cups: list[SparkassenJugendOpen] = SparkassenJugendOpen.query.all()
    return render_template("Turniere/Sparkassen Jugend Open.html", cups=cups)


@app.route("/Turniere/Stadtmeisterschaften")
def stadtmeisterschaften():
    cups: list[Stadtmeisterschaft] = Stadtmeisterschaft.query.all()
    return render_template("Turniere/Stadtmeisterschaften.html", cups=cups)


# andere
@app.route("/Mannschaftsbetrieb")
def mannschaftsbetrieb():
    teams = Mannschaft.query.all()
    return render_template("sites/Mannschaftsbetrieb.html", teams=teams)


@app.route("/Vorstand")
def vorstand():
    roles: list[VorstandsRolle] = VorstandsRolle.query.all()
    return render_template("sites/Vorstand.html", roles=roles)
