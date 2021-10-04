import argparse
import subprocess
import tempfile

import requests


def main():
    args = parse_args()
    auth = requests.auth.HTTPBasicAuth(args.user, args.token)
    repos = get_all_repos(auth)
    for repo in repos:
        archived = repo["archived"]
        if not archived:
            print(repo["name"])
            processor = RepoProcessor(repo, auth)
            processor.process()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Apply changes on multiple repositories"
    )
    parser.add_argument(
        "-u", "--user", action="store", required=True, help="The GitHub username"
    )
    parser.add_argument(
        "-t", "--token", action="store", required=True, help="The GitHub token"
    )
    return parser.parse_args()


def get_all_repos(auth):
    page = 1
    per_page = 1  # TODO 30
    has_more = True
    while has_more:
        count = 0
        for repo in get_all_repos_of_page(auth, page, per_page):
            count = count + 1
            yield repo
        page = page + 1
        has_more = False  # TODO count >= per_page


def get_all_repos_of_page(auth, page: int, per_page: int):
    # https://docs.github.com/en/rest/reference/repos#list-repositories-for-the-authenticated-user
    response = requests.get(
        "https://api.github.com/user/repos",
        auth=auth,
        headers={"Accept": "application/vnd.github.v3+json"},
        params={
            "page": page,  # first page's index is 1
            "per_page": per_page,  # Default: 30
            "visibility": "all",  # Can be one of all, public, or private. Default: all
            "affiliation": "owner",  # Comma-separated list of values. Default: owner,collaborator,organization_member
        },
    )
    response.raise_for_status()
    for repo in response.json():
        yield repo


class RepoProcessor:
    def __init__(self, repo, auth):
        self.repo = repo
        self.auth = auth
        self.clone_dir = ""

    def process(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            print("created temp dir", tmpdirname)
            self.clone_dir = tmpdirname
            self.prepare()
            self.run_fixes()
            if self.has_changes():
                self.create_merge_request()

    def prepare(self):
        ssh_url = self.repo["ssh_url"]
        subprocess.run(["git", "clone", ssh_url, self.clone_dir], check=True)
        subprocess.run(
            ["git", "checkout", "-b", "instarepo_branch"],
            check=True,
            cwd=self.clone_dir,
        )
        print(ssh_url)
        pass

    def run_fixes(self):
        with open(self.clone_dir + "/test.txt", "w") as f:
            f.write("hello, world")
        subprocess.run(["git", "add", "test.txt"], check=True, cwd=self.clone_dir)
        subprocess.run(
            ["git", "commit", "-m", "Adding a test.txt file"],
            check=True,
            cwd=self.clone_dir,
        )

    def has_changes(self):
        return True

    def create_merge_request(self):
        print("Would have created PR")
        return
        subprocess.run(
            ["git", "push", "-u", "origin", "HEAD"], check=True, cwd=self.clone_dir
        )
        # https://docs.github.com/en/rest/reference/pulls#create-a-pull-request
        response = requests.post(
            f"https://api.github.com/repos/{self.repo['full_name']}/pulls",
            auth=self.auth,
            headers={"Accept": "application/vnd.github.v3+json"},
            json={
                "head": "instarepo_branch",
                "base": self.repo["default_branch"],
                "title": "instarepo automatic PR",
                "body": "The following fixes have been applied",
            },
        )
        result = response.json()
        print(result)
        response.raise_for_status()
        print("A PR has been created: ", result["html_url"])


if __name__ == "__main__":
    main()
