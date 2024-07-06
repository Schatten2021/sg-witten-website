import re
from datetime import datetime

from flask import Blueprint, render_template, flash, request
from flask_login import current_user

from app import app, db
from app.models import Account, Role, Person, Mannschaft, Mannschaftsspieler, Turnier, Teilnehmer, Verein, FFATurnier, \
    SchweizerTurnier, KOTurnier, Game
from app.routes import redirect

bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder="templates")


@bp.before_request
def before_request():
    # verify that user is an admin
    if not current_user.is_authenticated:
        return render_template("Flask internals/404.html"), 404
    if Role.query.first() not in current_user.roles:
        return render_template("Flask internals/404.html"), 404


@bp.route("/personen")
def personen():
    people: list[Person] = sorted(Person.query.filter(Person.id >= 0).all(),
                                  key=lambda p: p.name.lower() + " " + p.surname.lower())
    return render_template("admin/personen.html", people=people)


@bp.route("/personen/<int:person_id>")
def personen_details(person_id):
    person: Person = Person.query.get(person_id)
    if person is None:
        return render_template("Flask internals/404.html"), 404
    return render_template("admin/personen_details.html", person=person)


@bp.route("/personen/<int:person_id>/change_name")
def personen_change_name(person_id):
    person: Person = Person.query.get(person_id)
    if person is None:
        return render_template("Flask internals/404.html"), 404
    if "name" not in request.args or "surname" not in request.args:
        flash("Name and surname must be provided", "error")
        return redirect(f"/admin/personen/{person_id}")
    person.name = request.args["name"]
    person.surname = request.args["surname"]
    db.session.commit()
    flash(f"Name updated successfully", "success")
    return redirect(f"/admin/personen/{person_id}")


@bp.route("/personen/add")
def add_person():
    if "name" not in request.args or "surname" not in request.args:
        flash("Name and surname must be provided", "error")
        return redirect(f"/admin/personen")
    person: Person = Person.query.filter_by(name=request.args["name"], surname=request.args["surname"]).first()
    if person is not None:
        flash(f"Person {person.name}, {person.surname} already exists.", "error")
        return redirect(f"/admin/personen")
    person = Person(name=request.args["name"], surname=request.args["surname"])
    db.session.add(person)
    db.session.commit()
    flash(f"Person {person.name}, {person.surname} added.", "success")
    return redirect(f"/admin/personen/{person.id}")


@bp.route("/personen/delete")
def delete_person():
    if "id" not in request.args:
        flash("id must be provided", "error")
        return redirect(f"/admin/personen")
    person: Person = Person.query.get(request.args["id"])
    if person is None:
        flash("Person not found", "error")
        return redirect(f"/admin/personen")

    pokale: list[Turnier] = (person.vereinspokal_teilnahmen
                             + person.sparkassen_jugend_open_teilnahmen
                             + person.stadtmeisterschaft_teilnahmen
                             + person.vorstands_rollen
                             + person.mannschaftsspieler)
    for teilnahme in pokale:
        teilnahme.person_id = -1
    account: Account = person.account
    if account is not None:
        requests = account.authentication_requests
        for req in requests:
            db.session.delete(req)
        db.session.delete(account)
    db.session.delete(person)
    db.session.commit()

    flash(f"removed person {person.name}, {person.surname}.", "success")
    return redirect(f"/admin/personen")


# Mannschaften
@bp.route("/mannschaften")  # für Mannschaftsbetrieb
def mannschaften():
    teams: list[Mannschaft] = Mannschaft.query.all()
    return render_template("admin/mannschaften.html", teams=teams)


