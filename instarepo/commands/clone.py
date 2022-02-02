import logging
import os.path

import instarepo.git
import instarepo.github
import instarepo.repo_source


class CloneCommand:
    def __init__(self, args):
        self.repo_source = (
            instarepo.repo_source.RepoSourceBuilder().with_args(args).build()
        )
        self.verbose: bool = args.verbose
        self.projects_dir: str = args.projects_dir

    def run(self):
        if not os.path.isdir(self.projects_dir):
            raise ValueError(f"Projects dir {self.projects_dir} does not exist")
        repos = self.repo_source.get()
        for repo in repos:
            project_dir = os.path.join(self.projects_dir, repo.name)
            if os.path.isdir(project_dir):
                logging.info("Skipping %s because it already exists", repo.name)
            else:
                logging.info("Cloning %s", repo.name)
                instarepo.git.clone(repo.ssh_url, project_dir, quiet=not self.verbose)
