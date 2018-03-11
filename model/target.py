from model.activity import name_id_map


class Target(object):

    @staticmethod
    def get_targets(activity_name):
        if activity_name in ["Sitting", "Standing", "On Phone (sit)", "On Phone (stand)"]:
            return [name_id_map[activity_name], name_id_map["Idle"]]

        else:  # if name in ["Walking", "Jogging", "Cycling", "Writing", "Typing"]
            return [name_id_map[activity_name]]
