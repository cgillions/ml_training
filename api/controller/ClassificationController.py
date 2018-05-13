from api.model.activity import Activity
from utils.classification_utils import BIN_SIZE
from utils.response_utils import error
from utils.db_utils import get_database, name_id_map
from python_speech_features import mfcc
from flask import jsonify
import numpy as np
import pickle

FEATURE_SET = 1


def classify(acceleration_data, diff_hands):
    if acceleration_data is None:
        return error("Acceleration data not provided.", "Post accelerometer data in the request.")

    # Get the features from the data.
    features, time_intervals = get_features(acceleration_data, FEATURE_SET)

    # Connect to the database.
    database_conn = get_database()
    cursor = database_conn.cursor()

    response = None
    if FEATURE_SET == 1:

        # Work out the dominant / watch hand configuration.
        if diff_hands is None:
            cursor.execute("""
                            SELECT data
                            FROM public."Model"
                            WHERE name = %s;
                            """, ("fs1_diff_hands",))

            model_data = cursor.fetchone()[0]
            classifier = pickle.loads(model_data)

            # Classify whether the user's dominant hand is different to their watch hand.
            diff_hands = classifier.predict(features)

            # Use the mean predicted configuration.
            diff_hands = sum(diff_hands) > (len(diff_hands) / 2)

        # Load the suitable activity classifier.
        cursor.execute("""
                        SELECT data, target_accuracies
                        FROM public."Model"
                        WHERE name = %s;
                        """, ("as1_fs1_{}_hands".format("diff" if diff_hands == 1 else "same"),))

        response = cursor.fetchone()

    if FEATURE_SET == 2:

        # Work out the dominant / watch hand configuration.
        if diff_hands is None:
            cursor.execute("""
                            SELECT data
                            FROM public."Model"
                            WHERE name = %s;
                            """, ("fs2_diff_hands",))

            model_data = cursor.fetchone()[0]
            classifier = pickle.loads(model_data)

            # Classify whether the user's dominant hand is different to their watch hand.
            diff_hands = classifier.predict(features)

            # Use the mean predicted configuration.
            diff_hands = sum(diff_hands) > (len(diff_hands) / 2)
        # Load the suitable activity classifier.
        cursor.execute("""
                        SELECT data, target_accuracies
                        FROM public."Model"
                        WHERE name = %s;
                        """, ("{}_hand_activity_set_1_fs2".format("diff" if diff_hands == 1 else "same"),))

        response = cursor.fetchone()

    # Decode the response.
    model_data = response[0]
    accuracy_data = response[1]
    classifier = pickle.loads(model_data)
    accuracies = pickle.loads(accuracy_data)

    # Close the database connection.
    cursor.close()
    database_conn.close()

    # Predict the activities.
    activity_ids = classifier.predict(features)

    # Create wrapper objects to store attribute name meta-data.
    activities = []
    for activity_id, time_interval in zip(activity_ids, time_intervals):
        activities.append(Activity(
                            int(activity_id),
                            name_id_map[activity_id],
                            time_interval[0],
                            time_interval[1], accuracies[name_id_map[activity_id]])
                          .__dict__)

    # Return the activities in json.
    return jsonify({"activities": activities, "diff_hands": "true" if diff_hands else "false"})


def get_features(acceleration_data, featureset):
    line_count = len(acceleration_data.splitlines())

    # Create a matrix to hold the trial data.
    trial_matrix = np.ndarray((line_count, 4))

    # Read the trial data into the matrix.
    line_index = 0
    for line in acceleration_data.splitlines():
        data = np.array(line.split(","))

        # Check if we've reached the end of the file.
        if len(data) == 0 or len(data) == 1:
            break

        trial_matrix[line_index] = data
        line_index += 1

    # Check if the data just read was valid.
    if line_index == 0:
        print("Invalid file.")
        return None

    # Divide the trial data into features of the activity.
    # Keep track of how much data has been assigned.
    data_covered = 0
    end_time = int(trial_matrix[0][0])

    features = []
    time_intervals = []

    # Loop until all activity data is grouped by time period.
    while data_covered < line_count:
        start_time = end_time
        end_time = start_time + BIN_SIZE

        # Work out the number of data points in the time period.
        data_count = 0
        for data in enumerate(trial_matrix, data_covered):
            if data[1][0] < end_time:
                data_count += 1
            else:
                break

        # Create a matrix to hold the sample of data.
        section_matrix = np.ndarray((data_count, 4))
        section_start = trial_matrix[data_covered][0]
        section_index = 0

        # Add data from the time period interval to the sample.
        for data in enumerate(trial_matrix, data_covered):
            if data[1][0] < end_time:
                section_matrix[section_index] = data[1]
                section_index += 1
                data_covered += 1
            else:
                break

        # Get features for the sample.
        if featureset == 1:
            features.append(extract_featureset1(section_matrix))
        else:
            features.append(extract_featureset2(section_matrix))

        # Keep track of the start and end time for this feature.
        time_intervals.append([section_start, section_matrix[section_index - 1][0]])

    return features, time_intervals


def extract_featureset1(data_sample):
    # Compute the mean of the sample.
    means = np.mean(data_sample[:, range(1, 4)], axis=0)

    # Compute the standard deviation of the sample.
    stds = np.std(data_sample[:, range(1, 4)], axis=0)

    # Return the feature array.
    return np.append(means, stds)


def extract_featureset2(data_sample):
    # Compute the mean of the sample.
    means = np.mean(data_sample[:, range(1, 4)], axis=0)

    # Compute the standard deviation of the sample.
    stds = np.std(data_sample[:, range(1, 4)], axis=0)

    # Compute the 13 mel-frequency cepstral coefficients for the x axis.
    length = (data_sample[len(data_sample) - 1][0] - data_sample[0][0]) / 1000
    step = (data_sample[1][0] - data_sample[0][0]) / 1000
    mfccX = mfcc(
        np.asarray([row[1] for row in data_sample]),
        winlen=length,
        winstep=step,
        nfft=800000
    )
    # Compute the 13 mel-frequency cepstral coefficients for the y axis.
    mfccY = mfcc(
        np.asarray([row[2] for row in data_sample]),
        winlen=length,
        winstep=step,
        nfft=800000
    )
    # Compute the 13 mel-frequency cepstral coefficients for the z axis.
    mfccZ = mfcc(
        np.asarray([row[3] for row in data_sample]),
        winlen=length,
        winstep=step,
        nfft=800000
    )
    return np.concatenate((means, stds, mfccX[0], mfccY[0], mfccZ[0]))
