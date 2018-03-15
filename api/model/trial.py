class Trial(object):

    id = None
    user_id = None
    filename = None
    data = None

    def __init__(self, idx, user_id, filename, data):
        self.id = idx
        self.user_id = user_id
        self.filename = filename
        self.data = data
