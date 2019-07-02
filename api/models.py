import os

import pymysql
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_connection() -> pymysql.connections.Connection:
    """
    This function is used to obtain a connection to the Database
    :return: pymysql connection
    """
    return pymysql.connect(
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        db=os.environ["DB_SCHEMA"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return "<Product %r>" % self.id


class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024), unique=True)

    def __repr__(self):
        return "<Webhook %r>" % self.url
