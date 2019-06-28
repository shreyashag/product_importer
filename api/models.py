from flask_sqlalchemy import SQLAlchemy
import pymysql
import os

db = SQLAlchemy()


def get_connection():
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

    def __repr__(self):
        return "<Product %r>" % self.id


class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024), unique=True)

    def __repr__(self):
        return "<Webhook %r>" % self.url
