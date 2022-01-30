import os.path
import requests
import instarepo.git
import instarepo.github
from instarepo.fixers.base import MissingFileFix
from .finders import is_lazarus_project, is_maven_project, is_vb6_project


class MustHaveReadmeFix(MissingFileFix):
    """Ensures that the repo has a readme file"""

    def __init__(
        self, git: instarepo.git.GitWorkingDir, repo: instarepo.github.Repo, **kwargs
    ):
        super().__init__(git, "README.md")
        self.repo = repo

    def get_contents(self):
        contents = f"# {self.repo.name}\n"
        if self.repo.description:
            contents = contents + "\n" + self.repo.description + "\n"
        return contents


EDITOR_CONFIG = """# Editor configuration, see https://editorconfig.org
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 120

[*.sh]
end_of_line = lf
"""


class MustHaveEditorConfigFix(MissingFileFix):
    """Ensures an editorconfig file exists"""

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        super().__init__(git, ".editorconfig")

    def get_contents(self):
        return EDITOR_CONFIG


class MustHaveGitHubFundingFix(MissingFileFix):
    """
    Ensures a GitHub funding file exists (.github/FUNDING.yml).
    The rule will use the FUNDING.yml file from `user-templates/.github/FUNDING.yml`,
    if one exists.
    """

    def __init__(
        self, git: instarepo.git.GitWorkingDir, repo: instarepo.github.Repo, **kwargs
    ):
        super().__init__(git, ".github/FUNDING.yml")
        self.repo = repo
        template = os.path.join(
            os.path.basename(__file__),
            "..",
            "..",
            "user-templates",
            ".github",
            "FUNDING.yml",
        )
        self.contents = ""
        if os.path.isfile(template):
            with open(template, "r", encoding="utf-8") as file:
                self.contents = file.read()

    def should_process_repo(self):
        return not self.repo.private and not self.repo.fork and self.contents

    def get_contents(self):
        return self.contents


class MustHaveGitIgnoreFix(MissingFileFix):
    """Ensures a .gitignore file exists"""

    LAZARUS_GITIGNORE = """*.o
*.ppu
*.obj
*.exe
*.dll
*.compiled
*.bak
*.lps
backup/
"""
    VB6_GITIGNORE = """*.exe
*.dll
*.ocx
*.vbw
"""

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        super().__init__(git, ".gitignore")

    def get_contents(self):
        if is_maven_project(self.git.dir):
            # https://github.com/github/gitignore/blob/master/Maven.gitignore
            response = requests.get(
                "https://raw.githubusercontent.com/github/gitignore/master/Maven.gitignore"
            )
            response.raise_for_status()
            return response.text
        if is_lazarus_project(self.git.dir):
            return self.LAZARUS_GITIGNORE
        if is_vb6_project(self.git.dir):
            return self.VB6_GITIGNORE
        return None
