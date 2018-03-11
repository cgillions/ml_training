from flask import jsonify
import psycopg2
import os

DATABASE_URL = os.environ["DATABASE_URL"]


# Method to return a database connection.
def get_database():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def get_attributes(db_response):
    # Remove brackets from the response.
    db_response = db_response[1:-1]

    # Strip extra quotation marks.
    db_response = db_response.replace("\"", "")

    # Split the attributes.
    return db_response.split(",")


def json_error(error, detail):
    return jsonify({
        "error": {
            "message": error,
            "detail": detail
        }
    })
