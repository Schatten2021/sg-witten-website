import logging
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import or_
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
    victors: Mapped[list["SparkassenJugendOpenVictors"]] = relationship(back_populates="cup")


class SparkassenJugendOpenVictors(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String)
    Jahrgang: Mapped[int] = db.Column(db.Integer)
    school: Mapped[str] = db.Column(db.String)
    cup_id: Mapped[int] = db.Column(db.ForeignKey("sparkassen_jugend_open.id"))
    cup: Mapped[SparkassenJugendOpen] = relationship(back_populates="victors")


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
    players: Mapped[list["Player"]] = relationship(back_populates="team")

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
    team: Mapped[Team] = relationship(back_populates="players")

    @property
    def index_in_team(self) -> int:
        return sorted(self.team.players).index(self)

    @property
    def is_reserve(self) -> bool:
        return self.team.boards <= self.index_in_team

    @property
    def board_number(self) -> int:
        if self.is_reserve:
            return 1_000 + self.index_in_team - self.team.boards + 1
        return self.index_in_team + 1  # since 0 index and it should be displayed as 1 index.

    def __lt__(self, other: "Player") -> bool:
        if not isinstance(other, Player):
            raise TypeError(f"other must be of type Player but was of type {type(other)}")
        return self.position_in_team < other.position_in_team


class Stadtmeisterschaft(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    year: Mapped[int] = db.Column(db.Integer)
    title: Mapped[str] = db.Column(db.String)
    teilnehmer: Mapped[list["StadtmeisterschaftTeilnehmer"]] = relationship(back_populates="meisterschaft")

    @property
    def teilnehmer_liste(self) -> list["StadtmeisterschaftTeilnehmer"]:
        return sorted(self.teilnehmer, key=lambda x: x.rank)


class StadtmeisterschaftTeilnehmer(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String)
    surname: Mapped[str] = db.Column(db.String)
    rank: Mapped[int] = db.Column(db.Integer)
    team: Mapped[str] = db.Column(db.String)
    DWZ: Mapped[int] = db.Column(db.Integer)
    points: Mapped[float] = db.Column(db.Float)
    Buchholz: Mapped[float] = db.Column(db.Float)
    meisterschaft_id: Mapped[int] = db.Column(db.ForeignKey("stadtmeisterschaft.id"))
    meisterschaft: Mapped[Stadtmeisterschaft] = relationship(back_populates="teilnehmer")
    anzahl_spielfrei: Mapped[int] = db.Column(db.Integer)

    @property
    def played_games(self) -> list["StadtmeisterschaftSpiel"]:
        return StadtmeisterschaftSpiel.query.filter(or_(StadtmeisterschaftSpiel.player_1_id == self.id,
                                                        StadtmeisterschaftSpiel.player_2_id == self.id)).all()

    @property
    def results(self) -> list[tuple[str | None, str]]:
        played_games = self.played_games
        players = self.meisterschaft.teilnehmer_liste
        res: list[tuple[str | None, str]] = []
        for player in players:
            if player == self:
                res.append(("#00F", "X"))
                continue
            found: bool = False
            for game in played_games:
                if not game.is_player(player):
                    continue
                game_result = game.result if game.player_1_id == self.id else -game.result
                found = True
                match game_result:
                    case 0:
                        res.append(("#990", "½"))
                    case 1:
                        res.append(("#090", "1"))
                    case 2:
                        res.append(("#0F0", "+"))
                    case -1:
                        res.append(("#900", "0"))
                    case -2:
                        res.append(("#F00", "-"))
                    case _:
                        logging.error(f"Unexpected result {game_result}")
                        res.append(("#000", "?"))
                break
            if not found:
                res.append((None, ""))
        res.append(("#0A0" if self.anzahl_spielfrei > 0 else None, "+" * self.anzahl_spielfrei))
        return res


class StadtmeisterschaftSpiel(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    player_1_id: Mapped[int] = db.Column(db.ForeignKey("stadtmeisterschaft_teilnehmer.id"))
    player_2_id: Mapped[int] = db.Column(db.ForeignKey("stadtmeisterschaft_teilnehmer.id"))
    result: Mapped[int] = db.Column(db.Integer)

    def is_player(self, player: StadtmeisterschaftTeilnehmer) -> bool:
        return self.player_1_id == player.id or self.player_2_id == player.id
