import os
import shutil
from flask import Flask, request, jsonify, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = "data/trials"
ALLOWED_EXTENSIONS = {"txt"}


@app.route("/trials/add", methods=["GET", "POST"])
def add_trial():
    if request.method == "POST":
        # Validate the POST form parameters.
        if "user_id" not in request.form:
            return json_error("user_id is required.", "We need a user ID to link the trial to.")

        if "activity_name" not in request.form:
            return json_error("activity_name is required.", "We need to know the activity so that we can train the AI.")

        if "file" not in request.files:
            return json_error("file is required.", "There was no file associated with the request. "
                                                   "The file should contain the raw accelerometer data.")

        # Get the file from the request.
        file = request.files["file"]

        # Check it's extension.
        if not allowed_file(file.filename):
            return json_error("File must have a .txt extension.", "The trial file must be a plain text file.")

        # Create a name for the file.
        filepath = os.path.join(UPLOAD_FOLDER, "U{}_{}.txt".
                                format(request.form["user_id"], request.form["activity_name"]))

        # Ensure the parent directory is created.
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Save the file.
        with open(filepath, "wb") as new_file:
            shutil.copyfileobj(file, new_file)

        return "POST success!"

    if request.method == "GET":
        return "GET success!"


@app.route("/trials/get", methods=["GET"])
def get_trials():
    if os.path.exists(UPLOAD_FOLDER):
        trials = os.listdir(UPLOAD_FOLDER)
    else:
        trials = []
    return trials



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


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
