from credentials import ADMIN_AUTH_HEADER
from utils.db_utils import get_database
import requests
import os


# Function to get metadata from a trial file.
# File name format: "ActivityName_user_n_trial_n.txt"
def get_trial_info(trial_filename):
    attrs = trial_filename.split(".")[0].split("_")

    activity = attrs[0]
    participant = attrs[2]
    trial_num = attrs[4]

    return activity, participant, trial_num


#
# Upload local trial files to the API. The API will validate and store data in the database.
#

# Define the API endpoint.
dst_url = "https://ml-training.herokuapp.com/trials"

# Define the trial file source.
source_dir = "C:/Users/Charlie/Documents/uni/final-project/Activities"

# Open a connection to the database (so we can check if trials already exist).
database_conn = get_database()
cursor = database_conn.cursor()

# List the user directories.
for user_dir in os.listdir(source_dir):

    # List the activity directories.
    for activity_dir in os.listdir("{}/{}".format(source_dir, user_dir)):

        # Iterate through the trial files.
        for trial_file in os.listdir("{}/{}/{}".format(source_dir, user_dir, activity_dir)):

            print(trial_file)

            # Get info about the trial.
            activity, participant_id, trial_num = get_trial_info(trial_file)

            # Check if this trial is already in the database.
            cursor.execute("""
                            SELECT COUNT(*)
                            FROM public."Trial"
                            WHERE filename=%s;
                            """, (trial_file,))

            count = cursor.fetchone()[0]
            if count != 0:
                print(trial_file + " already exists.")
                continue

            # Create the request body.
            body = {"participant_id": participant_id, "activity_name": activity, "trial_num": trial_num}

            # Create the multipart form.
            trial = open("{}/{}/{}/{}".format(source_dir, user_dir, activity_dir, trial_file), "rb")
            files = {"file": (trial_file, trial)}

            # Send the request.
            r = requests.post(dst_url, headers=ADMIN_AUTH_HEADER, data=body, files=files)

            # Close the file.
            trial.close()

            # Check the status.
            if r.status_code != requests.codes.ok:
                r.raise_for_status()

            print("Uploaded.\n")

# Close the database connection.
cursor.close()
database_conn.close()
