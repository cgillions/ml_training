import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)
DATABASE_URL = os.environ["DATABASE_URL"]


# Method to return a database connection.
def get_database():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@app.route("/trials", methods=["GET", "POST"])
def trials():
    if request.method == "POST":
        return Trial.post(request.form["user_id"], request.files["file"], request.form["user_id"])

    else:  # if request.method == "GET":
        return jsonify(Trial.get())


@app.route("/activities", methods=["GET"])
def activities():
    return jsonify(Activity.get())


def json_error(error, detail):
    return jsonify({
        "error": {
            "message": error,
            "detail": detail
        }
    })


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)


# Avoid circular dependencies.
from model.trial import Trial
from model.activity import Activity
