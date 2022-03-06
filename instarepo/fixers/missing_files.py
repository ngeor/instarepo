import requests
import instarepo.fixers.context
import instarepo.git
import instarepo.github
from instarepo.fixers.base import MissingFileFix
from .finders import is_lazarus_project, is_maven_project, is_vb6_project


class MustHaveReadmeFix(MissingFileFix):
    """
    Ensures that the repo has a readme file.

    Does not run for locally checked out repositories.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, "README.md")
        self.repo = context.repo

    def get_contents(self):
        contents = f"# {self.repo.name}\n"
        if self.repo.description:
            contents = contents + "\n" + self.repo.description + "\n"
        return contents

    def should_process_repo(self) -> bool:
        return self.repo is not None


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

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, ".editorconfig")

    def get_contents(self):
        return EDITOR_CONFIG


class MustHaveGitHubFundingFix(MissingFileFix):
    """
    Ensures a GitHub funding file exists (.github/FUNDING.yml).
    The template file needs to be configured in the configuration file.

    Does not run for locally checked out repositories.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, ".github/FUNDING.yml")
        self.context = context

    def should_process_repo(self):
        return (
            self.context.repo
            and not self.context.repo.private
            and not self.context.repo.fork
            and self._get_template_filename()
        )

    def get_contents(self):
        with open(self._get_template_filename(), "r", encoding="utf-8") as file:
            return file.read()

    def _get_template_filename(self):
        return self.context.get_setting("funding.yml")


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

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, ".gitignore")

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
