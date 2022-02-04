import logging
import os.path
import re
from typing import List, Optional

import instarepo.git
import instarepo.github


RE_DESCRIPTION_LINE = re.compile(r"^[>A-Za-z]")


class RepoDescriptionFix:
    """
    Updates GitHub's repo description based on the README file.

    Note: this fixer does not create an MR, it calls the
    GitHub REST API directly (https://docs.github.com/en/rest/reference/repos#update-a-repository).

    Does not run for local git repositories.
    """

    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        github: Optional[instarepo.github.GitHub],
        repo: Optional[instarepo.github.Repo],
        **kwargs
    ):
        self.github = github
        self.git = git
        self.repo = repo

    def run(self):
        readme_description = self.get_readme_description()
        if not readme_description or not self.repo or not self.github:
            return []
        if readme_description != self.repo.description:
            logging.info(
                "Repo description %s does not match readme description %s",
                self.repo.description,
                readme_description,
            )
            self.github.update_description(self.repo.full_name, readme_description)
        # this fixer does not create an MR
        return []

    def get_readme_description(self):
        filename = os.path.join(self.git.dir, "README.md")
        if not os.path.isfile(filename):
            return None
        with open(filename) as f:
            # read lines
            lines = f.readlines()
            # trim
            lines = [line.strip() for line in lines]
            # keep the ones that start with a letter
            lines = [line for line in lines if RE_DESCRIPTION_LINE.match(line)]
            return get_description_from_lines(lines)


def get_description_from_lines(lines: List[str]) -> str:
    if not lines:
        return ""
    line = lines[0]
    if line.startswith(">"):
        line = line[1:].strip()
    return line
