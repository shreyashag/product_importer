import csv
import io

import pymysql
import sqlalchemy
from flask import request
from flask_restful import Api, Resource


from api.models import Product, db
from api.tasks import flask_dramatiq_obj

from flask_sse import sse


def get_db_records():
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
    connection.close()
    return result


@flask_dramatiq_obj.actor()
def upload_product_csv_records(csv_records):

    total_records = len(csv_records)

    total_added = 0
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        db="PRODUCT",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    cursor = connection.cursor()
    for index, product_dict in enumerate(csv_records):
        sql_statement = """
        INSERT INTO product (sku, name, description)
        VALUES (%s,%s,%s)
        ON DUPLICATE KEY UPDATE
        name=%s,
        description=%s;
        """
        params = (
            product_dict["sku"],
            product_dict["name"],
            product_dict["description"],
            product_dict["name"],
            product_dict["description"],
        )
        cursor.execute(sql_statement, params)
        sse.publish(
            {
                "message": "Total:" + str(index + 1) + "/" + str(total_records),
                "total": str(total_records),
                "completed": str(index + 1),
            }
        )
        connection.commit()
    connection.close()


class ProductResource(Resource):
    def get(self):
        return get_db_records()
        # Using pymysql fetch as it is faster that loading SQLAlchemy objects
        # SQLAlchemy method is commented out

        # products = Product.query.all()
        # return_json = []
        # for item in products:
        #     return_json.append({'id':item.id, 'sku':item.sku, 'name':item.name, 'description':item.description})

        # return return_json

    def post(self):
        file = request.files["file"]
        stream = io.StringIO(file.stream.read().decode("UTF8"))
        reader = csv.DictReader(stream)
        unique_records = [dict(y) for y in set(tuple(x.items()) for x in reader)]
        upload_product_csv_records.send(unique_records)

    def delete(self):
        try:
            num_rows_deleted = db.session.query(Product).delete()
            db.session.commit()
        except:
            db.session.rollback()

    @staticmethod
    def add_product_to_db(product):
        try:
            # TODO: First try finding matching record.

            # If not exists, then add the record
            db.session.add(product)
            db.session.commit()
            return True

            # TODO: If exists, update the record
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            return False
