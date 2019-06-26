from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sse import sse

from api.models import db
from api.resources import ProductResource


def create_app():
    app = Flask(__name__)
    app.config["REDIS_URL"] = "redis://localhost"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/PRODUCT"
    app.register_blueprint(sse, url_prefix="/events")
    db.init_app(app)
    api = Api(app)
    CORS(app)
    api.add_resource(ProductResource, "/product")
    return app


app = create_app()

if __name__ == "__main__":
    # app = create_app()
    pass
