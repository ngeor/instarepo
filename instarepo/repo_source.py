"""
Fetches repository info from GitHub.
"""

from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional
from enum import Enum, auto, unique

import instarepo.github

from .credentials import build_requests_auth


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

    @staticmethod
    def parse(value: str):
        """
        Parses the given string value and returns the FilterMode.
        Matching is case sensitive. If not found, an error will be thrown.
        """
        return [member for member in FilterMode if member.name == value][0]


class StringFilter:
    """
    Defines a string filter.
    Allows filtering repositories based on a string property.
    The combination of `value` and `mode` allows to
    include or exclude repositories based on the value of
    the property that is being filtered on.
    """

    def __init__(self, value: str = "", mode: FilterMode = FilterMode.ALLOW):
        self.value = value
        self.mode = mode


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
        repo_prefix: StringFilter,
        language: StringFilter,
        pushed_after,
        pushed_before,
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
        :param language: Optionally filter repositories by their language
        :param pushed_after: Optionally filter repositories that were pushed after the given timedelta
        :param pushed_before: Optionally filter repositories that were pushed before the given timedelta
        """
        self.github = github
        self.sort = sort
        self.direction = direction
        self.archived = archived
        self.forks = forks
        self.repo_prefix = repo_prefix
        self.language = language
        self.pushed_after = pushed_after
        self.pushed_before = pushed_before

    def get(self) -> Iterable[instarepo.github.Repo]:
        """
        Retrieves repository information from GitHub.
        """
        return self._filter_pushed_after(
            self._filter_pushed_before(
                self._filter_language(
                    self._filter_prefix(
                        self._filter_forks(
                            self._filter_archived(
                                self.github.get_all_repos(self.sort, self.direction)
                            )
                        )
                    )
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
        return filter_by_name_prefix(repos, self.repo_prefix)

    def _filter_language(self, repos: Iterable[instarepo.github.Repo]):
        return filter_by_language(repos, self.language)

    def _filter_pushed_after(self, repos: Iterable[instarepo.github.Repo]):
        if self.pushed_after:
            return (
                repo
                for repo in repos
                if repo.pushed_at + self.pushed_after > datetime.now(timezone.utc)
            )
        else:
            return repos

    def _filter_pushed_before(self, repos: Iterable[instarepo.github.Repo]):
        if self.pushed_before:
            return (
                repo
                for repo in repos
                if repo.pushed_at + self.pushed_before < datetime.now(timezone.utc)
            )
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
        self.sort: str = ""
        self.direction: str = ""
        self.archived = FilterMode.DENY
        self.forks = FilterMode.DENY
        self.repo_prefix = StringFilter()
        self.language = StringFilter()
        self.pushed_after = None
        self.pushed_before = None

    def with_github(self, github: instarepo.github.GitHub):
        """
        Uses the given GitHub client.
        """
        self.github = github
        return self

    def with_args(self, args) -> RepoSourceBuilder:
        """
        Uses the properties defined in the given CLI arguments.

        If the github client is already set with the `with_github`
        method, it is not overwritten. Otherwise, it creates
        a read-only GitHub client.
        """
        if self.github is None:
            self.github = instarepo.github.GitHub(auth=build_requests_auth(args))
        if "sort" in args:
            self.sort = args.sort
        if "direction" in args:
            self.direction = args.direction
        self.forks = FilterMode.parse(args.forks.upper())
        if "archived" in args:
            self.archived = FilterMode.parse(args.archived.upper())

        if args.only_name_prefix:
            self.repo_prefix = StringFilter(args.only_name_prefix, FilterMode.ONLY)
        elif args.except_name_prefix:
            self.repo_prefix = StringFilter(args.except_name_prefix, FilterMode.DENY)

        if args.only_language:
            self.language = StringFilter(args.only_language, FilterMode.ONLY)
        elif args.except_language:
            self.language = StringFilter(args.except_language, FilterMode.DENY)

        self.pushed_after = parse_timedelta(args.pushed_after)
        self.pushed_before = parse_timedelta(args.pushed_before)

        return self

    def build(self):
        """
        Builds a new `RepoSource` instance.
        """
        if self.github is None:
            raise ValueError("GitHub client is mandatory")
        return RepoSource(
            self.github,
            self.sort,
            self.direction,
            self.archived,
            self.forks,
            self.repo_prefix,
            self.language,
            self.pushed_after,
            self.pushed_before,
        )


def filter_by_name_prefix(
    repos: Iterable[instarepo.github.Repo], string_filter: Optional[StringFilter]
) -> Iterable[instarepo.github.Repo]:
    """
    Filters the given repos on their name using the given filter.
    """
    if (
        not string_filter
        or not string_filter.value
        or string_filter.mode == FilterMode.ALLOW
    ):
        return repos
    if string_filter.mode == FilterMode.ONLY:
        return (repo for repo in repos if repo.name.startswith(string_filter.value))
    elif string_filter.mode == FilterMode.DENY:
        return (repo for repo in repos if not repo.name.startswith(string_filter.value))
    else:
        raise ValueError("Invalid filter mode " + string_filter.mode)


def filter_by_language(
    repos: Iterable[instarepo.github.Repo], string_filter: StringFilter
) -> Iterable[instarepo.github.Repo]:
    """
    Filters the given repos on their language using the given filter.
    """
    if not string_filter or string_filter.mode == FilterMode.ALLOW:
        return repos
    if string_filter.mode == FilterMode.ONLY:
        if string_filter.value:
            return (repo for repo in repos if repo.language == string_filter.value)
        else:
            return (repo for repo in repos if not repo.language)
    elif string_filter.mode == FilterMode.DENY:
        if string_filter.value:
            return (repo for repo in repos if repo.language != string_filter.value)
        else:
            return (repo for repo in repos if repo.language)
    else:
        raise ValueError("Invalid filter mode " + string_filter.mode)


def parse_timedelta(value: Optional[str]):
    """
    Parses a time delta string value. For example "15m" is parsed as a
    timedelta of 15 minutes.
    """
    if not value:
        return None
    unit = value[-1]
    amount = int(value[0:-1])
    if unit == "h":
        return timedelta(hours=amount)
    elif unit == "m":
        return timedelta(minutes=amount)
    elif unit == "d":
        return timedelta(days=amount)
    else:
        raise ValueError(f"Invalid time unit: {value}")