@bp.route("/mannschaften/player_up/<int:player_id>")
def player_up(player_id):
    player: Mannschaftsspieler = Mannschaftsspieler.query.get(player_id)
    if player is None:
        flash(f"Player {player_id} not found")
        return redirect(request.referrer)
    team: Mannschaft = player.mannschaft
    players: list[Mannschaftsspieler] = sorted(team.spieler)
    team_index: int = players.index(player)
    if team_index == 0:
        flash(f"Player {player.person.surname} {player.person.name} already at the top")
        return redirect(request.referrer)
    previous = players[team_index - 1]
    player.ersatz, previous.ersatz = previous.ersatz, player.ersatz
    player.BrettNr, previous.BrettNr = previous.BrettNr, player.BrettNr
    db.session.add(team)
    db.session.commit()
    flash(f"updated successfully", "success")
    return redirect(request.referrer)


# noinspection DuplicatedCode
@bp.route("/mannschaften/player_down/<int:player_id>")
def player_down(player_id):
    player: Mannschaftsspieler = Mannschaftsspieler.query.get(player_id)
    if player is None:
        flash(f"Player {player_id} not found")
        return redirect("/admin/mannschaften")
    team: Mannschaft = player.mannschaft
    players: list[Mannschaftsspieler] = sorted(team.spieler)
    team_index: int = players.index(player)
    if team_index == (len(players) - 1):
        flash(f"Player {player.person.surname} {player.person.name} already at the bottom")
        return redirect(request.referrer)
    next_player = players[team_index + 1]
    player.ersatz, next_player.ersatz = next_player.ersatz, player.ersatz
    player.BrettNr, next_player.BrettNr = next_player.BrettNr, player.BrettNr
    db.session.add(team)
    db.session.commit()
    flash(f"updated successfully", "success")
    return redirect(request.referrer)


@bp.route("/turniere")
def turniere():
    cups: list[Turnier] = Turnier.query.all()
    return render_template("admin/turniere.html", cups=cups)


@bp.route("/turniere/<int:id>", methods=["POST", "GET"])
def edit_turnier(id: int):
    cup: Turnier = Turnier.query.get(id)
    if request.method == "GET":
        return render_template("admin/turnier_details.html", cup=cup)
    try:
        contestants_ids: set[int] = {int(value) for key, value in request.form.items()
                                     if key.startswith("teilnehmer")}
    except ValueError:
        flash("teilnehmerID ungültig!", "error")
        return 400
    for teilnehmer in cup.teilnehmer:
        db.session.delete(teilnehmer)
        for game in Game.query.filter_by(player1=teilnehmer).all():
            db.session.delete(game)
    teilnehmer: list[Teilnehmer] = list()
    for id in contestants_ids:
        person: Person = Person.query.get(id)
        if person is None:
            flash(f"Person {id} not found")
            return 404
        contestant = Teilnehmer(person=person,
                                turnier=cup,
                                verein=Verein.query.first())
        teilnehmer.append(contestant)
    cup.teilnehmer = teilnehmer
    match request.form.get("turnier_type"):
        case "jeder gegen jeden":
            cup.__class__ = FFATurnier
        case "Schweizer":
            cup.__class__ = SchweizerTurnier
        case "K.O.":
            cup.__class__ = KOTurnier
        case _:
            cup.__class__ = Turnier
    games = {(key[len("game "):key.index("-")], key[key.index("-") + 1:]): value
             for key, value in request.form.items()
             if re.match(r"game [0-9]*-[0-9]", key)
             }
    for (player1_index, player2_index), result in games.items():
        if result == "":
            continue
        player1: Teilnehmer = teilnehmer[int(player1_index)]
        player2: Teilnehmer = teilnehmer[int(player2_index)]
        game: Game = Game(player1=player1, player2=player2, result=int(result))
        db.session.add(game)
    print(games)
    db.session.commit()
    return request.form


@bp.route("/teams")  # für Teams bei Turnieren
@bp.route("/teams/<int:id>")
def undefined(*args, **kwargs):
    flash(f"developmentURL {request.url}")
    for arg in args:
        flash(f"got arg {arg}")
    for kw, arg in kwargs.items():
        flash(f"got {kw}={arg}")
    return render_template("Flask internals/404.html"), 404


app.register_blueprint(bp)
