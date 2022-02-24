class Config:
    def __init__(self):
        self._config = {}

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
        