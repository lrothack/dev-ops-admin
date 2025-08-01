FROM python:3.12-slim AS build
# The python base image contains python, pip, etc. in a slim Debian buster 

# Variables defined with ARG can be modified when building the Docker image
# --> see docker build --build-arg

# Name of the code analyses report file
ARG REPORTFILE=code-analyses.txt

# pip environment variables: no version check, no caching
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Install debian packages required for executing make targets
RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

# Copy Python app into image 
WORKDIR /app
COPY . .

# Use Makefile in order to test/analyse code
# Docker build fails if unit tests fail
RUN make clean-all && \
    make install-dev && \
    make check && \
    make report >${REPORTFILE}

# Use Makefile in order to build a Python wheel from the app
RUN make clean-all && make build

# Start a new stage for the deployment image in order to minimize image size
# --> libs for code analysis are not required in the final image
FROM python:3.12-slim

# Define value of ENTRYPOINT environment variable with build-arg ENTRYPOINT.
# The environment variable will be available within the Docker container.
# It specifies the name of the executable which will be called in the script
# 'entrypoint.sh' in order to start the application. The script 'entrypoint.sh'
# is defined as the Docker ENTRYPOINT (see below).
ARG ENTRYPOINT
ENV ENTRYPOINT=${ENTRYPOINT}
# Name of the code analyses report file
ARG REPORTFILE=code-analyses.txt
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
COPY --from=build /app/entrypoint.sh .
# Copy REPORTFILE from build stage
COPY --from=build /app/${REPORTFILE} .
# Change owner
RUN chown user:user . ; \
    chown user:user entrypoint.sh; \
    chown user:user ${REPORTFILE}
# Switch user/set user for running the app
USER user
# Specify entrypoint in json style 
ENTRYPOINT ["bash", "./entrypoint.sh"]
# Provide default args with CMD. Default args are overridden by command-line
# arguments to docker run on the command-line.
# CMD ["--help"]
# Important: both entrypoint and cmd have to be specified in json style
# --> json style allows for better CLI interoperability when running the 
# container. Most importantly users can provide command-line arguments for
# the entrypoint script.