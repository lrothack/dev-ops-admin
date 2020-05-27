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
# Default log level: info
# logging.basicConfig(level=logging.INFO,
#                     format='%(message)s')
LOGGING_HANDLER = logging.StreamHandler()
logging.getLogger().addHandler(LOGGING_HANDLER)
logging.getLogger().setLevel(logging.INFO)


def logging_debug():
    logging_format = '%(asctime)-15s: [%(name)s] %(message)s'
    logging.getLogger().setLevel(logging.DEBUG)
    LOGGING_HANDLER.setFormatter(logging.Formatter(logging_format))


def logging_info():
    logging_format = '%(message)s'
    logging.getLogger().setLevel(logging.INFO)
    LOGGING_HANDLER.setFormatter(logging.Formatter(logging_format))


def logging_warn():
    logging_format = '%(message)s'
    logging.getLogger().setLevel(logging.WARNING)
    LOGGING_HANDLER.setFormatter(logging.Formatter(logging_format))
