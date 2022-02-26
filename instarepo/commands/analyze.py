import logging
import os
import tempfile
from datetime import date, datetime

import instarepo.git
import instarepo.github
import instarepo.repo_source


class AnalyzeCommand:
    def __init__(self, args):
        self.repo_source = (
            instarepo.repo_source.RepoSourceBuilder().with_args(args).build()
        )
        self.verbose: bool = args.verbose
        # TODO find date of oldest commit:
        # $ git show -s --format=%ci $(git rev-list --max-parents=0 HEAD) | cut -d' ' -f1
        # 2017-02-18
        self.since = datetime.strptime(args.since, "%Y-%m-%d").date()
        self.metric: str = args.metric

    def run(self):
        repos = self.repo_source.get()
        for repo in repos:
            self.process(repo)

    def process(self, repo: instarepo.github.Repo):
        logging.info("Processing repo %s", repo.name)
        with tempfile.TemporaryDirectory() as tmpdirname:
            logging.debug("Cloning repo into temp dir %s", tmpdirname)
            git = instarepo.git.clone(repo.ssh_url, tmpdirname, quiet=not self.verbose)
            self.process_git(git)

    def process_git(self, git: instarepo.git.GitWorkingDir):
        if self.metric == "commits":
            self.print_commits(git)
        elif self.metric == "files":
            self.print_files(git)
        else:
            raise ValueError("Unknown metric " + self.metric)

    def print_commits(self, git: instarepo.git.GitWorkingDir):
        print("Since,Until,Commit Count")
        for dt in generate_date_range(self.since):
            since, until = dt, next_month(dt)
            result = git.rev_list(since, until)
            print(f"{since},{until},{len(result)}")

    def print_files(self, git: instarepo.git.GitWorkingDir):
        print("Since,Until,Commit Date,File Count,LOC")
        current_branch_name = git.current_branch_name()
        for dt in generate_date_range(self.since):
            since, until = dt, next_month(dt)
            oldest_commit_id = oldest_commit_between_dates(git, since, until)
            if oldest_commit_id:
                git.checkout(oldest_commit_id)
                oldest_commit_date = git.commit_date(oldest_commit_id)

                stats = {"file": 0, "loc": 0}
                stats = count_files(git.dir, composite_counter, stats)
                print(
                    f'{since},{until},{oldest_commit_date},{stats["file"]},{stats["loc"]}'
                )
                git.checkout(current_branch_name)


def generate_date_range(since):
    stop = date.today()
    i = since
    while i < stop:
        yield i
        i = next_month(i)


def next_month(dt):
    if dt.month == 12:
        return date(dt.year + 1, 1, 1)
    else:
        return date(dt.year, dt.month + 1, 1)


def count_files(path, visitor, result):
    with os.scandir(path) as iterator:
        for entry in iterator:
            if entry.is_file():
                result = visitor(result, path, entry.name)
            elif entry.is_dir() and not entry.name.startswith("."):
                result = count_files(os.path.join(path, entry.name), visitor, result)
    return result


def file_counter(result, path, name):
    return result + 1


def loc(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return len(file.readlines())
    except:
        return 0


def loc_counter(result, path, name):
    return result + loc(os.path.join(path, name))


def composite_counter(result, path, name):
    result["file"] = file_counter(result["file"], path, name)
    result["loc"] = loc_counter(result["loc"], path, name)
    return result


def oldest_commit_between_dates(git: instarepo.git.GitWorkingDir, since, until):
    lines = git.rev_list(since, until, reverse=True)
    return lines[0] if len(lines) > 0 else ""
