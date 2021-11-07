import os

import instarepo.git
from instarepo.fixers.base import MissingFileFix


def is_vb6_project(dir: str) -> bool:
    """
    Checks if the given directory is a VB6 project.
    """
    with os.scandir(dir) as it:
        for entry in it:
            if entry.is_file() and has_vb6_extension(entry):
                return True
    return False


def has_vb6_extension(entry):
    return entry.name.endswith(".vbp") or entry.name.endswith(".vbg")


VB6_GITIGNORE = """*.exe
*.dll
*.ocx
*.vbw
"""


class MustHaveGitIgnore(MissingFileFix):
    """If mising, adds a gitignore file for VB6 projects"""

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        super().__init__(git, ".gitignore")

    def should_process_repo(self):
        return is_vb6_project(self.git.dir)

    def get_contents(self):
        return VB6_GITIGNORE
