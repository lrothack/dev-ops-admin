# Comments: single '#' for ordinary comments, 
#           '## ' indicates text for 'help' target 
#
# Use only one statement per line and do not mix statements and comments on a
# single line in order to allow for automatic editing.

# ATTENTION: Running `make <target>` is only supported from the project directory
#

# --- Common ---
#
# Obtain paths based on MAKEFILE_LIST variable, since variable contents can
# change while reading the Makefile (depending on include etc.) perform 
# immediate evaluation with ':='
# Note that a single '=' is only evaluated when accessing the variable 
#
# Current working directory
CWD := "${CURDIR}"
# Relative path to Makefile (from current working directory)
MKFILE_PATH := $(lastword $(MAKEFILE_LIST))


# --- Python ---
#
# Define names of executables used in make targets (and variables)
PYTHON = python
PIP = pip
META=$(PYTHON) $(SRC)/devopstemplate/template/meta.py
# Files required by `python build` (pip, name/version discovery)
# Note that building is only supported from the project root
# --> BUILDTOOLSFILES must be present in the working directory
# Adjust the list when your configuration changes, e.g., you use additional
# files one of the files is not used anymore.
BUILDTOOLSFILES = pyproject.toml
#
# Directory where sources are located
SRC=src
# Directory where unit tests are located
TESTS=tests
#
# Obtain Python package path, name and version
# Lazy variable evaluation (with a single '=') is used in order to evaluate
# variables only from inside make targets. This allows to check if BUILDTOOLSFILES
# are present *before* executing the shell commands. 
#
# Name of the application defined via pyproject.toml
NAME=$(shell $(META) --quiet --egginfo-path=$(SRC) --name)
# Version of the application defined via pyproject.toml
VERSION=$(shell $(META) --quiet --egginfo-path=$(SRC) --version)
# Directory where metadata for the installed package is found
EGGINFO=$(SRC)/$(NAME).egg-info
# Files that contain package metadata, adding SRC*/__init__.py since top-level __init__.py
# file contains version information (-> for reinstalling package if metadata changes)
METADATAFILES = pyproject.toml $(wildcard $(SRC)/*/__init__.py) $(wildcard $(SRC)/*/__about__.py)


# --- Linting/Testing configuration ---
#
# Executables
PYTEST = pytest
COVERAGE = coverage
PYLINT = pylint
BANDIT = bandit
RUFF = ruff
BLACK = black
ISORT = isort
MYPY = mypy
# Directory where to save linting and testing reports
REPDIR=./.codereports
# Report result files
PYTESTREP=$(REPDIR)/pytest.xml
COVERAGEREP=$(REPDIR)/coverage.xml
PYLINTREP=$(REPDIR)/pylint.txt
BANDITREP=$(REPDIR)/bandit.json


# --- Docker configuration ---
#
# Docker executable
DOCKER = docker
# Name of the executable that is to be run in the Docker entry point script
# (entrypoint.sh). It is expected that there exists an executable
# called $DOCKERENTRYPOINTEXEC in the PATH of the Docker container. 
DOCKERENTRYPOINTEXEC=$(NAME)
# Files required to build a docker image for the Python project
DOCKERFILES = Dockerfile entrypoint.sh


# --- SonarQube client configuration ---
#
# Authentication token variable
SONARTOKEN=
# Authentication token file
# (will be read if file exists and SONARTOKEN variable is not defined)
SONARTOKENFILE=.sonartoken
ifndef SONARTOKEN
ifneq (,$(wildcard $(SONARTOKENFILE)))
SONARTOKEN=$(strip $(shell cat $(SONARTOKENFILE)))
endif
endif
# Report to sonar URL
SONARURL=http://sonarqube:9000
# DISABLE/enable whether to include SCM (git) meta info in sonarqube report
SONARNOSCM=False
# Connect sonar-scanner Docker container to Docker network
DOCKERNET=sonarqube_net
# Docker command for running sonar-scanner container
# make sure to allocate at least 4GB RAM in the Docker resource config
# if SonarQube server and SonarScanner are running simultaneously
SONARSCANNER=$(DOCKER) run \
    --network=$(DOCKERNET) \
    --rm -v $(CWD):/usr/src \
    sonarsource/sonar-scanner-cli:10
#
# Local sonar-scanner installation
#
# Report to sonar URL
# SONARURL=http://localhost:9000
# Path to executable or name of executable if on PATH
# SONARSCANNER=sonar-scanner


# --- Common targets ---

.PHONY: help clean clean-all build install-dev test lint report check sonar docker-build docker-tag

## 
## MAKEFILE for building and testing Python package including
## code analysis and reporting to SonarQube in a dockerized build environment
## 
## ATTENTION: Running `make <target>` is only supported from the project directory
## 
## Targets:
## 

## help:         Print this comment-generated help message
# reads contents of this file and expects that this file is called 'Makefile'
help: $(MKFILE_PATH)
	@sed -n 's/^## //p' $(MKFILE_PATH)

## clean:        Clean up auto-generated files
clean:
	@rm -f $(PYTESTREP) $(COVERAGEREP)
	@rm -f $(PYLINTREP) $(BANDITREP)

