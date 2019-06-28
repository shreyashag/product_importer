from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sse import sse

from models import db
from resources import ProductResource
from webhooks import WebhookResource
from tasks import flask_dramatiq_obj

from dramatiq.brokers.redis import RedisBroker
import os


def create_app():
    app = Flask(__name__)
    app.config["REDIS_URL"] = "redis://" + os.environ['REDIS_HOST']
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://"
        + os.environ["DB_USERNAME"]
        + ":"
        + os.environ["DB_PASSWORD"]
        + "@"
        + os.environ["DB_HOST"]
        + ":"
        + os.environ["DB_PORT"]
        + "/"
        + os.environ["DB_SCHEMA"]
    )
    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PORT = os.environ["REDIS_PORT"]
    REDIS_DB = os.environ["REDIS_DB"]
    app.config["DRAMATIQ_BROKER"] = RedisBroker
    app.config["DRAMATIQ_BROKER_URL"] = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    app.register_blueprint(sse, url_prefix="/events")
    flask_dramatiq_obj.init_app(app)
    db.init_app(app)
    api = Api(app)
    CORS(app)
    api.add_resource(ProductResource, "/product/", "/product/<sku>")
    api.add_resource(WebhookResource, "/webhook/", "/webhook/<id>")
    return app


app = create_app()

if __name__ == "__main__":
    # app = create_app()
    pass
