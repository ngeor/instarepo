# instarepo

CLI automation tool to create repositories and activate their build pipeline

Requirements:

- python 3.9
- pipenv

Install dependencies with `pipenv install --dev`

## THE FOLLOWING GUIDE IS DEPRECATED

## Usage

This is the general way of running instarepo:

    ruby lib/main.rb [global options] command [command options]

To see the available commands:

    ruby lib/main.rb --help

To see help for a command:

    ruby lib/main.rb command --help

### Global Options

These options apply to all commands:

- `--dry-run`: Does not perform any changes, but instead shows what would change.

## Commands

### Create repository

Creates a new git repository with GitHub or Bitbucket Cloud.

    ruby lib/main.rb create [command options]

The following options are available:

- `--provider` chooses the git repository provider. Supported values are
  `bitbucket` and `github`.
- `--username` and `--password` provide the credentials to access the REST API
  of Bitbucket Cloud or GitHub.
- `--owner` is the owner of the repository. Might be the same as `username` for
  a user who doesn't belong to an organization.
- `--name` is the name of the repository. Together with the `owner` they form
  the slug of the repository, i.e. `owner/name`.
- `--description` provides a short description for the repository.
- `--language` sets the programming language of the repository.
  Currently the only valid value is `java`.

#### Example: Create new repository on GitHub

To create a new repository on GitHub:

    ruby lib/main.rb create --provider github \
      --username secret \
      --password secret \
      --owner ngeor \
      --name instarepo \
      --language java \
      --description "A cool new project"

The repository will be _public_ and it will be automatically initialized by
GitHub with a README file, a `.gitignore` file (currently only for Maven)
and a `LICENSE` file (currently only MIT license).

#### Example: Create new repository on Bitbucket Cloud

To create a new repository on Bitbucket Cloud:

    ruby lib/main.rb create --provider bitbucket \
      --username secret \
      --password secret \
      --owner ngeor \
      --name instarepo \
      --language java \
      --description "A cool new project"

The repository will be _private_ and it will be empty. It will have a no fork
policy.

### Delete repository

Deletes a repository from GitHub or Bitbucket Cloud.

    ruby lib/main.rb delete --provider bitbucket|github \
      --username username \
      --password password \
      --owner owner \
      --name name

The the Create repository command for the description of the parameters.

### Initialize a repository

Initializes a repository with a README file and performs the first commit. This
is more useful for Bitbucket, where the create repository command creates an
empty repository with no commits at all.

    ruby lib/main.rb init --provider bitbucket|github \
      --username username \
      --password password \
      --owner owner \
      --name name \
      --language language \
      --description description \
      --clone-dir clone-dir \
      --travis-badge

In addition to the parameters defined by the create command, init expects:

- `--clone-dir` the local directory in which the repository should
  be cloned. If you specify `C:\Projects` and the name of the
  repository is `my-project`, then the repository will end up
  being cloned in `C:\Projects\my-project`.
- `--travis-badge` is an optional flag. If specified, a Travis badge will be
  added to the README file.

### Activate Travis builds

Activates the repository in Travis. Only tested with GitHub repositories.

    ruby lib/main.rb activate-travis \
      --name name \
      --owner owner \
      --token token

- `name`: The name of the repository
- `owner`: The owner of the repository. Together with `name`, they form the
  repository slug e.g. `ngeor/instarepo`.
- `token`: The Travis authentication token (see next section on Authentication).

### Deactivate Travis builds

Deactivates the repository in Travis. Only tested with GitHub repositories.
This command will prevent build from being triggered in Travis.

    ruby lib/main.rb deactivate-travis \
      --name name \
      --owner owner \
      --token token

The parameters are the same as with the Activate Travis builds command.

### Activate Bitbucket Pipelines

Activates builds in Bitbucket Pipelines. Relevant only for Bitbucket Cloud
repositories.

    ruby lib/main.rb activate-bitbucket-pipelines \
      --name name \
      --owner owner \
      --username username \
      --password password

- `name`: The name of the repository
- `owner`: The owner of the repository. Together with `name`, they form the
  repository slug e.g. `ngeor/instarepo`.
- `username`: The Bitbucket username.
- `password`: The Bitbucket password.

### Deactivate Bitbucket Pipelines

Deactivates builds in Bitbucket Pipelines. Relevant only for Bitbucket Cloud
repositories.

    ruby lib/main.rb deactivate-bitbucket-pipelines \
      --name name \
      --owner owner \
      --username username \
      --password password

The parameters are the same with the Activate Bitbucket Pipelines command.

### Down

This is a composite command that deactivates builds and deletes repository.

#### Example: Deactivate Travis and delete GitHub Repository

    ruby lib/main.rb down \
      --name name \
      --owner owner \
      --username username \
      --password password \
      --provider github \
      --token travis-token

#### Example: Delete Bitbucket Pipelines and Repository

    ruby lib/main.rb down \
      --name name \
      --owner owner \
      --username username \
      --password password \
      --provider bitbucket

## Authentication

### Travis

To obtain the token for Travis, you need the Travis CLI.
You need to run `travis login` and `travis token`. You can read more in
[Travis documentation](https://developer.travis-ci.com/authentication).

### Two factor authentication

If you have enabled two factor authentication for GitHub or Bitbucket Cloud,
the `password` parameter needs to be your personal access token and not your
account password.
