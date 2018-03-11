from utils.db_utils import get_database, json_error, get_attributes
from model.target import Target
from model.trial import Trial
from flask import request, jsonify


def trial_endpoint():
    if request.method == "POST":
        return post(request.form["user_id"], request.files["file"], request.form["activity_name"])

    else:
        return jsonify({"trials": get()})


def get():
    trials = []
    database_conn = get_database()
    cursor = database_conn.cursor()
    cursor.execute("SELECT (id, user_id, filename, data) FROM public.\"Trial\";")

    for trial in cursor:
        attrs = get_attributes(trial[0])
        trials.append(Trial(attrs[0], attrs[1], attrs[2], attrs[3]).serialize())

    cursor.close()
    database_conn.close()
    return trials


def post(user_id, data_file, activity_name):
    # Validate the input.
    if user_id is None:
        return json_error("user_id is required.", "We need a user ID to link the trial to.")

    if activity_name is None:
        return json_error("activity_name is required.", "We need to know the activity so that we can train the AI.")

    if data_file is None:
        return json_error("file is required.", "There was no file associated with the request."
                                               "The file should contain the raw accelerometer data.")

    # Convert trial file to bytes.
    ba = bytearray(data_file.read())

    # Store the data in the database.
    database_conn = get_database()
    cursor = database_conn.cursor()
    cursor.execute("INSERT INTO public.\"Trial\" (user_id, filename, data) VALUES (%s, %s, %s) RETURNING id;",
                   (user_id, data_file.filename, ba))

    # Commit the transaction.
    database_conn.commit()

    # Get the ID of the new trial.
    idx = cursor.fetchone()[0]

    # Get the targets for the activity.
    targets = Target.get_targets(activity_name)

    # Make an entry for each target.
    for target in targets:
        cursor.execute("INSERT INTO public.\"Target\" (trial_id, activity_id) VALUES (%s, %s);",
                       (idx, target))

    # Close the connections.
    database_conn.commit()
    cursor.close()
    database_conn.close()

    return "Trial added for user: {}, activity: {}.".format(user_id, activity_name)


# Function to verify if a file has a txt extension.
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "txt"
