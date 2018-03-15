class Participant(object):

    id = None
    dom_hand = None
    watch_hand = None
    gender = None

    def __init__(self, idx, dom_hand, watch_hand, gender):
        self.id = idx
        self.dom_hand = dom_hand
        self.watch_hand = watch_hand
        self.gender = gender
