from model.activity import name_id_map


class Target(object):

    @staticmethod
    def get_targets(activity_id):
        name = name_id_map[activity_id]

        if name in ["Sitting", "Standing", "On Phone (sit)", "On Phone (stand)"]:
            return [activity_id, name_id_map["Idle"]]

        else:  # if name in ["Walking", "Jogging", "Cycling", "Writing", "Typing"]
            return [activity_id]
