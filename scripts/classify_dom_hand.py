from scripts.analysis import get_train_test_data, plot_confusion, get_best_classifier
from utils.db_utils import get_database
from random import shuffle

RIGHT_TARGET = 20
LEFT_TARGET = 10

activity = "Writing"
participant = 13
trial = 3

filename = "{}_user_{}_trial_{}.txt".format(activity, participant, trial)

database_conn = get_database()
cursor = database_conn.cursor()

cursor.execute("""
                SELECT "meanXYZ", "stdXYZ", dom_hand
                FROM public."Featureset_1" feature, public."Participant" ptct, public."Trial" trial
                WHERE trial.participant_id = ptct.id
                AND trial.id = feature.trial_id;
                """, (filename, participant))

# Create a matrix of feature data.
features = [[attrs[0][0], attrs[0][1], attrs[0][2], attrs[1][0], attrs[1][1], attrs[1][2], attrs[2]]
            for attrs in cursor.fetchall()]

cursor.close()
database_conn.close()

# Shuffle the features to distribute them more randomly between users and trials.
shuffle(features)

# Create training data for classifying a user's dominant hand.
x_train, x_test, y_train, y_test = get_train_test_data(features, range(0, 6), range(6, 7))

for index, hand in enumerate(y_train):
    if hand[0] == 'r':
        y_train[index] = RIGHT_TARGET
    else:
        y_train[index] = LEFT_TARGET

for index, hand in enumerate(y_test):
    if hand[0] == 'r':
        y_test[index] = RIGHT_TARGET
    else:
        y_test[index] = LEFT_TARGET

# Get the best classifier for these features.
classifier, accuracy = get_best_classifier(x_train, x_test, y_train, y_test)

# Print result.
print("Best classifier is: {}, with accuracy {}".format(classifier.__class__.__name__, accuracy))

# Plot the confusion matrix of the best performing.
plot_confusion(classifier, ["Left", "Right"], x_test, y_test, title="Confusion Matrix for Dominant Hand")
