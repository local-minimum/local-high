import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

import click
import psycopg2
from psycopg2.extensions import cursor, connection
from flask import current_app, g
from flask.app import Flask
from flask.cli import with_appcontext

_DBNAME = os.environ.get("LOCALHIGH_DBNAME", "localhigh")
_USER = os.environ.get("LOCALHIHG_DBUSER", "localhigh-user")
_USER_PWD = os.environ.get("LOCALHIHG_DBUSER_PWD", "")
_ADMIN_USER = os.environ.get("LOCALHIGH_DBADMIN", "localhigh-admin")
_ADMIN_USER_PWD = os.environ.get("LOCALHIGH_DBADMIN_PWD", "")
_HOST = os.environ.get("LOCALHIGH_DBHOST", 'localhost')
_PORT = os.environ.get("LOCALHIGH_DBPORT")

def get_connection(as_admin: bool = False) -> connection:
    return psycopg2.connect(
        dbname=_DBNAME,
        user=_ADMIN_USER if as_admin else _USER,
        password=_ADMIN_USER_PWD if as_admin else _USER_PWD,
        host=_HOST,
        port=_PORT,
    )


def get_db(as_admin: bool = False) -> connection:
    if as_admin:
        return get_connection(as_admin)
    if 'db' not in g:
        g.db = get_connection()
    return g.db


@contextmanager
def transaction(as_admin: bool = False) -> Iterator[cursor]:
    conn = get_db(as_admin=as_admin)
    with (
        conn,
        conn.cursor() as curs,
    ):
        yield curs



def close_db(e: BaseException = None):
    msg = "Tearing down db connection."
    if e is not None:
        logging.exception(msg)
    else:
        logging.info(msg)
    db: Optional[connection] = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    with (
        transaction(as_admin=True) as curs
    ):
        schema = (
            Path(__file__).parent.parent / Path('configuration/schema.sql')
        ).read_text()
        curs.execute(schema)


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
