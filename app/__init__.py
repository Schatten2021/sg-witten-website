import random
import string

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config["SECRET_KEY"] = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                                   for _ in range(64))
app.secret_key = app.config['SECRET_KEY']

# EMAIL setup
app.config["MAIL_SERVER"] = environ.get("MAIL_SERVER")
app.config["MAIL_USERNAME"] = environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = environ.get("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login_manager = LoginManager(app)

from app.models import *
from app.routes import *


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))
