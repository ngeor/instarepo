import configparser
import os
import os.path
import pathlib
import requests.auth


class Credentials:
    def __init__(self, username, token):
        self.username = username
        self.token = token

    def is_valid(self):
        return self.username and self.token

    def with_fallback(self, fallback):
        return Credentials(
            self.username or fallback.username, self.token or fallback.token
        )


if os.name == "nt":
    import winreg

    class WindowsCredentials:
        def __init__(self):
            pass

        def load(self):
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE") as k1:
                with winreg.CreateKey(k1, "ngeor") as k2:
                    with winreg.CreateKey(k2, "instarepo") as k3:
                        username, _ = winreg.QueryValueEx(k3, "username")
                        token, _ = winreg.QueryValueEx(k3, "token")
                        return Credentials(username, token)

        def store(self, credentials: Credentials):
            username = credentials.username
            token = credentials.token
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE") as k1:
                with winreg.CreateKey(k1, "ngeor") as k2:
                    with winreg.CreateKey(k2, "instarepo") as k3:
                        winreg.SetValueEx(k3, "username", None, winreg.REG_SZ, username)
                        winreg.SetValueEx(k3, "token", None, winreg.REG_SZ, token)

        def clear(self):
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE") as k1:
                with winreg.CreateKey(k1, "ngeor") as k2:
                    with winreg.CreateKey(k2, "instarepo") as k3:
                        winreg.DeleteValue(k3, "username")
                        winreg.DeleteValue(k3, "token")


class DotFileCredentials:
    def __init__(self):
        self.filename = os.path.join(pathlib.Path.home(), ".instarepo.ini")

    def load(self):
        username = ""
        token = ""
        if os.path.isfile(self.filename):
            config = configparser.ConfigParser()
            config.read(self.filename, encoding="utf-8")
            if "DEFAULT" in config:
                default_section = config["DEFAULT"]
                username = default_section.get("username", "")
                token = default_section.get("token", "")
        return Credentials(username, token)

    def store(self, credentials: Credentials):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            "username": credentials.username,
            "token": credentials.token,
        }
        with open(self.filename, "w", encoding="utf-8") as file:
            config.write(file)

    def clear(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)


class PlatformCredentials:
    def __init__(self):
        if os.name == "nt":
            self.delegate = WindowsCredentials()
        else:
            self.delegate = DotFileCredentials()

    def load(self):
        return self.delegate.load()

    def store(self, credentials: Credentials):
        self.delegate.store(credentials)

    def clear(self):
        self.delegate.clear()


def load_credentials(args):
    args_credentials = Credentials(args.username, args.token)
    if args_credentials.is_valid():
        return args_credentials

    stored_credentials = PlatformCredentials().load()
    mixed_credentials = args_credentials.with_fallback(stored_credentials)
    if not mixed_credentials.is_valid():
        raise ValueError(
            "Credentials not provided. Use the CLI parameters or login first."
        )
    return mixed_credentials


def build_requests_auth(args):
    credentials = load_credentials(args)
    return requests.auth.HTTPBasicAuth(credentials.username, credentials.token)
