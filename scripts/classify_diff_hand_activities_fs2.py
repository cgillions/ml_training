from scripts.analysis import plot_confusion, get_best_classifier, get_train_test_data
from utils.db_utils import get_database, name_id_map
from random import shuffle
import numpy as np
import pickle


# Define the activities to classify.
activities = ["Walking", "Jogging", "Cycling", "Writing", "Typing", "Sitting",
              "Standing", "On Phone (sit)", "On Phone (stand)"]
activity_ids = [name_id_map[activity] for activity in activities]

database_conn = get_database()
cursor = database_conn.cursor()

# Select features where the participant's watch hand is different to their dominant hand.
# Change <> to = for creating the model for the opposite.
cursor.execute("""
                SELECT "meanXYZ", "stdXYZ", "mfccX", "mfccY", "mfccZ", activity_id
                FROM public."Featureset_2" fs2, public."Target" target, public."Participant" ptct, public."Trial" trial
                WHERE ptct.dom_hand = ptct.watch_hand
                AND trial.participant_id = ptct.id
                AND trial.id = fs2.trial_id
                AND trial.id = target.trial_id
                AND target.activity_id IN %s;
                """, (tuple(activity_ids),))

# Create a matrix of feature data.
features = [[
             # Mean
             attrs[0][0], attrs[0][1], attrs[0][2],
             # Deviation
             attrs[1][0], attrs[1][1], attrs[1][2],
             # MFCC X
             attrs[2][0][0], attrs[2][0][1], attrs[2][0][2], attrs[2][0][3], attrs[2][0][4],attrs[2][0][5], attrs[2][0][6],
             attrs[2][0][7], attrs[2][0][8], attrs[2][0][9], attrs[2][0][10], attrs[2][0][11], attrs[2][0][12],
             # MFCC Y[0]
             attrs[3][0][0], attrs[3][0][1], attrs[3][0][2], attrs[3][0][3], attrs[3][0][4], attrs[3][0][5], attrs[3][0][6],
             attrs[3][0][7], attrs[3][0][8], attrs[3][0][9], attrs[3][0][10], attrs[3][0][11], attrs[3][0][12],
             # MFCC Z[0]
             attrs[4][0][0], attrs[4][0][1], attrs[4][0][2], attrs[4][0][3], attrs[4][0][4], attrs[4][0][5], attrs[4][0][6],
             attrs[4][0][7], attrs[4][0][8], attrs[4][0][9], attrs[4][0][10], attrs[4][0][11], attrs[4][0][12],
             # Target
             attrs[5]]
            for attrs in cursor.fetchall()]

# Shuffle the features to distribute them more randomly between users and trials.
shuffle(features)

# Create training data for classifying a user's dominant hand.
x_train, x_test, y_train, y_test = get_train_test_data(features, range(0, 45), 45)

# Attempt to load the classifier from the database.
cursor.execute("""
                SELECT data
                FROM public."Model"
                WHERE name = %s;
                """, ("same_hand_activity_set_1_fs2",))

model = None  # cursor.fetchone()
if model is None:
    # Get the best classifier for these features.
    classifier, accuracy = get_best_classifier(x_train, x_test, y_train, y_test)

    # Print result.
    print("Best classifier is: {}, with accuracy {}".format(classifier.__class__.__name__, accuracy))

    # Plot the confusion matrix of the best performing.
    cnf_matrix = plot_confusion(classifier, activities, x_test, y_test,
                                title="Confusion Matrix for Dominant Hand")

    # Calculate the accuracies for each activity.
    accuracies = dict()
    for index, activity in enumerate(activities):
        accuracies[activity] = (cnf_matrix[index][index] / sum(cnf_matrix[index]) * 100)

    # Encode the model's meta-data.
    cnf_encoded = pickle.dumps(cnf_matrix)
    classifier_encoded = pickle.dumps(classifier)
    accuracies_encoded = pickle.dumps(accuracies)

    cursor.execute("""
                    INSERT INTO
                    public."Model" (data, name, target_accuracies, confusion_matrix)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET data = %s,
                    target_accuracies = %s,
                    confusion_matrix = %s;
                    """, (classifier_encoded, "same_hand_activity_set_1_fs2",
                          accuracies_encoded,
                          cnf_encoded,
                          classifier_encoded,
                          accuracies_encoded,
                          cnf_encoded))
    database_conn.commit()

else:
    # Use the existing classifier.
    data = model[0]
    classifier = pickle.loads(data)

    # Classify the features.
    results = classifier.predict(x_train)

    # Compare results to the actual target.
    accuracy = np.mean(results == y_train) * 100

    print("Accuracy of {} is {}.".format(classifier.__class__.__name__, accuracy))

cursor.close()
database_conn.close()
