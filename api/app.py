import csv
import io

import pymysql
import sqlalchemy
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_sse import sse

from api.models import Product, db

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/PRODUCT"
app.register_blueprint(sse, url_prefix="/events")

db.init_app(app)

api = Api(app)
CORS(app)


class ProductResource(Resource):
    def get(self):
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            db="PRODUCT",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with connection.cursor() as cursor:
            sql_statement = """
            SELECT * FROM product
            """
            cursor.execute(sql_statement)
            result = cursor.fetchall()

        return result

        # products = Product.query.all()
        # return_json = []
        # for item in products:
        #     return_json.append({'id':item.id, 'sku':item.sku, 'name':item.name, 'description':item.description})

        # return return_json

    def post(self):
        # while True:
        file = request.files["file"]
        stream = io.StringIO(file.stream.read().decode("UTF8"))
        # sse.publish({"message": "Hello!"}, type='greeting')
        reader = csv.DictReader(stream)
        objects = list(reader)
        total_records = len(objects)
        total_added = 0
        for line in objects:
            product = Product(
                name=line["name"], sku=line["sku"], description=line["description"]
            )
            added = self.process_product_record(product=product, line=line)
            if added is True:
                total_added += 1
            sse.publish(
                {"message": "Total:" + str(total_added) + "/" + str(total_records)}
            )
        # sse.publish({"message": 'Completed'})

    def delete(self):
        try:
            num_rows_deleted = db.session.query(Product).delete()
            db.session.commit()
        except:
            db.session.rollback()

    def process_product_record(self, product, line):
        try:
            db.session.add(product)
            db.session.commit()
            # sse.publish({"message": line['name'] + ' added!'})
            return True
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            # sse.publish({"message": line['name'] + ' Discarded, sku duplicate!'})
            return False


api.add_resource(ProductResource, "/product")
