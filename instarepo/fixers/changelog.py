import os.path
import instarepo.git
from instarepo.fixers.base import MissingFileFix


class MustHaveCliffTomlFix(MissingFileFix):
    """Ensures the configuration for git-cliff (cliff.toml) exists"""

    order = -100

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        super().__init__(git, "cliff.toml")

    def get_contents(self):
        template = os.path.join(os.path.dirname(__file__), "..", "..", "cliff.toml")
        with open(template, "r", encoding="utf-8") as file:
            return file.read()
