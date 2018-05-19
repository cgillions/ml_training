from flask.json import jsonify

from utils.db_utils import get_database


def get():
    models = []
    database_conn = get_database()
    cursor = database_conn.cursor()
    cursor.execute("""
                        SELECT name, description 
                        FROM public."Model"
                        """)

    for model in cursor.fetchall():
        models.append({"name": model[0], "description": model[1]})

    cursor.close()
    database_conn.close()
    return jsonify({"models": models})
