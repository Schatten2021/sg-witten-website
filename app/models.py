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
    victors: Mapped["SparkassenJugendOpenVictors"] = relationship()


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
