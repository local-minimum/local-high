from typing import Optional
from flask_login import UserMixin
import psycopg2
from .db import transaction
import logging


class User(UserMixin):
    def __init__(self, id: str, name: str, email: str) -> None:
        self.id = id
        self.name = name
        self.email = email

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        with transaction() as curs:
            try:
                curs.execute("SELECT * FROM users WHERE id = %s LIMIT 1;", (user_id,)) 
                (id, name, email) = curs.fetchone()
            except psycopg2.Error:
                logging.exception(f"Unexpected error getting {user_id} user info")
                return None
            except TypeError:
                logging.warning(f"Attempt to get unknown user id {user_id}")
                return None
            except ValueError:
                logging.exception("User table returned unexpected number of columns")
                return None
            return User(id, name, email)

    @staticmethod
    def create(id: str, name: str, email: str) -> "User":
        with transaction() as curs:
            try:
                curs.execute(
                    "INSERT INTO users (id, name, email) VALUES (%s, %s, %s)",
                    (id, name, email),
                )
            except psycopg2.Error:
                logging.exception("Failed to add user.")
        
        user = User.get(id)
        assert user is not None
        return user
