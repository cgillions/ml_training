import os
from flask import Flask, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "../data/trials"
ALLOWED_EXTENSIONS = {"txt"}


@app.route("/trials/add", methods=["GET", "POST"])
def add_trial():
    if request.method == "POST":
        if "user_id" not in request.form:
            return json_error("user_id is required.", "We need a user ID to link the trial to.")

        if "activity_name" not in request.form:
            return json_error("activity_name is required.", "We need to know the activity so that we can train the AI.")

        if "file" not in request.files:
            return json_error("file is required.", "There was no file associated with the request. "
                                                   "The file should contain the raw accelerometer data.")


# Function to verify if a file has a txt extension.
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def json_error(error, detail):
    return jsonify({
        "error": {
            "message": error,
            "detail": detail
        }
    })
