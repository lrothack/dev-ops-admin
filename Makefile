# Comments: single '#' for ordinary comments, 
#           '## ' indicates text for 'help' target 
#
# Use only one statement per line and do not mix statements and comments on a
# single line in order to allow for automatic editing.


# --- Common ---
#
# Obtain paths based on MAKEFILE_LIST variable, since variable contents can
# change while reading the Makefile (depending on include etc.) perform 
# immediate evaluation with ':='
# Note that a single '=' is only evaluated when accessing the variable 
#
# Current working directory 
CWD := ${CURDIR}
# Relative path to Makefile (from current working directory)
MKFILE_PATH := $(lastword $(MAKEFILE_LIST))
# Absolute path to Makefile's parent directory (project root)
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))


# --- Python ---
#
# Define names of executables used in make targets (and variables)
PYTHON = python
PIP = pip
# Files required by setuptools (python setup.py, pip)
# Note that setuptools can only supports running from the project root
# --> SETUPTOOLSFILES must be present in the working directory
# Adjust the list when your configuration changes, e.g., one of the files is
# not used anymore.
SETUPTOOLSFILES = setup.py requirements.txt
#
# Obtain Python package path, name and version
# Lazy variable evualtion (with a single '=') is used in order to evaluate
# variables only from inside make targets. This allows to check if SETUPTOOLSFILES
# are present *before* executing the shell commands. 
#
# Name of the application defined in setup.py
NAME=$(shell $(PYTHON) setup.py --name)
# Version of the application defined in setup.py
VERSION=$(shell $(PYTHON) setup.py --version)
# Name of the directory where application sources are located
PACKAGE=$(ROOT)/$(NAME)
# Directory where unittests are located
TESTS=$(ROOT)/tests


# --- SonarQube configuration ---
#
# SonarQube client, test and code analysis tools
# Note that the test / code analysis tools are not specific to SonarQube but
# are only required for SonarQube reporting in the Makefile
SONARSCANNER = sonar-scanner
PYLINT = pylint
NOSETESTS = nosetests
BANDIT = bandit
# Directory where to save linting and testing reports
REPDIR=$(CWD)/.codereports
# Report result files
NOSETESTSREP=$(REPDIR)/nosetests.xml
COVERAGEREP=$(REPDIR)/coverage.xml
PYLINTREP=$(REPDIR)/pylint_report.txt
BANDITREP=$(REPDIR)/bandit_report.json
#
# Configuration variables for local sonarqube reporting with `make sonar`
# Report to sonar host (when running locally)
SONARHOST=localhost
# Report to sonar port (when running locally)
SONARPORT=9000
# DISABLE/enable whether to include SCM (git) meta info in sonarqube report
SONARNOSCM=False


# --- Docker configuration ---
# Note that the Docker configuration is mostly needed for SonarQube reporting
# from Docker besides the definition of the SonarQube executable 
#
# Docker executable
DOCKER = docker
#
# Configuration variables for sonarqube reporting within Docker build when
# running `make build_docker`, i.e., variables will be passed to Docker build
# as build arguments
# Enable/disable SonarQube reporting during Docker build
DOCKERSONAR=True
# Report to sonar host (when running in Docker build)
DOCKERSONARHOST=sonarqube
# Report to sonar port (when running in Docker build)
DOCKERSONARPORT=9000
# Docker network for running the Docker build. Sonarqube server must be hosted
# in the same network at $DOCKERSONARHOST:$DOCKERSONARPORT
# Only evaluated if $DOCKERSONAR==True
DOCKERNET=sonarqube_net


# --- Common targets ---

.PHONY: help clean clean-all bdist_wheel install_dev test sonar build_docker

## 
## MAKEFILE for building and testing Python package including
## code analysis and reporting to SonarQube in a dockerized build environment
## 
## Targets:
## 

## help:         Print this comment-generated help message
# reads contents of this file and expects that this file is called 'Makefile'
help:
	@sed -n 's/^## //p' $(MKFILE_PATH)

## clean:        Clean up auto-generated files
clean:
	@rm -f $(NOSETESTSREP) $(COVERAGEREP)
	@rm -f $(PYLINTREP) $(BANDITREP)

## clean-all:    Clean up auto-generated files and directories
##               (WARNING: do not store user data in auto-generated directories)
clean-all: clean
	@rm -rf $(NAME).egg-info
	@rm -rf build
	@rm -rf dist


# --- Python targets ---

# Check if setuptools files exist in current working directory, otherwise stop.
$(SETUPTOOLSFILES):
	$(error "Python packaging files missing in working directory ($(SETUPTOOLSFILES))")

