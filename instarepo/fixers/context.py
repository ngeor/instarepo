import functools
from typing import Optional
import instarepo.git
import instarepo.github
import instarepo.fixers.config


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

    @functools.lru_cache()
    def full_name(self):
        """
        Gets the full name of the repository.
        If the GitHub metadata is available in the 'repo' field, that is returned directly.
        Otherwise, i.e. for locally checked out repos, the method tries to extract the
        full name from the git remote URL.
        """
        if self.repo:
            return self.repo.full_name
        remote_url = self.git.get_remote_url()
        prefix = "git@github.com:"
        if remote_url.startswith(prefix):
            result = remote_url[len(prefix) :]
        else:
            raise ValueError(
                f"Unsupported git remote {remote_url} did not start with {prefix}"
            )
        suffix = ".git"
        if result.endswith(suffix):
            result = result[: -len(suffix)]
        else:
            raise ValueError(
                f"Unsupported git remote {remote_url} did not end with {suffix}"
            )
        return result

    def get_setting(self, key: str):
        return self.config.get_setting(self.full_name(), key)

    @functools.lru_cache()
    def default_branch(self):
        if self.repo:
            return self.repo.default_branch
        return self.git.get_default_branch()
