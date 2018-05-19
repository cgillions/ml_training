from scripts.analysis import get_train_test_data, plot_confusion, get_best_classifier, get_trained_classifiers, \
    get_accuracy
from utils.db_utils import get_database
from random import shuffle
import numpy as np
import pickle


# Define the model name.
model_name = "fs1_diff_hands"
description = "Classifies whether the watch is on the user's dominant hand."

database_conn = get_database()
cursor = database_conn.cursor()

# Get the participant's information alongside the features.
cursor.execute("""
                SELECT "meanXYZ", "stdXYZ", dom_hand, watch_hand
                FROM public."Featureset_1" feature, public."Participant" ptct, public."Trial" trial
                WHERE trial.participant_id = ptct.id
                AND trial.id = feature.trial_id;
                """)

# Create a matrix of feature data.
features = [[attrs[0][0], attrs[0][1], attrs[0][2], attrs[1][0], attrs[1][1], attrs[1][2], attrs[2] == attrs[3]]
            for attrs in cursor.fetchall()]

# Shuffle the features to distribute them more randomly between users and trials.
shuffle(features)

# Create training data for classifying a user's dominant hand.
x_train, x_test, y_train, y_test = get_train_test_data(features, range(0, 6), 6)

# # Update the target to a numerical value.
# for index, hand in enumerate(y_train):
#     if hand[0] == 'r':
#         y_train[index] = RIGHT_TARGET
#     else:
#         y_train[index] = LEFT_TARGET
#
# for index, hand in enumerate(y_test):
#     if hand[0] == 'r':
#         y_test[index] = RIGHT_TARGET
#     else:
#         y_test[index] = LEFT_TARGET
#
# We're saved doing this manipulation of data through the boolean comparator in the list comprehension above.

# Attempt to load the classifier from the database.
cursor.execute("""
                SELECT data
                FROM public."Model"
                WHERE name = %s;
                """, (model_name,))

model = None # cursor.fetchone()
if model is None:
    # Train the classifiers.
    trained_classifiers = get_trained_classifiers(x_train, y_train)

    # Measure their accuracies using the testing data.
    accuracies = [get_accuracy(classifier, x_test, y_test) for classifier in trained_classifiers]

    # Print the accuracies of each algorithm.
    for classifier, accuracy in zip(trained_classifiers, accuracies):
        print("{} is {}% accurate".format(classifier.__class__.__name__, accuracy))

    # Get the best classifier for these features.
    classifier, accuracy = trained_classifiers[accuracies.index(max(accuracies))], max(accuracies)

    # Plot the confusion matrix of the best performing.
    cnf_matrix = plot_confusion(classifier, ["Diff", "Same"], x_test, y_test,
                                title="Confusion Matrix for dominant = watch hand")

    # Calculate the accuracies for left and right handed users.
    diff_accuracy = cnf_matrix[0][0] / sum(cnf_matrix[0]) * 100
    same_accuracy = cnf_matrix[1][1] / sum(cnf_matrix[1]) * 100

    # Print result.
    print("Best classifier is: {}, with {}% total accuracy.\nSame hands: {}%\nDiff hands: {}%"
          .format(classifier.__class__.__name__, accuracy, same_accuracy, diff_accuracy))

    cnf_encoded = pickle.dumps(cnf_matrix)
    classifier_encoded = pickle.dumps(classifier)
    accuracies_encoded = pickle.dumps({"same": same_accuracy, "diff": diff_accuracy})

    cursor.execute("""
                    INSERT INTO
                    public."Model" (data, name, description, target_accuracies, confusion_matrix)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET data = %s,
                    target_accuracies = %s,
                    confusion_matrix = %s;
                    """, (classifier_encoded, model_name, description,
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
