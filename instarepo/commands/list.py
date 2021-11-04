import instarepo.github
import instarepo.repo_source


class ListCommand:
    def __init__(self, args):
        self.repo_source = (
            instarepo.repo_source.RepoSourceBuilder().with_args(args).build()
        )

    def run(self):
        print("repo", "language", "updated at")
        repos = self.repo_source.get()
        for repo in repos:
            print(repo.name, repo.language, repo.updated_at)
