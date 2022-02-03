from ..credentials import PlatformCredentials


class LogoutCommand:
    def __init__(self, args):
        self.args = args

    def run(self):
        credentials = PlatformCredentials()
        credentials.clear()
