from api.controller import ClassificationController, Featureset1Controller, ParticipantController, \
                           ActivityController, TrialController, UserController, ModelController

from utils.response_utils import error
from api.model.user import User
from flask import Flask, request


app = Flask(__name__)


@app.route("/classify", methods=["POST"])
def classify():
    return ClassificationController.classify(request.form.get("acceleration"), request.form.get("model_name"))


@app.route("/activities", methods=["GET"])
def activities():
    return ActivityController.get()


@app.route("/trials", methods=["GET", "POST"])
def trials():
    # This requires a valid user.
    result = UserController.login(
                    request.headers.get("auth_token"),
                    request.headers.get("Authorization"))

    # If not a user, return the error.
    if not isinstance(result, User):
        return result

    # Handle the trial response.
    if request.method == "POST":
        if result.role != "admin":
            return error("Permission denied", "You must have administrator rights to upload trials.")
        else:
            return TrialController.post(
                    request.form.get("participant_id"),
                    request.files.get("file"),
                    request.form.get("activity_name"),
                    request.form.get("trial_num"))
    else:
        return TrialController.get(result)


@app.route("/featureset1", methods=["GET", "POST"])
def featureset():
    # This requires a valid user.
    result = UserController.login(
        request.headers.get("auth_token"),
        request.headers.get("Authorization"))

    # If not a user, return the error.
    if not isinstance(result, User):
        return result

    if request.method == "POST":
        if result.role != "admin":
            return error("Permission denied", "You must have administrator rights to upload features.")
        else:
            return Featureset1Controller.post(request.form.get("trial_id"), request.files.get("file"))
    else:
        return Featureset1Controller.get(result)


@app.route("/register", methods=["POST"])
def register():
    return UserController.register()


@app.route("/participants", methods=["GET", "POST"])
def participants():
    # This requires a valid user.
    result = UserController.login(
        request.headers.get("auth_token"),
        request.headers.get("Authorization"))

    # If not a user, return the error.
    if not isinstance(result, User):
        return result

    # If the user isn't an admin, return the error.
    if result.role != "admin":
        return error("Permission denied", "You must have administrator rights to upload features.")

    if request.method == "POST":
        return ParticipantController.post(
                    request.form.get("id"),
                    request.form.get("dom_hand"),
                    request.form.get("watch_hand"),
                    request.form.get("gender"))
    else:
        return ParticipantController.get(request.args.get("id"))


@app.route("/models", methods=["GET"])
def models():
    return ModelController.get()


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
