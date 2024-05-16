import random
import string

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config["SECRET_KEY"] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                                   for _ in range(64))
app.secret_key = app.config['SECRET_KEY']

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)


from app.models import *
from app.routes import *

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
