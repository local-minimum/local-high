import logging
import os
from typing import Iterator, Optional
from flask.app import Flask
import psycopg2
from flask import current_app, g
from pathlib import Path
import click
from flask.cli import with_appcontext
from contextlib import contextmanager

_DBNAME = os.environ.get("LOCALHIGH_DBNAME", "localhigh")
_USER = os.environ.get("LOCALHIHG_DBUSER", "localhigh-user")
_USER_PWD = os.environ.get("LOCALHIHG_DBUSER_PWD", "")
_ADMIN_USER = os.environ.get("LOCALHIGH_DBADMIN", "localhigh-admin")
_ADMIN_USER_PWD = os.environ.get("LOCALHIGH_DBADMIN_PWD", "")
_HOST = os.environ.get("LOCALHIGH_DBHOST", 'localhost')
_PORT = os.environ.get("LOCALHIGH_DBPORT")

def get_connection(as_admin: bool = False) -> psycopg2.connection:
    return psycopg2.connect(
        dbname=_DBNAME,
        user=_ADMIN_USER if as_admin else _USER,
        password=_ADMIN_USER_PWD if as_admin else _USER_PWD,
        host=_HOST,
        port=_PORT,
    )


def get_db() -> psycopg2.connection:
    if 'db' not in g:
        g.db = get_connection()
    return g.db


@contextmanager
def transaction(as_admin: bool = False) -> Iterator[psycopg2.cursor]:
    conn = get_db()
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
    db: Optional[psycopg2.connection] = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    with (
        current_app.open_resource(
            Path('configuration/schema.sql'),
        ) as fh,
        transaction(as_admin=True) as curs
    ):
        curs.execute(fh.read().decode('utf8'))


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialzied the database')