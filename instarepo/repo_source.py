from typing import Iterable

import instarepo.github


def get_repos(
    github: instarepo.github.GitHub,
    sort: str,
    direction: str,
    repo_prefix: str = "",
    forks: bool = True,
) -> Iterable[instarepo.github.Repo]:
    repos = github.get_all_repos(sort, direction)
    repos = (repo for repo in repos if not repo.archived)
    if not forks:
        repos = (repo for repo in repos if not repo.fork)
    if repo_prefix:
        repos = (repo for repo in repos if repo.name.startswith(repo_prefix))
    return repos
