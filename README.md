# instarepo

[![Python CI](https://github.com/ngeor/instarepo/actions/workflows/build.yml/badge.svg)](https://github.com/ngeor/instarepo/actions/workflows/build.yml)

CLI automation tool to batch process multiple repositories.

## Requirements

Requirements:

- python 3.8+
- pipenv

Install dependencies with `pipenv install --dev`

## Usage

Inside a pipenv shell, run: `python -m instarepo.main`

```
$ python -m instarepo.main --help
usage: main.py [-h] [--verbose] {list,fix,analyze} ...

Apply changes on multiple repositories

positional arguments:
  {list,fix,analyze}  Sub-commands help
    list              Lists the available repositories
    fix               Runs automatic fixes on the repositories
    analyze           Analyzes the available repositories, counting historical LOC

optional arguments:
  -h, --help          show this help message and exit
  --verbose           Verbose output
```

## List

Lists the repositories.

By default, skips forks and archived repositories.

```
usage: main.py list [-h] -u USER -t TOKEN
                    [--sort {full_name,created,updated,pushed}]
                    [--direction {asc,desc}]
                    [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE]
                    [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                    [--forks {allow,deny,only}] [--pushed-after PUSHED_AFTER]
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
  -u USER, --user USER  The GitHub username
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
    pipenv run python -m instarepo.main list -u USER -t TOKEN
```

## Fix

Applies automatic fixes on repositories.

instarepo will:

- clone all your GitHub repositories in a temporary local folder
- process all non-archived repositories and apply automatic fixes
- create a merge request for every repository that had changes

By default skips forks. It's not possible to select archived repositories, as they are read-only.

```
usage: main.py fix [-h] -u USER -t TOKEN
                   [--sort {full_name,created,updated,pushed}]
                   [--direction {asc,desc}]
                   [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE]
                   [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                   [--forks {allow,deny,only}] [--pushed-after PUSHED_AFTER]
                   [--pushed-before PUSHED_BEFORE] [--dry-run]
                   [--only-fixers ONLY_FIXERS [ONLY_FIXERS ...] |
                   --except-fixers EXCEPT_FIXERS [EXCEPT_FIXERS ...]]

Runs automatic fixes on the repositories

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
  --dry-run             Do not actually push and create MR
  --only-fixers ONLY_FIXERS [ONLY_FIXERS ...]
                        Only run fixers that have the given prefixes
  --except-fixers EXCEPT_FIXERS [EXCEPT_FIXERS ...]
                        Do not run fixers that have the given prefixes

Authentication:
  -u USER, --user USER  The GitHub username
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
    pipenv run python -m instarepo.main fix -u USER -t TOKEN

Fixers:

changelog.must_have_cliff_toml
    Ensures the configuration for git-cliff (cliff.toml) exists
changelog.generate_changelog
    Generates changelog with git-cliff
ci.no_travis
    Removes the .travis.yml file
ci.no_travis_badge
    Removes the Travis badge from README files
dotnet.dot_net_framework_version
    Sets the .NET Framework version to 4.7.2 in csproj and web.config files
dotnet.must_have_c_sharp_app_veyor
    If missing, creates an appveyor.yml file for CSharp projects
license.copyright_year
    Ensures the year in the license file copyright is up to date
license.must_have_license
    Ensures that a license file exists
maven.maven
    Updates the dependencies of a Maven project
maven.must_have_maven_git_hub_workflow
    If missing, adds a GitHub action Maven build workflow
maven.maven_badges
    Fixes badges for Maven libraries
maven.url
    Ensures Maven projects have the correct URL and SCM sections
missing_files.must_have_readme
    Ensures that the repo has a readme file
missing_files.must_have_editor_config
    Ensures an editorconfig file exists
missing_files.must_have_git_hub_funding

    Ensures a GitHub funding file exists (.github/FUNDING.yml).
    The rule will use the FUNDING.yml file from `user-templates/.github/FUNDING.yml`,
    if one exists.

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
```

## Analyze

Analyzes repositories.

By default, skips forks and archived repositories.

```
usage: main.py analyze [-h] -u USER -t TOKEN
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
  -u USER, --user USER  The GitHub username
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
    pipenv run python -m instarepo.main analyze -u USER -t TOKEN --since 2021-11-06
```
