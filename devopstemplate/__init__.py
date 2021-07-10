"""Initializations on Python package level

- Define package version
- Initialize Python logging framework
"""

from devopstemplate.log import LoggerConfig

# Version can be parsed from setup.py or managed globally,
# e.g., with bumpversion
__version__ = '0.8.3'


# Global module variable that stores a singelton of the LoggerConfig
# Can be used globally in order to adjust log behavior.
LOGCONFIG = LoggerConfig()
