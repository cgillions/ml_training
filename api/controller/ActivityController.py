from utils.db_utils import get_database
from api.model.activity import Activity
from flask import jsonify


def get():
    activities = []
    database_conn = get_database()
    cursor = database_conn.cursor()
    cursor.execute("""
                    SELECT id, name 
                    FROM public."Activity" 
                    ORDER BY id ASC;
                    """)

    for activity in cursor.fetchall():
        activities.append(Activity(activity[0], activity[1]).__dict__)

    cursor.close()
    database_conn.close()
    return jsonify({"activities": activities})
