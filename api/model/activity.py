class Activity(object):

    id = None
    name = None
    end_time = None
    start_time = None
    confidence = None

    def __init__(self, idx, name, start_time=None, end_time=None, confidence=0):
        self.id = idx
        self.name = name
        self.end_time = end_time
        self.start_time = start_time
        self.confidence = confidence
