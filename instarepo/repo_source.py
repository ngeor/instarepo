from typing import Iterable
from enum import Enum, auto, unique

import instarepo.github
import requests


@unique
class FilterMode(Enum):
    """
    Controls filtering of repositories based on a boolean property (e.g. 'archived').

    ALLOW: Allows repositories, regardless of the property value
    DENY: Includes only repositories where the property is false
    ONLY: Includes only repositories where the property is true
    """

    ALLOW = auto()
    DENY = auto()
    ONLY = auto()


class RepoSource:
    """
    Retrieves repository information from GitHub.
    """

    def __init__(
        self,
        github: instarepo.github.GitHub,
        sort: str,
        direction: str,
        archived: FilterMode,
        forks: FilterMode,
        repo_prefix: str,
    ):
        """
        Creates an instance of this class

        Parameters:

        :param github: The instance of the GitHub client
        :param sort: The field to sort by
        :param direction: The direction to sort by
        :param archived: Determines how to filter archived repositories
        :param forks: Determines how to filter forks
        :param repo_prefix: Optionally filter repositories whose name starts with this prefix
        """
        self.github = github
        self.sort = sort
        self.direction = direction
        self.archived = archived
        self.forks = forks
        self.repo_prefix = repo_prefix

    def get(self) -> Iterable[instarepo.github.Repo]:
        """
        Retrieves repository information from GitHub.
        """
        return self._filter_prefix(
            self._filter_forks(
                self._filter_archived(
                    self.github.get_all_repos(self.sort, self.direction)
                )
            )
        )

    def _filter_archived(self, repos: Iterable[instarepo.github.Repo]):
        if self.archived == FilterMode.ONLY:
            return (repo for repo in repos if repo.archived)
        elif self.archived == FilterMode.DENY:
            return (repo for repo in repos if not repo.archived)
        else:
            return repos

    def _filter_forks(self, repos: Iterable[instarepo.github.Repo]):
        if self.forks == FilterMode.ONLY:
            return (repo for repo in repos if repo.fork)
        elif self.forks == FilterMode.DENY:
            return (repo for repo in repos if not repo.fork)
        else:
            return repos

    def _filter_prefix(self, repos: Iterable[instarepo.github.Repo]):
        if self.repo_prefix:
            return (repo for repo in repos if repo.name.startswith(self.repo_prefix))
        else:
            return repos


class RepoSourceBuilder:
    """
    A builder for RepoSource instances.
    """

    def __init__(self):
        """
        Creates an instance of this class.

        """
        self.github = None
        self.sort = None
        self.direction = None
        self.archived = FilterMode.DENY
        self.forks = FilterMode.DENY
        self.repo_prefix = None

    def with_github(self, github: instarepo.github.GitHub):
        """
        Uses the given GitHub client.
        """
        self.github = github
        return self

    def with_args(self, args):
        """
        Uses the properties defined in the given CLI arguments.

        If the github client is already set with the `with_github`
        method, it is not overwritten. Otherwise, it creates
        a read-only GitHub client.
        """
        if self.github is None:
            self.github = instarepo.github.GitHub(
                auth=requests.auth.HTTPBasicAuth(args.user, args.token),
            )
        self.sort = args.sort
        self.direction = args.direction
        self.forks = [
            member for member in FilterMode if member.name == args.forks.upper()
        ][0]
        if "archived" in args:
            self.archived = [
                member for member in FilterMode if member.name == args.archived.upper()
            ][0]
        self.repo_prefix = args.repo_prefix
        return self

    def build(self):
        """
        Builds a new `RepoSource` instance.
        """
        return RepoSource(
            self.github,
            self.sort,
            self.direction,
            self.archived,
            self.forks,
            self.repo_prefix,
        )
