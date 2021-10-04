import argparse
import requests
import instarepo.git


def main():
    repos = get_all_repos()
    for repo in repos:
        processor = RepoProcessor(repo)
        processor.process()


def get_all_repos():
    pass


class RepoProcessor:
    def __init__(self, repo):
        self.repo = repo

    def process(self):
        self.prepare()
        self.run_fixes()
        if self.has_changes():
            self.create_merge_request()

    def prepare(self):
        pass

    def run_fixes(self):
        pass

    def has_changes(self):
        pass

    def create_merge_request(self):
        pass


if __name__ == "__main__":
    print("hello from Python")
    instarepo.git.hello_from_git()
