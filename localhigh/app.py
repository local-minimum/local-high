import logging
import os

import psycopg2
from flask import Flask
from flask_login import LoginManager

from .gateways.db import init_app
from .gateways.user import User
from .routes import authentication, index


def get_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get('LOCALHIGH_SECRET_KEY') or os.urandom(24)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    init_app(app)
    index.register_routes(app)
    authentication.register_routes(app)
    return app
