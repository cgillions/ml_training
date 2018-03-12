class User:

    id = None
    username = None
    auth_token = None

    def __init__(self, idx, username, auth_token):
        self.id = idx
        self.username = username
        self.auth_token = auth_token
