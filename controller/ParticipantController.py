from utils.response_utils import error, success
from model.participant import Participant
from utils.db_utils import get_database
from flask import jsonify


def post(idx, dom_hand, watch_hand, gender):
    # Validate the input.
    if None in [idx, dom_hand, watch_hand, gender]:
        return error("Missing attributes.", "id, dom_hand, watch_hand, and gender are all required Participant fields.")

    # Get a database connection.
    database_conn = get_database()
    cursor = database_conn.cursor()

    # Check if the participant already exists.
    cursor.execute("""
                    SELECT COUNT(*)
                    FROM public."Participant"
                    WHERE id=%s;
                    """, (idx,))
    count = cursor.fetchone()[0]

    # Return if the participant exists.
    if count != 0:
        return error("Participant already exists.", "A participant with that ID has already been added.")

    # Add the new participant.
    cursor.execute("""
                    INSERT INTO
                    public."Participant"
                    (id, dom_hand, watch_hand, gender)
                    VALUES (%s, %s, %s, %s);
                    """, (idx, dom_hand, watch_hand, gender))

    # Commit and close the connection.
    database_conn.commit()
    cursor.close()
    database_conn.close()

    return success("Participant {} added.".format(idx))


def get(idx):
    # Get a database connection.
    database_conn = get_database()
    cursor = database_conn.cursor()

    # If there's no ID, select all participants.
    if idx is None:
        cursor.execute("""
                        SELECT id, dom_hand, watch_hand, gender
                        FROM public."Participant";
                        """)

        # Create a list of json participants.
        participants = []
        for attrs in cursor.fetchall():
            participants.append(Participant(attrs[0], attrs[1], attrs[2], attrs[3]).__dict__)

        # Return all participants.
        return jsonify({"participants": participants})

    else:
        # Find the specific participant.
        cursor.execute("""
                        SELECT id, dom_hand, watch_hand, gender
                        FROM public."Participant"
                        WHERE id=%s;
                        """, (idx,))
        attrs = cursor.fetchone()

        if attrs is None:
            return jsonify({"participant": None})
        else:
            # Return the json participant.
            return jsonify({"participant": Participant(attrs[0], attrs[1], attrs[2], attrs[3]).__dict__})
