from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(1024), nullable=False)

    def __repr__(self):
        return "<Product %r>" % self.id
