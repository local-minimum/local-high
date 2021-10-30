import logging
import os

from flask import Flask
from flask_login import (
    LoginManager,
)

from localhigh.gateways.db import init_db_command
import psycopg2
from localhigh.gateways.user import User 


def get_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get('LOCALHIGH_SECRET_KEY') or os.urandom(24)

    login_manager = LoginManager()
    login_manager.init_app(app)

    try:
        init_db_command()
    except psycopg2.DatabaseError:
        logging.exception("DB initiation caused exception")
    

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    return app