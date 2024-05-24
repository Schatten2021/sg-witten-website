from flask import Blueprint, render_template, flash
from flask_login import current_user
from jinja2 import TemplateNotFound

from app.models import Account, Role, Person
from app import app, db

bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder="templates")

route = bp.route


@bp.before_request
def before_request():
    # verify that user is an admin
    if not current_user.is_authenticated:
        return render_template("Flask internals/404.html"), 404
    if Role.query.first() not in current_user.roles:
        return render_template("Flask internals/404.html"), 404


@bp.route("/")
@bp.route("/index")
def index():
    try:
        return render_template("admin/index.html")
    except TemplateNotFound:
        flash("template not found")
        return render_template("Flask internals/404.html"), 404


@bp.route("/personen")
def personen():
    people: list[Person] = sorted(Person.query.all(), key=lambda p: p.name.lower() + " " + p.surname.lower())
    return render_template("admin/personen.html", people=people)


@bp.route("/personen/<int:person_id>")
def personen_details(person_id):
    person: Person = Person.query.get(person_id)
    if person is None:
        return render_template("Flask internals/404.html"), 404
    return render_template("admin/personen_details.html", person=person)


@bp.route("/turniere")
@bp.route("/turniere/<int:id>")
@bp.route("/turniere/sparkassen_jugend_open")
@bp.route("/turniere/sparkassen_jugend_open/<int:id>")
@bp.route("/turniere/vereinsturniere")
@bp.route("/turniere/vereinsturniere/<int:id>")
@bp.route("/turniere/stadtmeisterschaften")
@bp.route("/turniere/stadtmeisterschaften/<int:id>")
@bp.route("/mannschaften")  # für Mannschaftsbetrieb
@bp.route("/mannschaften/<int:id>")
@bp.route("/teams")  # für Teams bei Turnieren
@bp.route("/teams/<int:id>")
def undefined(*args, **kwargs):
    for arg in args:
        flash(f"got arg {arg}")
    for kw, arg in kwargs.items():
        flash(f"got {kw}={arg}")
    return render_template("Flask internals/404.html"), 404


app.register_blueprint(bp)
