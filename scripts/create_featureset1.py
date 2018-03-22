from utils.db_utils import get_database
from utils.classification_utils import BIN_SIZE, MIN_SAMPLE_FREQUENCY
import numpy as np


# Calculate how many samples are needed for a feature.
MIN_SAMPLES = (BIN_SIZE / 1000) * MIN_SAMPLE_FREQUENCY

# Get a connection to the database.
database_conn = get_database()
cursor = database_conn.cursor()

# Query for the trial data.
cursor.execute("""
                SELECT id, data
                FROM public."Trial";
                """)

# Iterate through trials.
for trial_id, trial_data in cursor.fetchall():

    # Decode the trial data.
    trial_data = bytearray(trial_data).decode("utf-8")

    # Work out how many data samples are in the trial.
    line_count = trial_data.count("\n")

    # Check there are enough samples to extract a feature.
    if line_count < MIN_SAMPLES:
        print("Not enough data to extract a feature! Trial: {}".format(trial_id))
        continue

    # Create a matrix to hold the trial data.
    trial_matrix = np.ndarray((line_count, 4))

    # Read the data into the matrix.
    index = 0                       # The last line of some trials contains a trialing char or byte.
    for line in [line for line in trial_data.split("\n") if line != "" and line != b'']:
        try:
            trial_matrix[index] = line.split(",")
            index += 1
        except:
            print("Error with line {}".format(line))

    # Divide the trial data into smaller samples of the activity.
    # Keep track of how much data has been assigned.
    data_covered = 0
    end_time = int(trial_matrix[0][0])

    # Loop until all activity data is grouped by time period.
    while data_covered < line_count:
        start_time = end_time
        end_time = start_time + BIN_SIZE

        # Work out the number of data points in the time period.
        data_count = len([data for (_, data) in enumerate(trial_matrix, data_covered)
                         if data[0] < end_time])

        # Add data from the time period interval to the sample.
        section_matrix = [data for _, data in enumerate(trial_matrix, data_covered) if data[0] < end_time]
        data_covered += len(section_matrix)

        # Compute the mean of the sample.
        means = np.mean(section_matrix, axis=0)

        # Compute the standard deviation of the sample.
        stds = np.std(section_matrix, axis=0)

        # Store the feature in the database.
        cursor.execute("""
                        INSERT INTO
                        public."Featureset_1"
                        ("meanXYZ", "stdXYZ", trial_id)
                        VALUES (%s, %s, %s);
                        """, (means[1:4].tolist(), stds[1:4].tolist(), trial_id))
        print("Made a feature for trial {}".format(trial_id))

# Commit all the features.
database_conn.commit()

# Close the connection.
cursor.close()
database_conn.close()
