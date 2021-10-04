import subprocess


def clone(ssh_url: str, clone_dir: str):
    subprocess.run(["git", "clone", ssh_url, clone_dir], check=True)
