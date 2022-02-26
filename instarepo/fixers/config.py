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

    def get_setting(self, full_name: str, key: str):
        if "repos" in self._config:
            repos = self._config["repos"]
            if full_name in repos:
                repo_settings = repos[full_name]
                if key in repo_settings:
                    return repo_settings[key]
        if "defaults" in self._config:
            default_settings = self._config["defaults"]
            if key in default_settings:
                return default_settings[key]


class Config:
    def __init__(self, user_config: PartialConfig, default_config: PartialConfig):
        self._user_config = user_config
        self._default_config = default_config

    def get_setting(self, full_name: str, key: str):
        result = self._user_config.get_setting(full_name, key)
        if result is None:
            return self._default_config.get_setting(full_name, key)
        else:
            return result


def load_default_config():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "config.json")
    return load_partial_config(filename)


def load_partial_config(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return PartialConfig(json.load(file))
