from app import get_database


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


class Activity(object):

    name = None
    id = None

    def __init__(self, idx, name):
        self.name = name
        self.id = idx

    @staticmethod
    def get():
        activities = []
        database_conn = get_database()
        cursor = database_conn.cursor()
        cursor.execute("SELECT (id, name) FROM public.\"Activity\";")

        for activity in cursor:
            activities.append(Activity(activity[0], activity[1]))

        cursor.close()
        database_conn.close()
