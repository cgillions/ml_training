from controller.ActivityController import activity_endpoint
from controller.TrialController import trial_endpoint
from controller.Featureset1Controller import featureset1_endpoint
from flask import Flask

app = Flask(__name__)


@app.route("/activities", methods=["GET"])
def activities():
    return activity_endpoint()


@app.route("/trials", methods=["GET", "POST"])
def trials():
    return trial_endpoint()


@app.route("/featureset1", methods=["GET", "POST"])
def featureset():
    return featureset1_endpoint()


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
