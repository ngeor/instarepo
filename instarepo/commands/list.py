import instarepo.github
import instarepo.repo_source


class ListCommand:
    def __init__(self, args):
        self.repo_source = (
            instarepo.repo_source.RepoSourceBuilder().with_args(args).build()
        )
        # remember sort order so that if we're sorting by a date field,
        # we'll be able to show that field on the last column
        self.sort = args.sort

    def run(self):
        repos = list(self.repo_source.get())
        if not repos:
            print("No repos found")
            return
        default_language = "N/A"
        max_repo_name_length = max(len(repo.name) for repo in repos)
        max_language_length = max(
            len(repo.language or default_language) for repo in repos
        )
        print(
            "{0:{1}s} {2:{3}s} {4}".format(
                "repo",
                max_repo_name_length,
                "language",
                max_language_length,
                date_column_title(self.sort),
            )
        )
        for repo in repos:
            print(
                "{0:{1}s} {2:{3}s} {4}".format(
                    repo.name,
                    max_repo_name_length,
                    repo.language or default_language,
                    max_language_length,
                    date_column_value(self.sort, repo),
                )
            )


def date_column_title(sort):
    if sort == "created":
        return "created at"
    elif sort == "updated":
        return "updated at"
    else:
        return "pushed at"


def date_column_value(sort, repo):
    if sort == "created":
        return repo.created_at
    elif sort == "updated":
        return repo.updated_at
    else:
        return repo.pushed_at
