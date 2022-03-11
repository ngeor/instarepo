# instarepo

[![Python CI](https://github.com/ngeor/instarepo/actions/workflows/build.yml/badge.svg)](https://github.com/ngeor/instarepo/actions/workflows/build.yml)
![PyPI](https://img.shields.io/pypi/v/instarepo)

CLI automation tool to batch process multiple repositories.

## Requirements

Requirements:

- Python 3.8+
- pip
- pipenv (for development)

## Installation

### Simple

Install from PyPI with `pip3 install --user instarepo`.

### Development mode

- Install dependencies with `pipenv install --dev`
- Inside a pipenv shell, run: `python -m instarepo.main`.

### Manual installation

- Install dependencies with `pipenv install --dev`
- Build the wheel with `pipenv run python -m build`
- Install the wheel with `pip install [--force-reinstall] --user dist/path-to-wheel.whl`

You'll be able to invoke `instarepo` by just `instarepo`.

Uninstall with `pip uninstall instarepo`.

## Usage

```
usage: instarepo [-h] [--verbose] [--version]
                 {list,fix,analyze,clone,login,logout} ...

Apply changes on multiple repositories

positional arguments:
  {list,fix,analyze,clone,login,logout}
                        Sub-commands help
    list                Lists the available repositories
    fix                 Runs automatic fixes on the repositories
    analyze             Analyzes the available repositories, counting
                        historical LOC
    clone               Clones all the available repositories
    login               Provide GitHub credentials for subsequent commands
    logout              Delete previously stored GitHub credentials

optional arguments:
  -h, --help            show this help message and exit
  --verbose             Verbose output
  --version             show program's version number and exit
```

### Login

Provide GitHub credentials for subsequent commands. Credentials are stored
in the Windows registry under `HKEY_CURRENT_USER\SOFTWARE\ngeor\instarepo`.
On Linux/Mac, the credentials are stored in `~/.instarepo.ini`.

```
usage: instarepo login [-h] -u USERNAME -t TOKEN

optional arguments:
  -h, --help            show this help message and exit

Authentication:
  -u USERNAME, --username USERNAME
                        The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token
```

### Logout

Delete previously stored GitHub credentials.

```
usage: instarepo logout [-h]

optional arguments:
  -h, --help  show this help message and exit
```

### List

Lists the repositories.

By default, skips forks and archived repositories.

```
usage: instarepo list [-h] [-u USERNAME] [-t TOKEN]
                      [--sort {full_name,created,updated,pushed}]
                      [--direction {asc,desc}]
                      [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE]
                      [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                      [--forks {allow,deny,only}]
                      [--pushed-after PUSHED_AFTER]
                      [--pushed-before PUSHED_BEFORE]
                      [--archived {allow,deny,only}]

optional arguments:
  -h, --help            show this help message and exit
  --only-language ONLY_LANGUAGE
                        Only process repositories of the given programming
                        language
  --except-language EXCEPT_LANGUAGE
                        Do not process repositories of the given programming
                        language
  --only-name-prefix ONLY_NAME_PREFIX
                        Only process repositories whose name starts with the
                        given prefix
  --except-name-prefix EXCEPT_NAME_PREFIX
                        Do not process repositories whose name starts with the
                        given prefix
  --archived {allow,deny,only}
                        Filter archived repositories

Authentication:
  -u USERNAME, --username USERNAME
                        The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token

Sorting:
  --sort {full_name,created,updated,pushed}
  --direction {asc,desc}

Filtering:
  --forks {allow,deny,only}
                        Filter forks
  --pushed-after PUSHED_AFTER
                        Only process repositories that had changes pushed
                        after the given time interval e.g. 4h
  --pushed-before PUSHED_BEFORE
                        Only process repositories that had changes pushed
                        before the given time interval e.g. 4h

Example:
    instarepo list -u USER -t TOKEN
```

### Fix

Applies automatic fixes on repositories.

instarepo will:

- clone all your GitHub repositories in a temporary local folder
- process all non-archived repositories and apply automatic fixes
- create a merge request for every repository that had changes

By default skips forks. It's not possible to select archived repositories, as they are read-only.

```
usage: instarepo fix [-h] [-u USERNAME] [-t TOKEN] [--sort {full_name,created,updated,pushed}] [--direction {asc,desc}]
                     [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE] [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                     [--forks {allow,deny,only}] [--pushed-after PUSHED_AFTER] [--pushed-before PUSHED_BEFORE] [--dry-run] [--only-fixers ONLY_FIXERS [ONLY_FIXERS ...] |
                     --except-fixers EXCEPT_FIXERS [EXCEPT_FIXERS ...]] [--local-dir LOCAL_DIR] [--auto-merge] [-c CONFIG_FILE]

Runs automatic fixes on the repositories

optional arguments:
  -h, --help            show this help message and exit
  --only-language ONLY_LANGUAGE
                        Only process repositories of the given programming language
  --except-language EXCEPT_LANGUAGE
                        Do not process repositories of the given programming language
  --only-name-prefix ONLY_NAME_PREFIX
                        Only process repositories whose name starts with the given prefix
  --except-name-prefix EXCEPT_NAME_PREFIX
                        Do not process repositories whose name starts with the given prefix
  --dry-run             Do not actually push and create MR
  --only-fixers ONLY_FIXERS [ONLY_FIXERS ...]
                        Only run fixers that have the given prefixes
  --except-fixers EXCEPT_FIXERS [EXCEPT_FIXERS ...]
                        Do not run fixers that have the given prefixes
  --local-dir LOCAL_DIR
                        Apply fixes for a project at a local working directory. Skips all GitHub related calls and git push.
  --auto-merge          Automatically merge open MRs that pass CI.
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        The location of an optional configuration file

Authentication:
  -u USERNAME, --username USERNAME
                        The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token

Sorting:
  --sort {full_name,created,updated,pushed}
  --direction {asc,desc}

Filtering:
  --forks {allow,deny,only}
                        Filter forks
  --pushed-after PUSHED_AFTER
                        Only process repositories that had changes pushed after the given time interval e.g. 4h
  --pushed-before PUSHED_BEFORE
                        Only process repositories that had changes pushed before the given time interval e.g. 4h

Example:
    instarepo fix -u USER -t TOKEN

Fixers:

changelog.must_have_cliff_toml
    Ensures the configuration for git-cliff (cliff.toml) exists
ci.no_travis
    Removes the .travis.yml file
ci.no_travis_badge
    Removes the Travis badge from README files
ci.python_build
    Adds a build GitHub action for Python projects
ci.python_release
    Adds a release GitHub action for Python projects
dotnet.must_have_ci

    Creates a GitHub Action workflow for CSharp projects, deletes appveyor.yml if present.

license.copyright_year

    Ensures the year in the license file copyright is up to date.

    Does not run for forks, private repos, and local git repos.

license.must_have_license

    Ensures that a license file exists.

    Does not run for forks, private repos, and local git repos.

maven.must_have_ci
    If missing, adds a GitHub action Maven build workflow
maven.maven_badges

    Fixes badges for Maven libraries.

    Does not work for local git repositories.

maven.url

    Ensures Maven projects have the correct URL and SCM sections.

    Does not work for local git repositories.

missing_files.must_have_readme

    Ensures that the repo has a readme file.

    Does not run for locally checked out repositories.

missing_files.must_have_editor_config
    Ensures an editorconfig file exists
missing_files.must_have_git_hub_funding

    Ensures a GitHub funding file exists (.github/FUNDING.yml).
    The template file needs to be configured in the configuration file.

    Does not run for locally checked out repositories.

missing_files.must_have_git_ignore
    Ensures a .gitignore file exists
pascal.auto_format
    Automatically formats Pascal files with JEDI code format
readme.readme_image

    Finds broken images in the `README.md` file.
    Able to correct images that were moved one or more
    folders up but the user forgot to update them in the `README.md` file.

repo_description.repo_description

    Updates GitHub's repo description based on the README file.

    Note: this fixer does not create an MR, it calls the
    GitHub REST API directly (https://docs.github.com/en/rest/reference/repos#update-a-repository).

    Does not run for local git repositories.
```

### Analyze

Analyzes repositories.

By default, skips forks and archived repositories.

```
usage: instarepo analyze [-h] [-u USERNAME] [-t TOKEN]
                         [--sort {full_name,created,updated,pushed}]
                         [--direction {asc,desc}]
                         [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE]
                         [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                         [--forks {allow,deny,only}]
                         [--pushed-after PUSHED_AFTER]
                         [--pushed-before PUSHED_BEFORE]
                         [--archived {allow,deny,only}] --since SINCE
                         [--metric {commits,files}]

optional arguments:
  -h, --help            show this help message and exit
  --only-language ONLY_LANGUAGE
                        Only process repositories of the given programming
                        language
  --except-language EXCEPT_LANGUAGE
                        Do not process repositories of the given programming
                        language
  --only-name-prefix ONLY_NAME_PREFIX
                        Only process repositories whose name starts with the
                        given prefix
  --except-name-prefix EXCEPT_NAME_PREFIX
                        Do not process repositories whose name starts with the
                        given prefix
  --archived {allow,deny,only}
                        Filter archived repositories
  --since SINCE         The start date of the analysis (YYYY-mm-dd)
  --metric {commits,files}
                        The metric to report on

Authentication:
  -u USERNAME, --username USERNAME
                        The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token

Sorting:
  --sort {full_name,created,updated,pushed}
  --direction {asc,desc}

Filtering:
  --forks {allow,deny,only}
                        Filter forks
  --pushed-after PUSHED_AFTER
                        Only process repositories that had changes pushed
                        after the given time interval e.g. 4h
  --pushed-before PUSHED_BEFORE
                        Only process repositories that had changes pushed
                        before the given time interval e.g. 4h

Example:
    instarepo analyze -u USER -t TOKEN --since 2021-11-06
```

### Clone

Clones repositories from GitHub locally. Skips repositories that are already present.

By default, skips forks and archived repositories.

```
usage: instarepo clone [-h] [-u USERNAME] [-t TOKEN]
                       [--archived {allow,deny,only}]
                       [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE]
                       [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                       [--forks {allow,deny,only}]
                       [--pushed-after PUSHED_AFTER]
                       [--pushed-before PUSHED_BEFORE] --projects-dir
                       PROJECTS_DIR

optional arguments:
  -h, --help            show this help message and exit
  --archived {allow,deny,only}
                        Filter archived repositories
  --only-language ONLY_LANGUAGE
                        Only process repositories of the given programming
                        language
  --except-language EXCEPT_LANGUAGE
                        Do not process repositories of the given programming
                        language
  --only-name-prefix ONLY_NAME_PREFIX
                        Only process repositories whose name starts with the
                        given prefix
  --except-name-prefix EXCEPT_NAME_PREFIX
                        Do not process repositories whose name starts with the
                        given prefix
  --projects-dir PROJECTS_DIR
                        The directory where projects are going to be cloned
                        into

Authentication:
  -u USERNAME, --username USERNAME
                        The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token

Filtering:
  --forks {allow,deny,only}
                        Filter forks
  --pushed-after PUSHED_AFTER
                        Only process repositories that had changes pushed
                        after the given time interval e.g. 4h
  --pushed-before PUSHED_BEFORE
                        Only process repositories that had changes pushed
                        before the given time interval e.g. 4h
```

## Development

- Files are formatted with `black`
- Unit tests with `pytest`
- Lint with `pylint --disable=R,C0116,C0114,C0115,C0301 instarepo`

### Creating a new release

- Make sure you're on the latest of the default branch and there are no pending changes
- Update the version in `instarepo/__init__.py`
- Update the changelog with `git-cliff -t x.y.z -o CHANGELOG.md`
- Commit with a message like "chore(release): prepare for version x.y.z"
- Create a tag `vx.y.z`
- Push with `git push --follow-tags`
- Clean to make sure there are no build files with `git clean -fdx`
- Build the wheel `python3 -m build` (inside pipenv)
- Upload the wheel with `twine upload dist/*`
- Update again the versions in `instarepo/__init__.py` to set the
  next development versions.
- Commit with a message like "chore(release): prepare for next development iteration"
