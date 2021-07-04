# Python Devops Template Tool

Command-line interface for setting up a Python project based on a dev-ops [template](https://github.com/lrothack/dev-ops).

- [Sample project](https://github.com/lrothack/dev-ops) for this template (including detailed documentation).
- [Cookiecutter](https://github.com/lrothack/cookiecutter-pydevops) for this template.
- Also check out [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) for additional Python package templates.

## Features

This command-line interface supports the creation and the management of a Python dev-ops template that provides:

- testing and deployment in a multi-stage [Docker](https://www.docker.com) environment,
- packaging with [setuptools](https://setuptools.readthedocs.io/en/latest/),
- code analysis with [pylint](https://www.pylint.org/), [bandit](https://bandit.readthedocs.io/en/latest/), [pytest](https://docs.pytest.org/en/stable/) and [coverage](https://coverage.readthedocs.io/en/latest/),
- code quality monitoring with [SonarQube](https://www.sonarqube.org).

The dev-ops pipeline is mostly implemented in a `Makefile` and a `Dockerfile` which are
independent of your Python code. A SonarQube server is started with `docker-compose`.

Creation and management of the template:

- create a new instance of the template (very similar to [Cookiecutter](https://github.com/audreyr/cookiecutter)),
- manage an existing instance/project by adding template components as the project evolves,
- generate a Cookiecutter template (see [lrothack/cookiecutter-pydevops](https://github.com/lrothack/cookiecutter-pydevops)),
- packages the template code in a Python distributions, e.g., binary wheel package,
- configure the template with boolean command-line flags or in interactive mode,
- resolves author information automatically with `git config`.

Optional template components:

- [MongoDB](https://www.mongodb.com)
- [MlFlow](https://www.mlflow.org) (with [PostgreSQL](https://www.postgresql.org) and [MinIO](https://min.io) backends)

These components have been developed in [jkortner/ml-ops](https://github.com/jkortner/ml-ops).

## Installation

Install the latest version from [pypi.org](https://pypi.org/project/devopstemplate/):

```bash
pip install -U devopstemplate
```

From source:

```bash
# Obtain sources
git clone --recurse-submodules https://github.com/lrothack/dev-ops-admin.git

# Install and activate virtual environment
cd dev-ops-admin
python3 -m venv venv
source venv/bin/activate

# Build package
make dist
```

The binary wheel package is located in the `dist` directory and can be installed with `pip`.

## Create and manage projects

After installation, the executable `devopstemplate` is available. It provides the sub-commands:

- create
- manage
- cookiecutter

An overview of the functionalities is shown on the help screens:

```bash
devopstemplate --help
devopstemplate <sub-command> --help
```

The working directory is always the root directory of your project, for example:

```bash
mkdir sampleproject
cd sampleproject
devopstemplate create
```

## Using the dev-ops template

After creating a new project or after switching to the project directory:

- Set up a virtual environment for your project and activate it (requires Python >= 3.6).
- Run `make help` in order to get an overview of the targets provided by `Makefile`.
  Note: Running `make` is only supported from project directory.
- Run `make install-dev` in order to install the package (and all dependencies) in development mode.
- Run `make lint` in order to run code analysis with pylint and bandit.
- Run `make test` in order to run unit tests with pytest and coverage.
- Run `make dist` in order to build a Python package (binary and source).
- Make sure you have [Docker](https://www.docker.com) installed and the Docker daemon is running. Allocate at least 4GB RAM in the Docker resource configuration.
- Run `docker-compose -p sonarqube -f sonarqube/docker-compose.yml up -d` in order to start a SonarQube server. Configure your server through its web interface and obtain an authentication token. The SonarQube URL and the authentication token can be configured through the `Makefile` variables `SONARURL` and `SONARTOKEN`.
- Run `make sonar` in order to run `sonar-scanner` and report results to your SonarQube server.
- Run `make docker-build` in order to analyze, test, package and deploy in a multi-stage Docker build. Analysis results and test results are shown after the build.

Advanced configurations can be made in the *configuration* sections of `Makefile`. See [lrothack/dev-ops](https://github.com/lrothack/dev-ops) for more information.

## Additional components

- `mongodb`
- `mlflow`

Additional components can be installed when creating a new project or with the `manage` command at a later time (replace `<component>` with a component from the list above, also see `devopstemplate manage --help`):

```bash
cd sampleproject
devopstemplate manage --add-<component>
```

Start the corresponding Docker containers with `docker-compose`:

```bash
docker-compose -p <component> -f <component>/docker-compose.yml up -d
```

Also check out the README file in the `<component>` directory and run the sample script.
