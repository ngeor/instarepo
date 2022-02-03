import os.path
import subprocess
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


class GenerateChangelogFix:
    """Generates changelog with git-cliff"""

    order = 100

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        self.git = git

    def run(self):
        if not self.git.isfile("cliff.toml"):
            return []
        changelog_file = "CHANGELOG.md"
        # load existing CHANGELOG contents, if it exists
        old_contents = ""
        if self.git.isfile(changelog_file):
            with open(self.git.join(changelog_file), "r", encoding="utf-8") as file:
                old_contents = file.read()
        # regenerate it
        subprocess.run(
            ["git-cliff", "-o", changelog_file], check=True, cwd=self.git.dir
        )
        # read the new CHANGELOG contents
        with open(self.git.join(changelog_file), "r", encoding="utf-8") as file:
            new_contents = file.read()
        # if same, no commit needed
        if old_contents == new_contents:
            return []
        self.git.add(changelog_file)
        msg = "chore(changelog): Updated changelog"
        self.git.commit(msg)
        return [msg]
