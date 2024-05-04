from datetime import datetime

from sqlalchemy import ForeignKey, Column
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
