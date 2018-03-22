from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC, SVC

from sklearn.model_selection import train_test_split

from utils.db_utils import get_database
from api.model.activity import name_id_map

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import numpy as np
import itertools
from random import shuffle


def get_features(cursor, activities):
    cursor.execute("""
                    SELECT "meanXYZ", "stdXYZ", activity_id
                    FROM public."Featureset_1" fs1, public."Target" target, public."Trial" trial
                    WHERE fs1.trial_id = target.trial_id
                    AND target.trial_id = trial.id
                    AND activity_id IN %s
                    AND trial.participant_id != 0;
                    """, (tuple(activities),))

    # Create a matrix of feature data.
    features = [[attrs[0][0], attrs[0][1], attrs[0][2], attrs[1][0], attrs[1][1], attrs[1][2], attrs[2]]
                for attrs in cursor.fetchall()]
    return features


def get_classifiers():
    return [
        QuadraticDiscriminantAnalysis(),
        DecisionTreeClassifier(),
        RandomForestClassifier(),
        KNeighborsClassifier(),
        MLPClassifier(hidden_layer_sizes=(150, 350, 100)),
        GaussianNB(),
        LinearSVC(),
        SVC(),
    ]


def get_train_test_data(features):
    # Split the data into features & targets.
    x = [feature[0:6] for feature in features]
    y = [feature[6] for feature in features]

    # Split the features into training and testing.
    return train_test_split(x, y, test_size=0.2)


def get_trained_classifiers(x_train, x_test, y_train, y_test):
    # Get the classifiers.
    classifiers = get_classifiers()

    # Train them on the training data.
    for classifier in classifiers:
        classifier.fit(x_train, y_train)

    # Measure their accuracies using the testing data.
    accuracies = []
    for classifier in classifiers:

        # Predict results.
        results = classifier.predict(x_test)

        # Compare results to the actual target.
        accuracy = np.mean(results == y_test) * 100

        # Store the result.
        print("{}\n{}\n".format(classifier.__class__.__name__, accuracy))
        accuracies.append(accuracy)

    # Return the classifier with the best accuracy.
    return classifiers


def get_best_classifier(x_train, x_test, y_train, y_test):
    classifiers = get_trained_classifiers(x_train, x_test, y_train, y_test)
    accuracies = []

    for classifier in classifiers:

        # Predict results.
        results = classifier.predict(x_test)

        # Compare results to the actual target.
        accuracy = np.mean(results == y_test) * 100

        # Store the result.
        accuracies.append(accuracy)

    return classifiers[accuracies.index(max(accuracies))], max(accuracies)


def plot_confusion(classifier, class_names, x_test, y_test):
    print("Plotting confusion matrix for {}".format(classifier.__class__.__name__))

    # Calculate probabilities.
    results = classifier.predict(X=x_test)

    # Create the confusion matrix.
    cnf_matrix = confusion_matrix(y_test, results)
    np.set_printoptions(precision=4)

    plt.figure()
    plt.imshow(cnf_matrix, cmap=plt.cm.Blues)
    plt.title("Confusion Matrix for {}".format(classifier.__class__.__name__))
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)

    fmt = 'd'
    thresh = cnf_matrix.max() / 2.
    for i, j in itertools.product(range(cnf_matrix.shape[0]), range(cnf_matrix.shape[1])):
        plt.text(j, i, format(cnf_matrix[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cnf_matrix[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()


def script():
    # Get a list of activity ids to use as targets.
    # activities = ["Walking", "Jogging", "Cycling", "Idle"]
    # activities = ["Walking", "Jogging", "Cycling", "Writing", "Typing", "Idle"]
    activities = ["Walking", "Jogging", "Cycling", "Writing", "Typing", "Sitting",
                  "Standing", "On Phone (sit)", "On Phone (stand)"]

    activity_ids = [name_id_map[activity] for activity in activities]

    # Get a connection to the database.
    database_conn = get_database()
    cursor = database_conn.cursor()

    # Get the features relating to these activities.
    features = get_features(cursor, activity_ids)

    # Close the database connections.
    cursor.close()
    database_conn.close()

    # Ensure there are the same number of features for each class.
    class_counts = []
    for activity_id in activity_ids:
        class_count = sum([1 for row in features if row[6] == activity_id])
        class_counts.append([activity_id, class_count])

    min_count = min([class_count[1] for class_count in class_counts])

    for activity_id, class_count in class_counts:
        if class_count > min_count:
            rows = [row for row in features if row[6] == activity_id]

            for row in rows[:-min_count]:
                features.remove(row)

    # Shuffle the features to distribute them more randomly between training and testing.
    shuffle(features)

    # Split the features into training and testing.
    x_train, x_test, y_train, y_test = get_train_test_data(features)

    # Get the best classifier for these features.
    classifier, accuracy = get_best_classifier(x_train, x_test, y_train, y_test)

    # Print result.
    print("Best classifier is: {}, with accuracy {}".format(classifier.__class__.__name__, accuracy))

    # Plot the confusion matrix of the best performing.
    plot_confusion(classifier, activities, x_test, y_test)


# Run the analysis script.
script()