## clean-all:    Clean up auto-generated files and directories
##               (WARNING: do not store user data in auto-generated directories)
clean-all: clean
	@rm -rf .coverage .scannerwork
	@rm -rf .pytest_cache
	@rm -rf ./$(REPDIR)
	@rm -rf $(EGGINFO)
	@rm -rf dist/*.whl dist/*.tar.gz


# --- Python targets ---

# Check if project source directory exists in current working directory, otherwise stop.
$(SRC):
	$(error "Python source directory missing in working directory ($@)")
# Check if test files exist in current working directory, otherwise stop.
$(TESTS):
	$(error "Python test files missing in working directory ($@)")
# Check if files for building exist in current working directory, otherwise stop.
$(BUILDTOOLSFILES):
	$(error "Python packaging files missing in working directory ($@)")

## build:        Build a Python wheel with `python build` (based on pyproject.toml)
build: $(BUILDTOOLSFILES)
	$(PIP) install build
	$(PYTHON) -m build

## install-dev:  Install development dependencies (based on pyproject.toml)
##               (installation within a Python virtual environment is
##                recommended)
##               (application sources will be symlinked to PYTHONPATH)
# along with PHONY target `install-dev` the rule generates the $(EGGINFO) directory
# this distribution specification should be rebuilt whenever any package metadata changes
# -> an updated $(EGGINFO) is required for successful package name/version discovery
install-dev $(EGGINFO): $(BUILDTOOLSFILES) $(METADATAFILES)
	$(PIP) install -e ".[dev]"

## test:         Run Python unit tests with pytest and coverage analysis
test: $(SRC) $(TESTS)
	@echo "\n\nUnit Tests with Coverage\n------------------------\n"
	$(PYTEST) --cov=$(SRC) $(TESTS)

## lint:         Run Python linter (bandit, pylint) and print output to terminal
lint: $(SRC)
	@echo "\n\nBandit Vulnerabilities\n----------------------\n"
	-$(BANDIT) -r --exclude "**/template/*,**/venv/*" $(SRC)
	@echo "\n\nPylint Code Analysis\n--------------------\n"
	$(PYLINT) --ignore template,venv --output-format=colorized --reports=n --exit-zero $(SRC)

## report:       Combines test and lint targets in order to create a report
report: lint test

## check:        Checks test coverage, black/isort formatting, ruff linting
##               and mypy type hints
check: $(SRC) $(TESTS)
	$(PYTEST) --cov=$(SRC) --cov-fail-under=80 $(TESTS)
	$(BLACK) --extend-exclude template --check $(SRC)
	$(RUFF) check --extend-exclude "**/template/*" $(SRC)
	# $(MYPY) --strict --exclude "/template/" $(SRC)
	$(ISORT) --check $(SRC)



# --- SonarQube targets ---

## sonar:        Report code analysis and test coverage results to SonarQube
##               (requires SonarQube server, to run server in Docker:
##                `docker compose -p sonarqube \
##                                -f sonarqube/docker-compose.yml up -d`)
#                (requires code analysis dependencies, 
#                 intall with `make install-dev`
#                 ATTENTION: make sure to allocate at least 4GB RAM in the 
#                 Docker resource configuration when running sonar server 
#                 and sonar scanner containers simulataneously)
# leading dash (in front of commands, not parameters) ignores error codes,
# `make` would fail if test case fails or linter reports infos/warnings/errors.
# check EGGINFO that is required for package NAME discovery
sonar: $(EGGINFO) $(SRC) $(TESTS)
	@mkdir -p $(REPDIR)
	-$(BANDIT) -r $(SRC) --format json >$(BANDITREP)
	$(PYLINT) $(SRC) --exit-zero --reports=n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > $(PYLINTREP)
	-$(COVERAGE) run --source $(SRC) -m $(PYTEST) --junit-xml=$(PYTESTREP) -o junit_family=xunit2 $(TESTS)
	$(COVERAGE) xml -o $(COVERAGEREP)
	$(SONARSCANNER) -Dsonar.host.url=$(SONARURL) \
              -Dsonar.token=$(SONARTOKEN) \
              -Dsonar.projectKey=$(NAME) \
              -Dsonar.projectVersion=$(VERSION) \
              -Dsonar.sourceEncoding=UTF-8 \
              -Dsonar.sources=$(SRC) \
              -Dsonar.tests=$(TESTS) \
              -Dsonar.scm.disabled=$(SONARNOSCM) \
              -Dsonar.python.xunit.reportPath=$(PYTESTREP) \
              -Dsonar.python.coverage.reportPaths=$(COVERAGEREP) \
              -Dsonar.python.pylint.reportPaths=$(PYLINTREP) \
              -Dsonar.python.bandit.reportPaths=$(BANDITREP)


# --- Docker targets ---

## docker-build: Build docker image for Python application with code analysis
# Note: info is parsed and immediately printed by make, echo is executed in a
# shell as are the other commands in the recipe.
# check EGGINFO that is required for package NAME discovery
docker-build: $(EGGINFO) $(DOCKERFILES)
	$(info Running Docker build in context: ./ )
	$(info ENTRYPOINT executable: $(DOCKERENTRYPOINTEXEC))
	$(eval REPORTFILE:=code-analyses.txt)
	$(DOCKER) build --rm -t $(NAME) ./ \
		--build-arg REPORTFILE=$(REPORTFILE) \
		--build-arg ENTRYPOINT=$(DOCKERENTRYPOINTEXEC)
	@echo "\n### CODE ANALYSIS REPORT ###\n"
	$(DOCKER) run -it --entrypoint="more" --rm $(NAME) $(REPORTFILE)
	@echo "\n\nbuild finished, run the container with \`docker run --rm $(NAME)\`"

## docker-tag:   Tag the 'latest' image created with `make docker-build` with
##               the current version that is defined via pyproject.toml
# check EGGINFO that is required for package NAME and VERSION discovery
docker-tag: $(EGGINFO)
	$(DOCKER) tag $(NAME) $(NAME):$(VERSION)