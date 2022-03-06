import instarepo.fixers.context
from instarepo.fixers.base import MissingFileFix


class MustHaveCliffTomlFix(MissingFileFix):
    """Ensures the configuration for git-cliff (cliff.toml) exists"""

    order = -100

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, "cliff.toml")
        self.context = context

    def should_process_repo(self):
        return self._get_template_filename()

    def get_contents(self):
        with open(self._get_template_filename(), "r", encoding="utf-8") as file:
            return file.read()

    def _get_template_filename(self):
        return self.context.get_setting("cliff.toml")
