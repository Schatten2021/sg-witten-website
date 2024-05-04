from app import app
from flask import render_template, flash, redirect, url_for
from app.models import SparkassenJugendOpen, Turnier


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/Turniere')
def turniere():
    cups: list[Turnier] = Turnier.query.all()
    return render_template("Turniere.html", cups=cups)

@app.route('/SparkassenJugendOpen')
def spo():
    cups: list[SparkassenJugendOpen] = SparkassenJugendOpen.query.all()
    return render_template("SparkassenOpen.html", cups=cups)
