import csv
import io

import pymysql
import sqlalchemy
from flask import request, jsonify
from flask_restful import Api, Resource


from models import Webhook, db, get_connection


class WebhookResource(Resource):
    def get(self):
        webhooks = Webhook.query.all()
        return_json = []
        for item in webhooks:
            return_json.append({"id": item.id, "url": item.url})

        return return_json

    def post(self):
        request_body = request.json
        connection = get_connection()

        cursor = connection.cursor()
        sql_statement = """
        INSERT INTO webhook (url)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE
        url=%s;
        """
        params = (request_body["url"], request_body["url"])
        try:
            cursor.execute(sql_statement, params)
            connection.commit()
        except Exception as e:
            pass
        connection.close()

    def delete(self, id):
        connection = get_connection()

        cursor = connection.cursor()
        sql_statement = """
        DELETE FROM webhook
        WHERE id=%s
        """
        params = id
        try:
            cursor.execute(sql_statement, params)
            connection.commit()
        except Exception as e:
            pass
        connection.close()
