"""
Fixers regarding CI.
"""

import os.path
import re
import instarepo.fixers.base
import instarepo.git


class NoTravisFix:
    """Removes the .travis.yml file"""

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        self.git = git

    def run(self):
        filename = ".travis.yml"
        full_name = os.path.join(self.git.dir, filename)
        if not os.path.isfile(full_name):
            return []
        self.git.rm(filename)
        msg = f"chore: Removed {filename}"
        self.git.commit(msg)
        return [msg]


class NoTravisBadgeFix(instarepo.fixers.base.SingleFileFix):
    """Removes the Travis badge from README files"""

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        super().__init__(git, "README.md", "chore: Removed Travis badge from README")

    def convert(self, contents: str) -> str:
        return remove_travis_badge(contents)


RE_BADGE = re.compile(
    r"\[!\[Build Status\]\(https://travis-ci[^)]+\)\]\(https://travis-ci[^)]+\)"
)


def remove_travis_badge(contents: str) -> str:
    return RE_BADGE.sub("", contents)
