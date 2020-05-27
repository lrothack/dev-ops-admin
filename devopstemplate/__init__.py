"""Initializations on Python package level

- Obtain Python package version with setuptools
- Initialize Python logging framework

Useful log message formats:
LOGGING_FORMAT = '%(asctime)-15s: [%(name)s] %(message)s'
LOGGING_FORMAT = '[%(name)s] %(message)s'
LOGGING_FORMAT = '%(message)s'
"""

import pkg_resources
__version__ = pkg_resources.require(__name__)[0].version

import logging


def logging_debug():
    logging_format = '%(asctime)-15s: [%(name)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=logging_format)


def logging_info():
    logging_format = '%(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=logging_format)


def logging_warn():
    logging_format = '%(message)s'
    logging.basicConfig(level=logging.WARNING,
                        format=logging_format)


# Default log level: info
logging_info()
