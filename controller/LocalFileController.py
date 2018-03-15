import requests
import os


# Function to upload local trial files to the database.
def upload_local_trials():

    # Define the API endpoint.
    dst_url = "https://ml-training.herokuapp.com/trials"

    # Define the trial file source.
    source_dir = "C:/Users/Charlie/Documents/uni/final-project/Classification API/"\
                 "classification/classification/data/source/activities"

    # List the user directories.
    for user_dir in os.listdir(source_dir):

        # List the activity directories.
        for activity_dir in os.listdir("{}/{}".format(source_dir, user_dir)):

            # Iterate through the trial files.
            for trial_file in os.listdir("{}/{}/{}".format(source_dir, user_dir, activity_dir)):

                # Get info about the trial.
                activity, participant_id, trial_num = get_trial_info(trial_file)

                # Create the request headers.
                headers = {"Authorization": "Basic Y2dpbGxpb25zOmh1bmt5ZG9yeQ=="}

                # Create the request body.
                body = {"participant_id": participant_id, "activity_name": activity, "trial_num": trial_num}

                # Create the multipart form.
                trial = open("{}/{}/{}/{}".format(source_dir, user_dir, activity_dir, trial_file), "rb")
                files = {"file": (os.path.basename(trial_file), trial)}

                # Send the request.
                r = requests.post(dst_url, headers=headers, data=body, files=files)

                # Close the file.
                trial.close()

                # Check the status.
                if r.status_code != requests.codes.ok:
                    r.raise_for_status()


def get_trial_info(trial_filename):
    attrs = trial_filename.split(".")[0].split("_")

    activity = attrs[0]
    participant = attrs[2]
    trial_num = attrs[4]

    return activity, participant, trial_num


upload_local_trials()
