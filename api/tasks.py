import random

import requests
from flask_dramatiq import Dramatiq
from flask_sse import sse
from models import Webhook, get_connection

# Initialise the dramatiq object, that is later called for decorating the worker methods
flask_dramatiq_obj = Dramatiq()


@flask_dramatiq_obj.actor()
def upload_product_csv_records(csv_records: list) -> None:
    """
    This is the background function that is responsible for uploading the CSV records onto the database.
    :param csv_records: list of product records
    """
    total_records = len(csv_records)
    connection = get_connection()

    cursor = connection.cursor()
    for index, product_dict in enumerate(csv_records):
        # Use Upsert logic as application dictates that record must be updated
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
            random.choice([0, 1]),
        )
        cursor.execute(sql_statement, params)
        # Publish SSE event on flask sse endpoint
        sse.publish(
            {
                "message": "Total:" + str(index + 1) + "/" + str(total_records),
                "total": total_records,
                "completed": index + 1,
            }
        )
        # Commit the changes to the database
        connection.commit()

    # Close connection after work is completed.
    connection.close()


@flask_dramatiq_obj.actor()
def trigger_webhooks(webhook_message) -> None:
    """
    This is the background function to trigger webhooks.
    :param webhook_message: The webhook_message that needs to be sent to the webhooks.
    """

    webhooks = Webhook.query.all()
    for item in webhooks:
        if item.url.startswith("http://requestbin"):
            requests.post(item.url, data={"message": webhook_message})
