from model.target import Target
from model.activity import name_id_map
from utils.db_utils import get_database, json_error


class Trial(object):

    id = None
    user_id = None
    filename = None
    data = None

    def __init__(self, idx, user_id, filename, data):
        self.id = idx
        self.user_id = user_id
        self.filename = filename
        self.data = data

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "data": self.data
        }

    @staticmethod
    def get():
        trials = []
        database_conn = get_database()
        cursor = database_conn.cursor()
        cursor.execute("SELECT (id, user_id, filename, data) FROM public.\"Trial\";")

        for trial in cursor:
            trials.append(Trial(trial[0], trial[1], trial[2], trial[3]).serialize())

        cursor.close()
        database_conn.close()
        return trials

    @staticmethod
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

        # Loop through the response (1 id).
        for idx in cursor.fetchall():
            idx = idx[0]
            # Get the targets for the activity.
            targets = Target.get_targets(activity_name)

            # Make an entry for each target.
            for target in targets:
                cursor.execute("INSERT INTO public.\"Target\" (trial_id, activity_id) VALUES (%s, %s);",
                               (idx, target))

        # Close the connections.
        cursor.close()
        database_conn.close()

        return "Trial added for user: {}, activity: {}.".format(user_id, activity_name)

    # Function to verify if a file has a txt extension.
    @staticmethod
    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() == "txt"
