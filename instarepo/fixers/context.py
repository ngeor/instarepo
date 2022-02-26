import instarepo.git
import instarepo.github
import instarepo.fixers.config
from typing import Optional


class Context:
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        config: instarepo.fixers.config.Config,
        repo: Optional[instarepo.github.Repo] = None,
        github: Optional[instarepo.github.GitHub] = None,
        verbose: bool = False,
    ):
        self.git = git
        self.config = config
        self.repo = repo
        self.github = github
        self.verbose = verbose
