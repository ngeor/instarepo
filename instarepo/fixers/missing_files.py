import instarepo.git
import instarepo.github
from instarepo.fixers.base import MissingFileFix


class MustHaveReadmeFix(MissingFileFix):
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: instarepo.github.Repo,
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
    def __init__(self, git: instarepo.git.GitWorkingDir):
        super().__init__(git, ".editorconfig")

    def get_contents(self):
        return EDITOR_CONFIG


FUNDING_YML = """# These are supported funding model platforms

github: # Replace with up to 4 GitHub Sponsors-enabled usernames e.g., [user1, user2]
patreon: # Replace with a single Patreon username
open_collective: # Replace with a single Open Collective username
ko_fi: # Replace with a single Ko-fi username
tidelift: # Replace with a single Tidelift platform-name/package-name e.g., npm/babel
community_bridge: # Replace with a single Community Bridge project-name e.g., cloud-foundry
liberapay: # Replace with a single Liberapay username
issuehunt: # Replace with a single IssueHunt username
otechie: # Replace with a single Otechie username
custom: ['https://ngeor.com/support/']
"""


class MustHaveGitHubFundingFix(MissingFileFix):
    def __init__(self, git: instarepo.git.GitWorkingDir, repo: instarepo.github.Repo):
        super().__init__(git, ".github/FUNDING.yml")
        self.repo = repo

    def should_process_repo(self):
        return not self.repo.private and not self.repo.fork

    def get_contents(self):
        return FUNDING_YML
