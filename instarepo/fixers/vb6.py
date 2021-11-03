import os

import instarepo.git
from instarepo.fixers.base import MissingFileFix


def is_vb6_project(dir: str) -> bool:
    """
    Checks if the given directory is a VB6 project.
    """
    with os.scandir(dir) as it:
        for entry in it:
            if entry.name.endswith(".vbp") and entry.is_file():
                return True
    return False


VB6_GITIGNORE = """*.exe
*.dll
*.ocx
*.vbw
"""


class MustHaveVB6GitIgnore(MissingFileFix):
    def __init__(self, git: instarepo.git.GitWorkingDir):
        super().__init__(git, ".gitignore")

    def should_process_repo(self):
        return is_vb6_project(self.git.dir)

    def get_contents(self):
        return VB6_GITIGNORE