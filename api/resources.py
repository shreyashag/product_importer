import csv
import io
import os
import pymysql
import sqlalchemy
from flask import request, jsonify
from flask_restful import Api, Resource

import requests
from models import Product, db, get_connection, Webhook
from tasks import flask_dramatiq_obj
import random
from flask_sse import sse


@flask_dramatiq_obj.actor()
def upload_product_csv_records(csv_records):

    total_records = len(csv_records)

    total_added = 0
    connection = get_connection()

    cursor = connection.cursor()
    for index, product_dict in enumerate(csv_records):
        sql_statement = """
        INSERT INTO product (sku, name, description, active)
        VALUES (%s,%s,%s, %s)
        ON DUPLICATE KEY UPDATE
        name=%s,
        description=%s,
        active=%s;
        """
        params = (
            product_dict["sku"].strip(),
            product_dict["name"].strip(),
            product_dict["description"].strip(),
            random.choice([0, 1]),
            product_dict["name"].strip(),
            product_dict["description"].strip(),
            random.choice([0, 1])
        )
        cursor.execute(sql_statement, params)
        sse.publish(
            {
                "message": "Total:" + str(index + 1) + "/" + str(total_records),
                "total": total_records,
                "completed": index + 1,
            }
        )
        connection.commit()
    connection.close()


class ProductResource(Resource):
    def get(self):
        connection = get_connection()

        with connection.cursor() as cursor:
            sql_statement = """
            SELECT * FROM product
            """
            cursor.execute(sql_statement)
            result = cursor.fetchall()
        connection.close()
        return result
        # Using pymysql fetch as it is faster that loading SQLAlchemy objects
        # SQLAlchemy method is commented out

        # products = Product.query.all()
        # return_json = []
        # for item in products:
        #     return_json.append({'id':item.id, 'sku':item.sku, 'name':item.name, 'description':item.description})

        # return return_json

    def post(self, sku=None):
        if sku is None:
            file = request.files["file"]
            stream = io.StringIO(file.stream.read().decode("UTF8"))
            reader = csv.DictReader(stream)
            unique_records = [dict(y) for y in set(tuple(x.items()) for x in reader)]
            upload_product_csv_records.send(unique_records)
            webhooks = Webhook.query.all()
            for item in webhooks:
                if item.url.startswith("http://requestbin"):
                    r = requests.post(
                        item.url,
                        data={
                            "message": "CSV File uploaded with "
                            + str(len(unique_records))
                            + " records"
                        },
                    )

        else:
            request_body = request.json
            connection = get_connection()
            name = str(request_body["name"]).strip()
            description = str(request_body["description"]).strip()
            active = str(request_body["active"]).strip()[0]
            if active is True:
                active = 1
            elif active is False:
                active = 0
            cursor = connection.cursor()
            sql_statement = """
            UPDATE product 
            SET
            name=%s,
            active=%s,
            description=%s
            WHERE sku=%s;
            """
            params = (name, active, description, sku)
            cursor.execute(sql_statement, params)
            connection.commit()
            connection.close()

            webhooks = Webhook.query.all()
            for item in webhooks:
                if item.url.startswith("http://requestbin"):
                    r = requests.post(
                        item.url,
                        data={
                            "message": f"Product with sku {sku} "
                            f"updated, name is {name} and description is {description}."
                        },
                    )

        return jsonify({"message": "Success"})

    def put(self):
        request_body = request.json
        connection = get_connection()
        name = str(request_body["name"]).strip()
        active = str(request_body["active"]).strip()
        description str(= request_body["description"]).strip()
        sku = str(request_body["sku"]).strip()

        cursor = connection.cursor()
        sql_statement = """
        INSERT INTO product (sku, name, description, active)
        VALUES (%s,%s,%s, %s)
        ON DUPLICATE KEY UPDATE
        name=%s,
        description=%s,
        active=%s;
        """
        params = (
            request_body["sku"],
            request_body["name"],
            request_body["description"],
            request_body["active"][0],
            request_body["name"],
            request_body["description"],
            request_body["active"][0],
        )
        cursor.execute(sql_statement, params)
        connection.commit()

        connection.close()

        webhooks = Webhook.query.all()
        for item in webhooks:
            if item.url.startswith("http://requestbin"):
                r = requests.post(
                    item.url,
                    data={
                        "message": f"Product with sku {sku} "
                        f"added, name is {name} and description is {description}."
                    },
                )
        return jsonify({"message": "Success"})

    def delete(self, sku=None):
        webhooks = Webhook.query.all()
        if sku is None:
            try:
                num_rows_deleted = db.session.query(Product).delete()
                db.session.commit()
            except:
                db.session.rollback()
            for item in webhooks:
                if item.url.startswith("http://requestbin"):
                    r = requests.post(
                        item.url, data={"message": f"Deleted all products!"}
                    )
        else:
            try:
                Product.query.filter_by(sku=sku).delete()
                db.session.commit()
            except Exception as e:
                raise e
                db.session.rollback()
            for item in webhooks:
                if item.url.startswith("http://requestbin"):
                    r = requests.post(
                        item.url, data={"message": f"Product with sku {sku} deleted."}
                    )

        return jsonify({"message": "Success"})

    # @staticmethod
    # def add_product_to_db(product):
    #     try:
    #         # TODO: First try finding matching record.

    #         # If not exists, then add the record
    #         db.session.add(product)
    #         db.session.commit()
    #         return True

    #         # TODO: If exists, update the record
    #     except sqlalchemy.exc.IntegrityError as e:
    #         db.session.rollback()
    #         return False
