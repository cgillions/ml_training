from utils.db_utils import get_database, get_attributes
from model.activity import Activity
from flask import jsonify


def activity_endpoint():
    return jsonify({"activities": get()})


def get():
    activities = []
    database_conn = get_database()
    cursor = database_conn.cursor()
    cursor.execute("SELECT (id, name) FROM public.\"Activity\" ORDER BY id ASC;")

    for activity in cursor:
        attrs = get_attributes(activity[0])
        activities.append(Activity(attrs[0], attrs[1]).serialize())

    cursor.close()
    database_conn.close()
    return activities