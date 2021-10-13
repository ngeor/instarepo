import requests
import instarepo.github
import instarepo.repo_source


class ListCommand:
    def __init__(self, args):
        self.github = instarepo.github.GitHub(
            auth=requests.auth.HTTPBasicAuth(args.user, args.token),
        )
        self.repo_prefix: str = args.repo_prefix
        self.verbose: bool = args.verbose
        self.forks: bool = args.forks
        self.sort: str = args.sort
        self.direction: str = args.direction

    def run(self):
        print("repo", "updated at")
        repos = instarepo.repo_source.get_repos(
            self.github,
            self.sort,
            self.direction,
            repo_prefix=self.repo_prefix,
            forks=self.forks,
        )
        for repo in repos:
            print(repo.name, repo.updated_at)
