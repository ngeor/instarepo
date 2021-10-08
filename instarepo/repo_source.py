import random
from typing import Iterable

import instarepo.github

SAMPLE_SIZE = 5


def get_repos(
    github: instarepo.github.GitHub, sample=False
) -> Iterable[instarepo.github.Repo]:
    all_repos = github.get_all_repos()
    non_archived_repos = exclude_archived(all_repos)
    if sample:
        collected = []
        for repo in non_archived_repos:
            collected.append(repo)
            if len(collected) >= SAMPLE_SIZE:
                break
        return [random.choice(collected)]
    else:
        return non_archived_repos


def exclude_archived(repos: Iterable[instarepo.github.Repo]):
    for repo in repos:
        if not repo.archived:
            yield repo
