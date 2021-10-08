import logging
import requests


class Repo:
    def __init__(self, repo_json):
        self.name: str = repo_json["name"]
        self.archived: bool = repo_json["archived"]
        self.ssh_url: str = repo_json["ssh_url"]
        self.default_branch: str = repo_json["default_branch"]
        self.full_name: str = repo_json["full_name"]
        self.description: str = repo_json["description"]


class GitHub:
    def __init__(self, auth):
        self.auth = auth

    def get_all_repos(self):
        page = 1
        per_page = 30
        has_more = True
        while has_more:
            count = 0
            for repo in self.get_all_repos_of_page(page, per_page):
                count = count + 1
                yield repo
            page = page + 1
            has_more = count >= per_page

    def get_all_repos_of_page(self, page: int, per_page: int):
        # https://docs.github.com/en/rest/reference/repos#list-repositories-for-the-authenticated-user
        response = requests.get(
            "https://api.github.com/user/repos",
            auth=self.auth,
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
            logging.debug("yield repo: %s", repo)
            yield Repo(repo)

    def create_merge_request(
        self, full_name: str, head: str, base: str, title: str, body: str
    ) -> str:
        logging.debug("Would have created MR")
        return ""

    def update_description(self, full_name: str, description: str):
        logging.debug("Would have set description of %s to %s", full_name, description)


class ReadWriteGitHub(GitHub):
    def __init__(self, auth):
        super().__init__(auth)

    def create_merge_request(
        self, full_name: str, head: str, base: str, title: str, body: str
    ) -> str:
        # https://docs.github.com/en/rest/reference/pulls#create-a-pull-request
        response = requests.post(
            f"https://api.github.com/repos/{full_name}/pulls",
            auth=self.auth,
            headers={"Accept": "application/vnd.github.v3+json"},
            json={
                "head": head,
                "base": base,
                "title": title,
                "body": body,
            },
        )
        result = response.json()
        response.raise_for_status()
        return result["html_url"]

    def update_description(self, full_name: str, description: str):
        # https://docs.github.com/en/rest/reference/repos#update-a-repository
        response = requests.patch(
            f"https://api.github.com/repos/{full_name}",
            auth=self.auth,
            headers={"Accept": "application/vnd.github.v3+json"},
            json={"description": description},
        )
        response.raise_for_status()
