from scripts.analysis import get_train_test_data, plot_confusion, get_best_classifier
from utils.db_utils import get_database, LEFT_TARGET, RIGHT_TARGET
from random import shuffle
import numpy as np
import pickle

database_conn = get_database()
cursor = database_conn.cursor()

cursor.execute("""
                SELECT "meanXYZ", "stdXYZ", dom_hand
                FROM public."Featureset_1" feature, public."Participant" ptct, public."Trial" trial
                WHERE trial.participant_id = ptct.id
                AND trial.id = feature.trial_id;
                """)

# Create a matrix of feature data.
features = [[attrs[0][0], attrs[0][1], attrs[0][2], attrs[1][0], attrs[1][1], attrs[1][2],
             RIGHT_TARGET if (attrs[2] == 'r') else LEFT_TARGET]
            for attrs in cursor.fetchall()]

# Shuffle the features to distribute them more randomly between users and trials.
shuffle(features)

# Create training data for classifying a user's dominant hand.
x_train, x_test, y_train, y_test = get_train_test_data(features, range(0, 6), 6)

# Attempt to load the classifier from the database.
cursor.execute("""
                SELECT data
                FROM public."Model"
                WHERE name = %s;
                """, ("dom_hand",))

model = cursor.fetchone()
if model is None:
    # Get the best classifier for these features.
    classifier, accuracy = get_best_classifier(x_train, x_test, y_train, y_test)

    # Print result.
    print("Best classifier is: {}, with accuracy {}".format(classifier.__class__.__name__, accuracy))

    # Plot the confusion matrix of the best performing.
    cnf_matrix = plot_confusion(classifier, ["Left", "Right"], x_test, y_test,
                                title="Confusion Matrix for Dominant Hand")

    # Calculate the accuracies for left and right handed users.
    left_accuracy = cnf_matrix[0][0] / sum(cnf_matrix[0]) * 100
    right_accuracy = cnf_matrix[1][1] / sum(cnf_matrix[1]) * 100

    cnf_encoded = pickle.dumps(cnf_matrix)
    classifier_encoded = pickle.dumps(classifier)
    accuracies_encoded = pickle.dumps({"left": left_accuracy, "right": right_accuracy})

    cursor.execute("""
                    INSERT INTO
                    public."Model" (data, name, target_accuracies, confusion_matrix)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET data = %s,
                    target_accuracies = %s,
                    confusion_matrix = %s;
                    """, (classifier_encoded, "dom_hand",
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
