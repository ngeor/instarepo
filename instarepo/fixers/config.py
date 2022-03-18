import json
import os.path


def load_config(filename: str):
    default_config = load_default_config()
    if filename:
        user_config = load_partial_config(filename)
        return Config(user_config, default_config)
    else:
        return default_config


class PartialConfig:
    def __init__(self, config):
        self._config = config

    def get_setting(self, full_name: str, *args):
        repo_value = _lookup_key(self._config, "repos", full_name, *args)
        if repo_value is None:
            return _lookup_key(self._config, "defaults", *args)
        else:
            return repo_value


class Config:
    def __init__(self, user_config: PartialConfig, default_config: PartialConfig):
        self._user_config = user_config
        self._default_config = default_config

    def get_setting(self, full_name: str, *args):
        result = self._user_config.get_setting(full_name, *args)
        if result is None:
            return self._default_config.get_setting(full_name, *args)
        else:
            return result


def load_default_config():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "config.json")
    return load_partial_config(filename)


def load_partial_config(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return PartialConfig(json.load(file))


def _lookup_key(dictionary, *args):
    if not dictionary:
        return None
    current = dictionary
    for key in args:
        if not key in current:
            return None
        current = current[key]
    return current
