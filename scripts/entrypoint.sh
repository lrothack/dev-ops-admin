#!/bin/bash

# start Python application
# ENTRYPOINT environment variable contains the name of the executable
# (expected to be on the PATH)
# $@ forwards all command-line arguments from this script to the 
# entry point executable
$ENTRYPOINT $@
