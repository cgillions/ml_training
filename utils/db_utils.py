import psycopg2
import os


LEFT_TARGET = 10
RIGHT_TARGET = 20


DATABASE_URL = os.environ["DATABASE_URL"]


# Method to return a database connection.
def get_database():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


# Map of activity names to target values.
name_id_map = {
    "Walking": 10,
    10: "Walking",
    "Jogging": 20,
    20: "Jogging",
    "Cycling": 30,
    30: "Cycling",
    "Writing": 40,
    40: "Writing",
    "Typing": 50,
    50: "Typing",
    "Sitting": 60,
    60: "Sitting",
    "Standing": 70,
    70: "Standing",
    "On Phone (sit)": 80,
    80: "On Phone (sit)",
    "On Phone (stand)": 90,
    90: "On Phone (stand)",
    "Idle": 100,
    100: "Idle",
}
