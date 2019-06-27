from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sse import sse

from api.models import db
from api.resources import ProductResource
from api.tasks import flask_dramatiq_obj

from dramatiq.brokers.redis import RedisBroker

REDIS_HOST = "localhost"


def create_app():
    app = Flask(__name__)
    app.config["REDIS_URL"] = "redis://localhost"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/PRODUCT"
    app.config["DRAMATIQ_BROKER"] = RedisBroker
    app.config["DRAMATIQ_BROKER_URL"] = f"redis://{REDIS_HOST}:6379/0"
    app.register_blueprint(sse, url_prefix="/events")
    flask_dramatiq_obj.init_app(app)
    db.init_app(app)
    api = Api(app)
    CORS(app)
    api.add_resource(ProductResource, "/product")
    return app


app = create_app()

if __name__ == "__main__":
    # app = create_app()
    pass