## bdist_wheel:  Build a Python wheel with setuptools (based on setup.py)
bdist_wheel: $(SETUPTOOLSFILES)
	$(PYTHON) setup.py bdist_wheel

## install_dev:  Install development dependencies (based on setup.py)
##               (installation within a Python virtual environment is
##                recommended)
##               (application sources will be symlinked to PYTHONPATH)
install_dev: $(SETUPTOOLSFILES)
	$(PIP) install -r requirements.txt

## test:         Run Python unit tests with nosetests
test:
	$(NOSETESTS) --where $(TESTS)


# --- SonarQube targets ---

## sonar:        Report code analysis and test coverage results to SonarQube
##               (requires SonarQube server, run:
##                `docker-compose -p sonarqube \
##                                -f sonarqube/docker-compose.yml up -d`)
#                (requires code analysis dependencies, 
#                 intall with `make install_dev`)
#                (requires SonarQube client sonar-scanner, 
#                 install with `brew sonar-scanner` or see ./Dockerfile)
sonar: $(NOSETESTSREP) $(COVERAGEREP) $(PYLINTREP) $(BANDITREP) $(SETUPTOOLSFILES)
	$(SONARSCANNER) -Dsonar.host.url=http://$(SONARHOST):$(SONARPORT) \
              -Dsonar.projectKey=$(NAME) \
              -Dsonar.projectVersion=$(VERSION) \
              -Dsonar.sourceEncoding=UTF-8 \
              -Dsonar.sources=$(PACKAGE) \
              -Dsonar.tests=$(TESTS) \
              -Dsonar.scm.disabled=$(SONARNOSCM) \
              -Dsonar.python.xunit.reportPath=$(NOSETESTSREP) \
              -Dsonar.python.coverage.reportPaths=$(COVERAGEREP) \
              -Dsonar.python.pylint.reportPath=$(PYLINTREP) \
              -Dsonar.python.bandit.reportPaths=$(BANDITREP)


# analysis tools can be installed with `make install_dev`
# leading - ignores error codes, make would fail if test case fails
$(NOSETESTSREP):
	@mkdir -p $(REPDIR)
	-$(NOSETESTS) --with-xunit --xunit-file=$@ --where $(TESTS)

# analysis tools can be installed with `make install_dev`
# leading - ignores error codes, make would fail if test case fails
$(COVERAGEREP):
	@mkdir -p $(REPDIR)
	-$(NOSETESTS) --with-coverage --cover-xml --cover-xml-file=$@ --where $(TESTS)
	
# analysis tools can be installed with `make install_dev`
# --exit-zero always return exit code 0: make would fail otherwise
$(PYLINTREP): $(SETUPTOOLSFILES)
	@mkdir -p $(REPDIR)
	$(PYLINT) $(PACKAGE) --exit-zero --reports=n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > $@

# analysis tools can be installed with `make install_dev`
# leading - ignores error codes, make would fail if test case fails
$(BANDITREP): $(SETUPTOOLSFILES)
	@mkdir -p $(REPDIR)
	-$(BANDIT) -r $(PACKAGE) --format json >$@


# --- Docker targets ---

## build_docker: Build docker image for Python application including
##               code analysis and reporting to SonarQube (multi-stage build)
##               (requires SonarQube server, see target 'sonar' above)
##               (SonarQube reporting during Docker build can be disabled
##                with `make build_docker DOCKERSONAR=False`)
#                (WARNING: do not run in Docker, Docker-in-Docker!)
# The if-statement is required in order to determine if we have to run the
# build in the $(DOCKERNET) network
# Note: info is parsed and immediately printed by make, echo is executed in a
# shell as are the other commands in the recipe.
build_docker: $(SETUPTOOLSFILES)
	$(info WARNING: Do not run this target within a Docker build/container)
	$(info Running Docker build in context $(ROOT))
ifeq ($(DOCKERSONAR), True)
	$(info building Docker image within Docker network $(DOCKERNET))
	$(info (make sure SonarQube is running in the same network))
	$(info (run `docker-compose -p sonarqube -f sonarqube/docker-compose.yml up -d`))
	$(DOCKER) build --rm --network=$(DOCKERNET) -t $(NAME) $(ROOT) \
		--build-arg SONARHOST=$(DOCKERSONARHOST) \
		--build-arg SONARPORT=$(DOCKERSONARPORT)
else
	$(info building Docker image without reporting to SonarQube)
	$(DOCKER) build --rm -t $(NAME) $(ROOT) --build-arg SONAR=False
endif
	@echo "build finished, run the container with \`docker run --rm $(NAME)\`"