import psycopg2
import os

DATABASE_URL = os.environ["DATABASE_URL"]


# Method to return a database connection.
def get_database():
    return psycopg2.connect(DATABASE_URL, sslmode="require")
