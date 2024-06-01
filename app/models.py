import logging
from datetime import datetime
from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import or_, Column, Integer, ForeignKey, Boolean, DateTime, Float, String
from app import db
import re


class Person(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: str = Column(String)
    surname: str = Column(String)

    @property
    def account(self) -> Optional["Account"]:
        return Account.query.filter_by(person_id=self.id).first()

    @property
    def mannschaftsspieler(self) -> list["Mannschaftsspieler"]:
        return Mannschaftsspieler.query.filter_by(person_id=self.id).all()

    @property
    def sparkassen_jugend_open_teilnahmen(self) -> list["SparkassenJugendOpenTeilnehmer"]:
        return SparkassenJugendOpenTeilnehmer.query.filter_by(person_id=self.id).all()

    @property
    def stadtmeisterschaft_teilnahmen(self) -> list["StadtmeisterschaftTeilnehmer"]:
        return StadtmeisterschaftTeilnehmer.query.filter_by(person_id=self.id).all()

    @property
    def vorstands_rollen(self) -> list["VorstandsRolle"]:
        return VorstandsRolle.query.filter_by(person_id=self.id).all()

    @property
    def vereinspokal_teilnahmen(self) -> list["VereinspokalTeilnehmer"]:
        return VereinspokalTeilnehmer.query.filter_by(person_id=self.id).all()

    @property
    def shortened_surname(self) -> str:
        surnames = re.split(r"[- ]", self.surname)
        letters = [surname[0].upper() for surname in surnames if len(surname) > 0]
        return "".join(letters)


#
# Account management
#
class Role(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: str = Column(String)
    accounts: Mapped[list["Account"]] = relationship("Account", "role_account_association_table",
                                                     back_populates="roles")


class Account(db.Model):
    person_id: Mapped[int] = Column(ForeignKey("person.id"), primary_key=True)
    person: Mapped[Person] = relationship("Person")
    email: Mapped[str] = Column(String)
    password: Mapped[str] = Column(String)
    is_authenticated: Mapped[bool] = Column(Boolean, default=False)
    roles: Mapped[list[Role]] = relationship("Role", "role_account_association_table", back_populates="accounts")

    @property
    def is_admin(self) -> bool:
        admin_role: Role = Role.query.first()
        return admin_role is not None and admin_role in self.roles

    @property
    def authentication_requests(self) -> list["AuthenticationRequest"]:
        return AuthenticationRequest.query.filter_by(account_id=self.person.id).all()

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password, password)

    is_active: bool = True
    is_anonymous: bool = False

    def get_id(self):
        return self.person_id


class RoleAccountAssociationTable(db.Model):
    account_id: Mapped[int] = Column(ForeignKey("account.person_id"), primary_key=True)
    role_id: Mapped[int] = Column(ForeignKey("role.id"), primary_key=True)


class AuthenticationRequest(db.Model):
    id: Mapped[str] = Column(String, primary_key=True)
    account_id: Mapped[int] = Column(ForeignKey("account.person_id"), primary_key=True)
    account: Mapped[Account] = relationship()


#
# Mannschaftsmanagement
#
class Mannschaft(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)
    spieler: Mapped[list["Mannschaftsspieler"]] = relationship("Mannschaftsspieler", back_populates="mannschaft")


class Mannschaftsspieler(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    person_id: Mapped[int] = Column(ForeignKey("person.id"))
    person: Mapped[Person] = relationship()
    mannschaft_id: Mapped[int] = Column(ForeignKey("mannschaft.id"))
    mannschaft: Mapped[Mannschaft] = relationship("Mannschaft", back_populates="spieler")
    BrettNr: Mapped[int] = Column(Integer)
    ersatz: Mapped[bool] = Column(Boolean)

    def __lt__(self, other: "Mannschaftsspieler") -> bool:
        if self.ersatz != other.ersatz:
            return not self.ersatz and other.ersatz
        return self.BrettNr < other.BrettNr


#
# Vorstand
#

class VorstandsRolle(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    person_id: Mapped[Optional[int]] = Column(ForeignKey("person.id"))
    person: Mapped[Optional[Person]] = relationship("Person")
    email: Mapped[str] = Column(String)
    titel: Mapped[str] = Column(String)


#
# Turniere
#
class Turnier(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)
    date: Mapped[datetime] = Column(DateTime)


class Verein(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)


# Sparkassen Jugend Open
class SparkassenJugendOpen(db.Model):
    id: Mapped[int] = Column(ForeignKey("turnier.id"), primary_key=True)
    turnier: Mapped[Turnier] = relationship("Turnier")
    artikel: Mapped[str] = Column(String)
    teilnehmer: Mapped[list["SparkassenJugendOpenTeilnehmer"]] = relationship("SparkassenJugendOpenTeilnehmer",
                                                                              back_populates="turnier")

    @property
    def beste_teilnehmer(self) -> dict[int, list["SparkassenJugendOpenTeilnehmer"]]:
        maximum_points: dict[int, float] = {}
        for teilnehmer in self.teilnehmer:
            maximum_points.setdefault(teilnehmer.Jahrgang, 0)
            if maximum_points[teilnehmer.Jahrgang] < teilnehmer.points:
                maximum_points[teilnehmer.Jahrgang] = teilnehmer.points
        res: dict[int, list["SparkassenJugendOpenTeilnehmer"]] = {}
        for teilnehmer in self.teilnehmer:
            res.setdefault(teilnehmer.Jahrgang, [])
            if maximum_points[teilnehmer.Jahrgang] == teilnehmer.points:
                res[teilnehmer.Jahrgang].append(teilnehmer)
        return dict(sorted(res.items()))


class SparkassenJugendOpenTeilnehmer(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    person_id: Mapped[int] = Column(ForeignKey("person.id"))
    person: Mapped[Person] = relationship("Person")
    points: Mapped[float] = Column(Float)
    Jahrgang: Mapped[int] = Column(Integer)
    vereins_id: Mapped[int] = Column(ForeignKey("verein.id"))
    verein: Mapped[Verein] = relationship("Verein")
    turnier_id: Mapped[int] = Column(ForeignKey("sparkassen_jugend_open.id"))
    turnier: Mapped[SparkassenJugendOpen] = relationship("SparkassenJugendOpen", back_populates="teilnehmer")


# Stadtmeisterschaft
class Stadtmeisterschaft(db.Model):
    id: Mapped[int] = Column(ForeignKey("turnier.id"), primary_key=True)
    turnier: Mapped[Turnier] = relationship()
    teilnehmer: Mapped[list["StadtmeisterschaftTeilnehmer"]] = relationship("StadtmeisterschaftTeilnehmer",
                                                                            back_populates="turnier")

    @property
    def teilnehmer_liste(self) -> list["StadtmeisterschaftTeilnehmer"]:
        return sorted(self.teilnehmer, key=lambda x: x.rang)


class StadtmeisterschaftTeilnehmer(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    person_id: Mapped[int] = Column(ForeignKey("person.id"))
    person: Mapped[Person] = relationship("Person")
    turnier_id: Mapped[int] = Column(ForeignKey("stadtmeisterschaft.id"))
    turnier: Mapped[Stadtmeisterschaft] = relationship("Stadtmeisterschaft", back_populates="teilnehmer")
    dwz: Mapped[int] = Column(Integer)
    rang: Mapped[int] = Column(Integer)
    buchholz: Mapped[float] = Column(Float)
    punkte: Mapped[float] = Column(Float)
    freispiele: Mapped[int] = Column(Integer)
    vereins_id: Mapped[int] = Column(ForeignKey("verein.id"))
    verein: Mapped[Verein] = relationship("Verein")

    @property
    def spiele(self) -> list["StadtmeisterschaftSpiel"]:
        return StadtmeisterschaftSpiel.query.filter(or_(StadtmeisterschaftSpiel.spieler1_id == self.id,
                                                        StadtmeisterschaftSpiel.spieler2_id == self.id)).all()

    @property
    def results(self) -> list[tuple[Optional[str], str]]:
        played_games: list[StadtmeisterschaftSpiel] = self.spiele
        players: list[StadtmeisterschaftTeilnehmer] = self.turnier.teilnehmer_liste
        res: list[tuple[Optional[str], str]] = []
        player_results: dict[StadtmeisterschaftTeilnehmer, tuple[str, str]] = {}
        for game in played_games:
            player_results[game.get_other(self)] = game.get_result_str(self)
        for player in players:
            if player == self:
                res.append(("#00A", "X"))
            elif player in player_results:
                res.append(player_results[player])
            else:
                res.append((None, ""))
        res.append(("#0A0" if self.freispiele > 0 else None, "+" * self.freispiele))
        res.append((None, str(self.punkte)))
        return res


class StadtmeisterschaftSpiel(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    spieler1_id: Mapped[int] = Column(ForeignKey("stadtmeisterschaft_teilnehmer.id"))
    spieler2_id: Mapped[int] = Column(ForeignKey("stadtmeisterschaft_teilnehmer.id"))
    result: Mapped[int] = Column(Integer)

    def get_result(self, player: StadtmeisterschaftTeilnehmer) -> Optional[int]:
        if self.spieler1_id == player.id:
            return self.result
        elif self.spieler2_id == player.id:
            return self.result
        else:
            return None

    def get_other(self, player: StadtmeisterschaftTeilnehmer) -> StadtmeisterschaftTeilnehmer:
        if self.spieler1_id == player.id:
            return StadtmeisterschaftTeilnehmer.query.get(self.spieler2_id)
        return StadtmeisterschaftTeilnehmer.query.get(self.spieler1_id)

    def get_result_str(self, player: StadtmeisterschaftTeilnehmer) -> tuple[str, str]:
        game_res: int = self.get_result(player)
        if game_res is None:
            return "", ""
        match game_res:
            case 0:
                return "#990", "½"
            case 1:
                return "#090", "1"
            case 2:
                return "#0F0", "+"
            case -1:
                return "#900", "0"
            case -2:
                return "#F00", "-"
            case _:
                logging.error(f"Unexpected result {game_res}")
                return "#000", "?"

    @property
    def spieler1(self):
        return StadtmeisterschaftTeilnehmer.query.get(self.spieler1_id)

    @property
    def spieler2(self):
        return StadtmeisterschaftTeilnehmer.query.get(self.spieler2_id)


# Vereinspokal
class Vereinspokal(Turnier):
    id: Mapped[int] = Column(ForeignKey("turnier.id"), primary_key=True)
    teilnehmer: Mapped[list["VereinspokalTeilnehmer"]] = relationship("VereinspokalTeilnehmer",
                                                                      back_populates="turnier")

    __mapper_args__ = {"polymorphic_identity": "vereinspokal"}

    @property
    def spiele(self) -> list["VereinspokalSpiel"]:
        return sorted(VereinspokalSpiel.query.filter_by(turnier_id=self.id).all(), key=lambda x: x.runde)

    @property
    def runden(self) -> list[list["VereinspokalSpiel"]]:
        all_rounds: list[list["VereinspokalSpiel"]] = [[] for _ in range(self.spiele[-1].runde)]
        for spiel in self.spiele:
            all_rounds[spiel.runde - 1].append(spiel)

        # go through all rounds except last one.
        if len(all_rounds) < 2:
            return all_rounds
        for i in reversed(range(len(all_rounds) - 1)):
            prev_player_games: dict[VereinspokalTeilnehmer, int] = {}
            for index, game in enumerate(all_rounds[i+1]):
                prev_player_games[game.weiss] = index * 2
                prev_player_games[game.schwarz] = index * 2 + 1

            def get_index_of_game(game: VereinspokalSpiel) -> int:
                if game.weiss in prev_player_games:
                    return prev_player_games[game.weiss]
                elif game.schwarz in prev_player_games:
                    return prev_player_games[game.schwarz]
                return 0

            all_rounds[i] = sorted(all_rounds[i], key=get_index_of_game)

        return all_rounds


class VereinspokalSpiel(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    turnier_id: Mapped[int] = Column(ForeignKey("vereinspokal.id"))
    turnier: Mapped[Vereinspokal] = relationship("Vereinspokal")
    weiss_id: Mapped[int] = Column(ForeignKey("vereinspokal_teilnehmer.id"))
    weiss: Mapped["VereinspokalTeilnehmer"] = relationship("VereinspokalTeilnehmer", foreign_keys=[weiss_id])
    schwarz_id: Mapped[int] = Column(ForeignKey("vereinspokal_teilnehmer.id"))
    schwarz: Mapped["VereinspokalTeilnehmer"] = relationship("VereinspokalTeilnehmer", foreign_keys=[schwarz_id])
    weiss_gewonnen: Mapped[bool] = Column(Boolean)
    result: Mapped[None] = Column(Integer)
    runde: Mapped[int] = Column(Integer)


class VereinspokalTeilnehmer(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    person_id: Mapped[int] = Column(ForeignKey("person.id"))
    person: Mapped[Person] = relationship("Person")
    turnier_id: Mapped[int] = Column(ForeignKey("vereinspokal.id"))
    turnier: Mapped[Vereinspokal] = relationship("Vereinspokal", back_populates="teilnehmer")

    @property
    def spiele(self) -> list[VereinspokalSpiel]:
        return Vereinspokal.query.filter_by(or_(self.id == VereinspokalSpiel.weiss_id,
                                                self.id == VereinspokalSpiel.schwarz_id)).all()
