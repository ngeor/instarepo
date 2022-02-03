from ..credentials import PlatformCredentials


class LoginCommand:
    def __init__(self, args):
        self.args = args

    def run(self):
        credentials = PlatformCredentials()
        credentials.store(self.args)
