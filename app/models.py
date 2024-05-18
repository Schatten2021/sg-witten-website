from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, relationship

from app import db


class Turnier(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)
    date: Mapped[datetime] = db.Column(db.DateTime)


class SparkassenJugendOpen(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    year: Mapped[int] = db.Column(db.Integer)
    title: Mapped[str] = db.Column(db.String)
    article: Mapped[str] = db.Column(db.String)
    victors: Mapped[list["SparkassenJugendOpenVictors"]] = relationship()


class SparkassenJugendOpenVictors(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String)
    Jahrgang: Mapped[int] = db.Column(db.Integer)
    school: Mapped[str] = db.Column(db.String)
    cup_id: Mapped[int] = db.Column(db.ForeignKey("sparkassen_jugend_open.id"))
    cup: Mapped[SparkassenJugendOpen] = relationship()


class User(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String)
    surname: Mapped[str] = db.Column(db.String)
    email: Mapped[str] = db.Column(db.String)
    password: Mapped[str] = db.Column(db.String)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    is_active: bool = True
    is_authenticated: bool = True
    is_anonymous: bool = False

    def get_id(self):
        return self.id


class Vorstand(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String)
    title: Mapped[str] = db.Column(db.String)
    mail: Mapped[str] = db.Column(db.String)


class Team(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    boards: Mapped[int] = db.Column(db.Integer)
    players: Mapped[list["Player"]] = relationship()

    @property
    def main_players(self) -> list["Player"]:
        return sorted(filter(lambda player: not player.is_reserve, self.players))

    @property
    def reserve_players(self) -> list["Player"]:
        return sorted(filter(lambda player: player.is_reserve, self.players))


class Player(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String)
    surname: Mapped[str] = db.Column(db.String)
    position_in_team: Mapped[int] = db.Column(db.Integer)
    team_id: Mapped[int] = db.Column(db.ForeignKey("team.id"))
    team: Mapped[Team] = relationship()

    @property
    def index_in_team(self) -> int:
        return sorted(self.team.players).index(self)

    @property
    def is_reserve(self) -> bool:
        return self.team.boards <= self.index_in_team

    @property
    def board_number(self) -> int:
        if self.is_reserve:
            return 1001 + self.index_in_team - self.team.boards
        return self.index_in_team + 1  # since 0 index and it should be displayed as 1 index.

    def __lt__(self, other: "Player") -> bool:
        if not isinstance(other, Player):
            raise TypeError(f"other must be of type Player but was of type {type(other)}")
        return self.position_in_team < other.position_in_team
