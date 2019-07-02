from flask import request
from flask_restful import Resource
from models import Webhook, get_connection


class WebhookResource(Resource):
    """
    This Resource is used for managing the Webhooks.
    """

    @staticmethod
    def get():
        """
        The GET method returns a list of all existing webhooks from the database.
        :return: return_json: A list of webhooks
        """
        webhooks = Webhook.query.all()
        return_json = []
        for item in webhooks:
            return_json.append({"id": item.id, "url": item.url})

        return return_json

    @staticmethod
    def post():
        """
        The POST method is used to insert/update a webhook in the database..
        """
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
            raise e
        connection.close()

    @staticmethod
    def delete(id):
        """
        The DELETE method is used to delete a webhook from the database..
        :return: return_json: A list of webhooks
        """
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
            raise e
        connection.close()
