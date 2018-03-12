import controller.Featureset1Controller as Featureset1Controller
import controller.ActivityController as ActivityController
import controller.TrialController as TrialController
import controller.UserController as UserController
from flask import Flask, request
from model.user import User


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
                    request.headers.get("username"),
                    request.headers.get("password"))

    # If not a user, return the error.
    if not isinstance(result, User):
        return result

    # Handle the trial response.
    if request.method == "POST":
        return TrialController.post(
                    request.form.get("participant_id"),
                    request.files.get("file"),
                    request.form.get("activity_name"))
    else:
        return TrialController.get()


@app.route("/featureset1", methods=["GET", "POST"])
def featureset():
    if request.method == "POST":
        return Featureset1Controller.post(request.files.get("file"))
    else:
        return Featureset1Controller.get()


@app.route("/register", methods=["POST"])
def register_user():
    return UserController.register()


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
