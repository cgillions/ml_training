import os
import psycopg2
from flask import Flask, request, jsonify, redirect, url_for
from model.trial import Trial

app = Flask(__name__)
DATABASE_URL = os.environ["DATABASE_URL"]


# Method to return a database connection.
def get_database():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@app.route("/trials/add", methods=["GET", "POST"])
def add_trial():
    if request.method == "POST":
        return Trial.post(request.form["user_id"], request.files["file"], request.form["user_id"])

    else:  # if request.method == "GET":
        return jsonify(Trial.get())


def json_error(error, detail):
    return jsonify({
        "error": {
            "message": error,
            "detail": detail
        }
    })


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
