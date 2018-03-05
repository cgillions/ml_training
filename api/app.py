import os
from flask import Flask, request, jsonify, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = "../data/trials"
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

        # Save the file.
        file.save(os.path.join(UPLOAD_FOLDER, "U{}_{}".format(request.form["user_id"], request.form["activity_name"])))

        return "POST success!"

    if request.method == "GET":
        return "GET success!"


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
