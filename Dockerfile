FROM python:3.8-slim-buster as build
# The python base image contains python, pip, etc. in a slim Debian buster 

# Variables defined with ARG can be modified when building the Docker image
# --> see docker build --build-arg

# Sonar-Scanner (SonarQube client) configuration
# Enable/disable sonar reporting
ARG SONAR=True
ARG SONARHOST=sonarqube
ARG SONARPORT=9000
# Installation directory for sonar-scanner
ARG SONAR_SCANNER_HOME=/opt/sonar-scanner
# sonar-scanner version, allows to control which version will be installed
ARG SONAR_SCANNER_VERSION=4.3.0.2102
# Define environment variables based on arguments
# Add sonar-scanner executable to PATH for sonar reporting
ENV PATH=${SONAR_SCANNER_HOME}/bin:${PATH}

# pip environment variables: no version check, no caching
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Install debian packages required for sonar-scanner installation
RUN apt-get update \
    && apt-get install -y --no-install-recommends make ca-certificates wget unzip \
    && rm -rf /var/lib/apt/lists/*

# Install sonar-scanner, based on sonar-scanner-cli Dockerfile --> see docker hub
WORKDIR /opt
RUN if [ ${SONAR} = "True" ] ; then \
    wget -U "scannercli" -q -O /opt/sonar-scanner-cli.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip \
    && unzip sonar-scanner-cli.zip \
    && rm sonar-scanner-cli.zip \
    && mv sonar-scanner-${SONAR_SCANNER_VERSION}-linux ${SONAR_SCANNER_HOME} ;fi

# Copy Python app into image 
WORKDIR /app
COPY . .

# Use Makefile in order to test/analyse and report results to SonarQube
# Sonar analysis requires that SonarQube server is running (by default on 
# host 'sonarqube' and port 9000, see Makefile).
# This can easily be achieved by naming the SonarQube container 'sonarqube' and
# building this image within the same (docker) network where the 'sonarqube'
# container is running.
# SONARNOSCM disables SonarQube's version control support (e.g., for git) as
# it is not customary to copy the actual repository (.git/) into the image
# for building (also see Makefile) 
# SONAR reporting can be disabled by passing --build-arg SONAR=False
# only unit tests will be run in this case
# Note that the build won't fail if unit tests fail (in both cases)
RUN if [ ${SONAR} = "True" ] ; then \
    make clean-all \
    && make install_dev \
    && make sonar SONARHOST=${SONARHOST} SONARPORT=${SONARPORT} SONARNOSCM=True \
    ; else \
    make clean-all \
    && make install_dev \
    && (make pylint test || exit 0) \
    ;fi
# Use Makefile in order to build a Python wheel from the app
RUN make clean-all && make bdist_wheel

# Start a new stage for the deployment image in order to minimize image size
# --> sonar-scanner and test libs are not required here 
FROM python:3.8-slim-buster

ARG ENTRYPOINT
ENV ENTRYPOINT=${ENTRYPOINT}
# pip environment variables: no version check, no caching
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Create a user which will be used for running the application
# --> do not run application as root
RUN groupadd user \
    && useradd --gid user --shell /bin/bash --create-home user

# Copy the Python wheel from the build image to the deployment image
# --> the specfic name of the wheel is generated by Python setuptools and
# cannot be easily controlled externaly
# --> copy wheel file to its own directory with a generic name in order to
# easily access the wheel from outside the image/container
# --> docker cp does not support wildcards
COPY --from=build /app/dist/*.whl /dist/ 
# Install the Python wheel 
#(also installs all dependencies are specified in the wheel)
RUN pip install /dist/*.whl
# Switch to working directory in user's home, dir exists due to useradd param
WORKDIR /home/user/app
# Copy entrypoint.sh script from build stage
COPY --from=build /app/scripts/entrypoint.sh .
# Change owner
RUN chown user:user . ; chown user:user entrypoint.sh
# Switch user/set user for running the app
USER user
# Specify entrypoint in json style 
ENTRYPOINT ["./entrypoint.sh"]
# Provide default args with CMD. Default args are overridden by command-line
# arguments to docker run on the command-line.
CMD ["--help"]
# Important: both entrypoint and cmd have to be specified in json style
# --> json style allows for better CLI interoperability when running the 
# container. Most importantly users can provide command-line arguments for
# the entrypoint script. 
