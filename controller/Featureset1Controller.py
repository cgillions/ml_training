from utils.db_utils import get_database, get_attributes
from utils.response_utils import error, success
from model.featureset1 import Featureset1
from flask import jsonify


def post(file):
    if file is None:
        return error("Featureset 1 file is missing.",
                     "The POST request is missing the file containing feature data.")

    database_conn = get_database()
    cursor = database_conn.cursor()
    ids = []
    targets = []
    index = 0
    try:
        for line in file:
            index += 1

            # Get the features from the line.
            features = line.split(",")

            # Validate the length.
            if len(features) != 7:
                remove_files(database_conn, cursor, ids, targets)
                cursor.close()
                database_conn.close()
                return error("The wrong amount of features were sent.",
                             "On line {} there were {} values instead of 7. "
                             "There should be 6 features and one target."
                             .format(index, len(features)))

            # Store the data in the database.
            cursor.execute("""
                            INSERT INTO 
                            public."Featureset_1" (meanXYZ, stdXYZ) 
                            VALUES (%s, %s) 
                            RETURNING id;
                            """, (
                [features[0], features[1], features[2]],
                [features[3], features[4], features[5]]))

            # Commit the transaction.
            database_conn.commit()

            # Get the ID and target of the new feature.
            idx = cursor.fetchone()[0]
            target = features[6]

            # Store the target.
            cursor.execute("""
                            INSERT INTO 
                            public."Target" (feature_id, activity_id) 
                            VALUES (%s, %s);
                            """, (idx, target))

            targets.append(target)
            ids.append(idx)

        cursor.close()
        database_conn.close()
        return success("{} features added.".format(len(ids)))

    # Delete any database entries if there was an error.
    except():
        remove_files(database_conn, cursor, ids, targets)
        cursor.close()
        database_conn.close()
        return error("Error storing featureset.", "An unknown error occurred on line {}.".format(index))


def get():
    features = []
    database_conn = get_database()
    cursor = database_conn.cursor()
    cursor.execute("""
                    SELECT id, "meanXYZ", "stdXYZ"
                    FROM public."Featureset_1";
                    """)

    for attrs in cursor:
        features.append(Featureset1(attrs[0], attrs[1], attrs[2]).__dict__)

    cursor.close()
    database_conn.close()
    return jsonify({"features": features})


# Function to remove any files added to the database before an error occurred.
def remove_files(database_conn, cursor, feature_ids, target_ids):
    cursor.execute("""
                    DELETE FROM 
                    public."Featureset_1" 
                    WHERE id IN (%s);
                    """, (",".join(feature_ids),))

    for idx, target in zip(feature_ids, target_ids):
        cursor.execute("""
                    DELETE FROM 
                    public."Target" 
                    WHERE feature_id=(%s) 
                    AND activity_id=(%s);
                    """, (idx, target))

    database_conn.commit()
