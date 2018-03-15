import controller.Featureset1Controller as Featureset1Controller
import controller.ActivityController as ActivityController
import controller.TrialController as TrialController
import controller.UserController as UserController
from flask import Flask, request

from controller import ParticipantController
from model.user import User
from utils.response_utils import error

app = Flask(__name__)

app.config["ADMIN_SECRET"] = "5dyvo1z6y34so4ogkgksw88ookoows00cgoc488kcs8wk4c40s"


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


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
