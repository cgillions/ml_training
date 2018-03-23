import matplotlib.pyplot as plt
from utils.db_utils import get_database
import numpy as np


participant = 13
activity = "Writing"
trial = 3

filename = "{}_user_{}_trial_{}.txt".format(activity, participant, trial)

database_conn = get_database()
cursor = database_conn.cursor()

cursor.execute("""
                SELECT data
                FROM public."Trial"
                WHERE filename = %s
                AND participant_id = %s
                LIMIT 1;
                """, (filename, participant))

# Decode the trial data.
trial_data = bytearray(cursor.fetchone()[0]).decode("utf-8")

# Work out how many data samples are in the trial.
line_count = trial_data.count("\n")

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

plt.figure()
plt.title(filename)
plt.xlabel('Time (ms epoch)')
plt.ylabel('Acceleration (m/s)')
plt.plot(trial_matrix[::2, 0], trial_matrix[::2, 1])
plt.plot(trial_matrix[::2, 0], trial_matrix[::2, 2])
plt.plot(trial_matrix[::2, 0], trial_matrix[::2, 3])
plt.legend(["X", "Y", "Z"])
plt.show()
