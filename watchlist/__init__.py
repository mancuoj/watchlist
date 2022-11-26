import os
import sys

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_babel import Babel, _

WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
app.config["SQLALCHEMY_DATABASE_URI"] = prefix + os.path.join(
    os.path.dirname(app.root_path), os.getenv("DATABASE_FILE", "data.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["LANGUAGES"] = ["en", "zh"]

db = SQLAlchemy(app)
babel = Babel(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = _("请登录！")


@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User

    user = User.query.get(int(user_id))
    return user


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config["LANGUAGES"])


from watchlist import views, errors, commands
