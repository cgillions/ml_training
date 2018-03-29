from scripts.analysis import get_train_test_data, get_accuracy
from utils.db_utils import get_database, name_id_map
import unittest
import pickle


class DiffHandsTest(unittest.TestCase):

    def setUp(self):
        self.database_conn = get_database()
        self.cursor = self.database_conn.cursor()

    def tearDown(self):
        self.cursor.close()
        self.database_conn.close()

    def test_diff_hands_response(self):
        # Get the model.
        self.cursor.execute("""
                            SELECT data
                            FROM public."Model"
                            WHERE name = %s;
                            """, ("diff_hands",))
        data = self.cursor.fetchone()

        # Check for existence.
        if data is None:
            self.fail("There is no model with the name diff_hands.")

        # Decode the classifier.
        data = data[0]
        classifier = pickle.loads(data)

        # Get a feature to test.
        feature = self.get_features(limit=1)[0][:6]

        # Classify the feature.
        result = classifier.predict([feature])

        # Check it is a valid response.
        self.assertEqual(result[0] in [True, False], True, "The classifier did not provide a boolean response.")

    def test_diff_hand_activities_response(self):
        # Get the model.
        self.cursor.execute("""
                            SELECT data
                            FROM public."Model"
                            WHERE name = %s;
                            """, ("diff_hand_activity_set_1",))
        data = self.cursor.fetchone()

        # Check for existence.
        if data is None:
            self.fail("There is no model with the name diff_hand_activity_set_1.")

        # Decode the classifier.
        data = data[0]
        classifier = pickle.loads(data)

        # Get a feature to test.
        feature = self.get_features(limit=1)[0][:6]

        # Classify the feature.
        result = classifier.predict([feature])

        # Check it is a valid response.
        self.assertEqual(result[0] in name_id_map.keys(), True, "The classifier did not provide a known response.")

    def test_same_hand_activities_response(self):
        # Get the model.
        self.cursor.execute("""
                            SELECT data
                            FROM public."Model"
                            WHERE name = %s;
                            """, ("same_hand_activity_set_1",))
        data = self.cursor.fetchone()

        # Check for existence.
        if data is None:
            self.fail("There is no model with the name same_hand_activity_set_1.")

        # Decode the classifier.
        data = data[0]
        classifier = pickle.loads(data)

        # Get a feature to test.
        feature = self.get_features(limit=1)[0][:6]

        # Classify the feature.
        result = classifier.predict([feature])

        # Check it is a valid response.
        self.assertEqual(result[0] in name_id_map.keys(), True, "The classifier did not provide a known response.")

    def test_improved_accuracy(self):
        # Get the "same hand" activity classifying model.
        self.cursor.execute("""
                            SELECT data
                            FROM public."Model"
                            WHERE name = %s;
                            """, ("same_hand_activity_set_1",))
        data = self.cursor.fetchone()

        # Check for existence.
        if data is None:
            self.fail("There is no model with the name same_hand_activity_set_1.")

        # Decode the classifier.
        data = data[0]
        same_hand_classifier = pickle.loads(data)

        # Get the "diff hand" activity classifying model.
        self.cursor.execute("""
                            SELECT data
                            FROM public."Model"
                            WHERE name = %s;
                            """, ("diff_hand_activity_set_1",))
        data = self.cursor.fetchone()

        # Check for existence.
        if data is None:
            self.fail("There is no model with the name diff_hand_activity_set_1.")

        # Decode the classifier.
        data = data[0]
        diff_hand_classifier = pickle.loads(data)

        # Get the general activity classifying model for comparison.
        self.cursor.execute("""
                            SELECT data
                            FROM public."Model"
                            WHERE name = %s;
                            """, ("activity_set_1",))
        data = self.cursor.fetchone()

        # Check for existence.
        if data is None:
            self.fail("There is no model with the name activity_set_1.")

        # Decode the classifier.
        data = data[0]
        general_classifier = pickle.loads(data)

        # Get features for users that wear their watch on their dominant hand.
        same_features = self.get_features(dom_hand_is_watch_hand=True)

        # Get features for users that don't wear their watch on their dominant hand.
        diff_features = self.get_features(dom_hand_is_watch_hand=False)

        # Get the activity classification accuracy when the user wears the watch on their dominant hand.
        _, x_test, _, y_test = get_train_test_data(same_features, range(0, 6), 6)
        same_accuracy = get_accuracy(same_hand_classifier, x_test, y_test)

        # Get the activity classification accuracy when the user wears the watch on their non-dominant hand.
        _, x_test, _, y_test = get_train_test_data(diff_features, range(0, 6), 6)
        diff_accuracy = get_accuracy(diff_hand_classifier, x_test, y_test)

        # Get the accuracy for all watch / arm configurations.
        same_features.append(diff_features)
        _, x_test, _, y_test = get_train_test_data(same_features, range(0, 6), 6)
        general_accuracy = get_accuracy(general_classifier, x_test, y_test)

        self.assertTrue(general_accuracy < same_accuracy, "The targeted classifier did not improve accuracy "
                                                          "for those who wear a watch on their dominant hand.\n"
                                                          "General: {}%. Same: {}%. Diff: {}%."
                        .format(general_accuracy, same_accuracy, diff_accuracy))

        self.assertTrue(general_accuracy < diff_accuracy, "The targeted classifier did not improve accuracy "
                                                          "for those who wear a watch on their non-dominant hand.\n"
                                                          "General: {}%. Same: {}%. Diff: {}%."
                        .format(general_accuracy, same_accuracy, diff_accuracy))

    def get_features(self, limit=-1, dom_hand_is_watch_hand=False):

        self.cursor.execute("""
                            SELECT "meanXYZ", "stdXYZ", activity_id
                            FROM public."Featureset_1" fs1, public."Trial" trial, 
                                 public."Participant" ptcpt, public."Target" target
                            WHERE fs1.trial_id = trial.id
                            AND target.trial_id = trial.id
                            AND trial.participant_id = ptcpt.id
                            AND ptcpt.dom_hand {} ptcpt.watch_hand
                            {};
                            """.format(
                                "=" if dom_hand_is_watch_hand else "<>",
                                "LIMIT ALL" if limit == -1 else """LIMIT {}""".format(limit)
                            ))

        features = [[attrs[0][0], attrs[0][1], attrs[0][2], attrs[1][0], attrs[1][1], attrs[1][2], attrs[2]]
                    for attrs in self.cursor.fetchall()]
        return features


if __name__ == "__main__":
    unittest.main()
