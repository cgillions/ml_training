from flask import Flask, request, jsonify
from model.activity import Activity
from model.trial import Trial

app = Flask(__name__)


@app.route("/trials", methods=["GET", "POST"])
def trials():
    if request.method == "POST":
        return Trial.post(request.form["user_id"], request.files["file"], request.form["activity_name"])

    else:  # if request.method == "GET":
        return jsonify(Trial.get())


@app.route("/activities", methods=["GET"])
def activities():
    return jsonify({"activities": Activity.get()})


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
