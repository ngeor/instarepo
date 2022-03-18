from instarepo.fixers.base import MissingFileFix


class MustHaveCliffTomlFix(MissingFileFix):
    """Ensures the configuration for git-cliff (cliff.toml) exists"""

    order = -100

    def should_process_repo(self):
        return self._get_template_filename()

    def get_contents(self):
        with open(self._get_template_filename(), "r", encoding="utf-8") as file:
            return file.read()

    def get_filename(self):
        return "cliff.toml"

    def _get_template_filename(self):
        return self.context.get_setting("cliff.toml")
