import csv
import io

from flask import jsonify, request
from flask_restful import Resource
from models import Product, db, get_connection
from tasks import trigger_webhooks, upload_product_csv_records


class ProductResource(Resource):
    """
    The Product Resource is used to handle all operations related to Product
    """

    @staticmethod
    def get() -> object:
        """
        The GET method is used to return a list of all the products present in the database
        :return: list of products in json
        """
        connection = get_connection()

        with connection.cursor() as cursor:
            sql_statement = """
            SELECT * FROM product
            """
            cursor.execute(sql_statement)
            result = cursor.fetchall()
        connection.close()

        # Using pymysql fetch as it is faster that loading SQLAlchemy objects
        # SQLAlchemy method is commented out

        # products = Product.query.all()
        # result = []
        # for item in products:
        #     result.append({'id':item.id, 'sku':item.sku, 'name':item.name, 'description':item.description})

        return result

    @staticmethod
    def post(sku=None):
        """
        POST method is used for creating/updating the product records.
        If sku is none, then assumes that a CSV file with records is present in the request body.
        If sku is given tries to create/update a record with the given sku.
        :param sku:
        :return:
        """
        if sku is None:
            # If sku is None, assume file is present in the request
            file = request.files["file"]

            # Read the CSV file and get unique records from it
            stream = io.StringIO(file.stream.read().decode("UTF8"))
            reader = csv.DictReader(stream)
            unique_records = [dict(y) for y in set(tuple(x.items()) for x in reader)]
            # Send the list of records to worker for processing
            upload_product_csv_records.send(unique_records)
            trigger_webhooks.send("CSV Upload in progress!")

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
            trigger_webhooks.send(
                f"Product with sku {sku} "
                f"updated, name is {name} and description is {description}."
            )

        return jsonify({"message": "Success"})

    @staticmethod
    def put():
        """
        The PUT method is invoked for inserting an individual record into the database.
        In case of item with the same SKU already existing, the existing item is updated with
        the given form parameters.
        """
        request_body = request.json
        connection = get_connection()
        name = str(request_body["name"]).strip()
        active = str(request_body["active"]).strip()
        description = str(request_body["description"]).strip()
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
        params = (sku, name, description, active, name, description, active)
        cursor.execute(sql_statement, params)
        connection.commit()

        connection.close()
        trigger_webhooks.send(
            f"Product with sku {sku} "
            f"added, name is {name} and description is {description}."
        )
        return jsonify({"message": "Success"})

    @staticmethod
    def delete(sku=None):
        """
        The
        :param sku: Optional parameter. If sku is None, then all the records are deleted.
        If sku is provided, only deletes the item with given sku.
        :return:
        """
        if sku is None:
            try:
                db.session.query(Product).delete()
                db.session.commit()
            except:
                db.session.rollback()
            trigger_webhooks.send(f"Deleted all products!")
        else:
            try:
                Product.query.filter_by(sku=sku).delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
            trigger_webhooks.send(f"Product with sku {sku} deleted.")

        return jsonify({"message": "Success"})
