from utils.db_utils import get_database
from utils.response_utils import error, success
from api.model.target import Target
from api.model.trial import Trial
from flask import jsonify


def get(user):
    trials = []
    database_conn = get_database()
    cursor = database_conn.cursor()
    cursor.execute("""
                    SELECT id, participant_id, filename, data
                    FROM public."Trial";
                    """)

    for attrs in cursor:
        trials.append(Trial(attrs[0], attrs[1], attrs[2], attrs[3]).__dict__)

    cursor.close()
    database_conn.close()

    if user is None:
        return jsonify({"trials": trials})
    else:
        return jsonify({"trials": trials, "user": user.__dict__})


def post(participant_id, data_file, activity_name, trial_num):
    # Validate the input.
    if participant_id is None:
        return error("participant_id is required.", "We need a participant ID to link the trial to.")

    if activity_name is None:
        return error("activity_name is required.", "We need to know the activity so that we can train the AI.")

    if data_file is None:
        return error("file is required.", "There was no file associated with the request."
                                          "The file should contain the raw accelerometer data.")

    if trial_num is None:
        return error("trial_num is required.", "We need a trial number link the trial to.")

    # Convert trial file to bytes.
    data = data_file.read()

    # Store the data in the database.
    database_conn = get_database()
    cursor = database_conn.cursor()
    cursor.execute("""
                    INSERT INTO 
                    public."Trial" 
                    (participant_id, filename, data, trial_num) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING id;
                    """, (participant_id, data_file.filename, data, trial_num))

    # Commit the transaction.
    database_conn.commit()

    # Get the ID of the new trial.
    idx = cursor.fetchone()[0]

    # Get the targets for the activity.
    targets = Target.get_targets(activity_name)

    # Make an entry for each target.
    for target in targets:
        cursor.execute("""
                        INSERT INTO 
                        public."Target" 
                        (trial_id, activity_id) 
                        VALUES (%s, %s);
                        """, (idx, target))

    # Commit the transaction.
    database_conn.commit()

    # Close the connections.
    cursor.close()
    database_conn.close()

    return success("Trial added for participant: {}, activity: {}.".format(participant_id, activity_name))


# Function to verify if a file has a txt extension.
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "txt"
