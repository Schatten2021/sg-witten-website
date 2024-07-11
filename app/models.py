import re
from datetime import datetime
from typing import Optional

from sqlalchemy import or_, and_, Column, Integer, ForeignKey, Boolean, DateTime, String, Float
from sqlalchemy.orm import Mapped, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


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
    def vorstands_rollen(self) -> list["VorstandsRolle"]:
        return VorstandsRolle.query.filter_by(person_id=self.id).all()

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
    description: Mapped[str] = Column(String)
    teilnehmer: Mapped[list["Teilnehmer"]] = relationship("Teilnehmer")
    # jeder gegen jeden; Schweizer; K.O.
    runden_art: Mapped[str] = Column(String)
    display_dwz: Mapped[bool] = Column(Boolean, default=False)
    display_age_group: Mapped[bool] = Column(Boolean, default=False)

    @property
    def termine(self) -> list["Termin"]:
        return Termin.query.filter_by(turnier_id=self.id).all()

    __mapper_args__ = {
        "polymorphic_identity": "Turnier",
        "polymorphic_on": runden_art
    }


# Turnierarten
class FFATurnier(Turnier):
    __mapper_args__ = {
        "polymorphic_identity": "jeder gegen jeden"
    }


class SchweizerTurnier(Turnier):
    __mapper_args__ = {
        "polymorphic_identity": "Schweizer"
    }


class KOTurnier(Turnier):
    __mapper_args__ = {
        "polymorphic_identity": "K.O."
    }


# Teilnehmer
class Teilnehmer(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    person_id: Mapped[int] = Column(ForeignKey("person.id"))
    person: Mapped[Person] = relationship("Person")
    turnier_id: Mapped[int] = Column(ForeignKey("turnier.id"))
    turnier: Mapped[Turnier] = relationship("Turnier", back_populates="teilnehmer")
    turnier_type: Mapped[str] = Column(String)
    vereins_id: Mapped[int] = Column(ForeignKey("verein.id"))
    verein: Mapped["Verein"] = relationship("Verein")
    dwz: Mapped[float] = Column(Float, nullable=True)
    age_group: Mapped[int] = Column(Integer, nullable=True)

    @property
    def games(self) -> list["Game"]:
        return Game.query.filter(or_(Game.player1 == self, Game.player2 == self)).all()

    @property
    def points(self) -> float:
        return sum(game.getPoints(self) for game in self.games)

    __mapper_args__ = {
        "polymorphic_identity": "Teilnehmer",
        "polymorphic_on": turnier_type,
    }


class FFATeilnehmer(Teilnehmer):
    def get_result_against(self, other: "FFATeilnehmer") -> int | None:
        game = Game.query.filter(or_(and_(Game.player1 == self, Game.player2 == other),
                                     and_(Game.player2 == self, Game.player1 == other))).first()
        if game is None:
            return None
        if game.player1 == self:
            return game.result
        else:
            return -game.result

    __mapper_args__ = {
        "polymorphic_identity": "jeder gegen jeden"
    }


class SchweizerTeilnehmer(Teilnehmer):
    __mapper_args__ = {
        "polymorphic_identity": "Schweizer"
    }


class KOTeilnehmer(Teilnehmer):
    __mapper_args__ = {
        "polymorphic_identity": "K.O."
    }


# andere Turnier parameter
class Termin(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    turnier_id: Mapped[int] = Column(ForeignKey("turnier.id"))
    turnier: Mapped[Turnier] = relationship("Turnier")
    start: Mapped[datetime] = Column(DateTime)
    end: Mapped[datetime] = Column(DateTime)


class Verein(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)


class Game(db.Model):
    id: Mapped[int] = Column(Integer, primary_key=True)
    result: Mapped[int] = Column(Integer)
    player1_id: Mapped[int] = Column(ForeignKey("teilnehmer.id"))
    player1: Mapped[Teilnehmer] = relationship("Teilnehmer", foreign_keys=[player1_id])
    player2_id: Mapped[int] = Column(ForeignKey("teilnehmer.id"))
    player2: Mapped[Teilnehmer] = relationship("Teilnehmer", foreign_keys=[player2_id])

    def getPoints(self, player: Teilnehmer) -> float:
        if self.result == 0:
            return .5
        if player == self.player1:
            if self.result > 0:
                return 1
            return 0
        if self.result > 0:
            return 0
        return 1
