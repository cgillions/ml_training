from random import shuffle

from scripts.analysis import get_features, get_train_test_data, get_trained_classifiers, get_accuracy, plot_confusion
from utils.db_utils import get_database

energy_id_map = {
    10: "Idle",
    20: "Low",
    30: "Medium",
    40: "High",
    "Sitting": 10,
    "Standing": 10,
    "On Phone (sit)": 10,
    "On Phone (stand)": 10,
    "Writing": 20,
    "Typing": 20,
    "Walking": 30,
    "Cycling": 30,
    "Jogging": 40
}


def script():
    # Get a list of activity ids to use as targets.
    # activities = ["Walking", "Jogging", "Cycling", "Idle"]
    # activities = ["Walking", "Jogging", "Cycling", "Writing", "Typing", "Idle"]
    activities = ["Walking", "Jogging", "Cycling", "Writing", "Typing", "Sitting",
                  "Standing", "On Phone (sit)", "On Phone (stand)"]

    activity_ids = [energy_id_map[activity] for activity in activities]

    targets = ["Idle", "Low", "Medium", "High"]

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

    # Split the features into training and testing.
    x_train, x_test, y_train, y_test = get_train_test_data(features, range(0, 6), 6)

    # Train the classifiers.
    trained_classifiers = get_trained_classifiers(x_train, y_train)

    # Plot confusion matrices.
    conf_matrix = None
    for classifier in trained_classifiers:
        cnf = plot_confusion(classifier, targets, x_test, y_test)
        if conf_matrix is None:
            conf_matrix = cnf
        else:
            conf_matrix += cnf

    # Plot the total conf matrix.
    plot_confusion(None, targets, x_test, y_test, conf_matrix)

    # Measure their accuracies using the testing data.
    accuracies = [get_accuracy(classifier, x_test, y_test) for classifier in trained_classifiers]

    # Print the accuracies of each algorithm.
    for classifier, accuracy in zip(trained_classifiers, accuracies):
        print("{} is {}% accurate".format(classifier.__class__.__name__, accuracy))

    # Get the best classifier for these features.
    classifier, accuracy = trained_classifiers[accuracies.index(max(accuracies))], max(accuracies)

    # Print result.
    print("Best classifier is: {}, with accuracy {}".format(classifier.__class__.__name__, accuracy))

    # Plot the confusion matrix of the best performing.
    plot_confusion(classifier, targets, x_test, y_test)


# Run the script.
if __name__ == "__main__":
    script()
