from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC, SVC

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from random import shuffle
import numpy as np
import itertools

from utils.db_utils import get_database, name_id_map


def get_features(cursor, activities):
    cursor.execute("""
                    SELECT "meanXYZ", "stdXYZ", activity_id
                    FROM public."Featureset_1" fs1, public."Target" target, public."Trial" trial
                    WHERE fs1.trial_id = target.trial_id
                    AND target.trial_id = trial.id
                    AND activity_id IN %s;
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


def get_train_test_data(features, feature_range, target_index):
    # Split the data into features & targets.
    x = [[feature[index] for index in feature_range] for feature in features]
    y = [feature[target_index] for feature in features]

    # Split the features into training and testing.
    return train_test_split(x, y, test_size=0.2)


def get_accuracy(classifier, x, target):
    # Predict results.
    results = classifier.predict(x)

    # Compare results to the actual target.
    accuracy = np.mean(results == target) * 100

    # Return the result.
    return accuracy


def get_trained_classifiers(x_train, y_train):
    # Get the classifiers.
    classifiers = get_classifiers()

    # Train them on the training data.
    for classifier in classifiers:
        classifier.fit(x_train, y_train)

    # Return the classifier with the best accuracy.
    return classifiers


def get_best_classifier(x_train, x_test, y_train, y_test):
    # Train the classifiers.
    classifiers = get_trained_classifiers(x_train,  y_train)

    # Measure their accuracies using the testing data.
    accuracies = [get_accuracy(classifier, x_test, y_test) for classifier in classifiers]

    # Return the best performing one.
    return classifiers[accuracies.index(max(accuracies))], max(accuracies)


def plot_confusion(classifier, class_names, x_test, y_test, cnf_matrix=None, title=None):
    plt.figure()

    if cnf_matrix is None:
        print("Plotting confusion matrix for {}".format(classifier.__class__.__name__))

        # Calculate probabilities.
        results = classifier.predict(X=x_test)

        # Create the confusion matrix.
        cnf_matrix = confusion_matrix(y_test, results)

        # Set the title.
        if title is None:
            plt.title("Confusion Matrix for {}".format(classifier.__class__.__name__))
        else:
            plt.title(title)
    else:
        if title is None:
            plt.title("Summed Confusion Matrix")
        else:
            plt.title(title)

    np.set_printoptions(precision=4)
    plt.imshow(cnf_matrix, cmap=plt.cm.Blues)
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

    return cnf_matrix


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

    # Shuffle the features to distribute them more randomly between users and trials.
    shuffle(features)

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

    # Split the features into training and testing.
    x_train, x_test, y_train, y_test = get_train_test_data(features, range(0, 6), 6)

    # Plot confusion matrices.
    conf_matrix = None
    for classifier in get_trained_classifiers(x_train, y_train):
        cnf = plot_confusion(classifier, activities, x_test, y_test)
        if conf_matrix is None:
            conf_matrix = cnf
        else:
            conf_matrix += cnf

    # Plot the total conf matrix.
    plot_confusion(None, activities, x_test, y_test, conf_matrix)

    # Get the best classifier for these features.
    classifier, accuracy = get_best_classifier(x_train, x_test, y_train, y_test)

    # Print result.
    print("Best classifier is: {}, with accuracy {}".format(classifier.__class__.__name__, accuracy))

    # Plot the confusion matrix of the best performing.
    plot_confusion(classifier, activities, x_test, y_test)


# Run the analysis script.
if __name__ == "__main__":
    script()
