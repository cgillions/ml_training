from flask import jsonify
import psycopg2
import os

DATABASE_URL = \
    os.environ["DATABASE_URL"]
    # "postgres://ebncaoihiytsjs:e2bdbacf5f15757757dba02947de9484da7a02cd6318220e8c26b5fc5ce7de4b@ec2-54-228-181-43.eu-west-1.compute.amazonaws.com:5432/d7b793kte97uqb"


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
