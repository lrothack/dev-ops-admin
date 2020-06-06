"""Initializations on Python package level

- Obtain Python package version with setuptools
- Initialize Python logging framework
"""

import pkg_resources
__version__ = pkg_resources.require(__name__)[0].version

import logging


class _LoggerConfig():
    """
    Useful log message formats:
    LOGGING_FORMAT = '%(asctime)-15s: [%(name)s] %(message)s'
    LOGGING_FORMAT = '[%(name)s] %(message)s'
    LOGGING_FORMAT = '%(message)s'
    """

    def __init__(self):
        # Default log level: info
        # logging.basicConfig(level=logging.INFO,
        #                     format='%(message)s')
        self.__format_plain = '%(message)s'
        self.__format_debug = '%(asctime)-15s: [%(name)s] %(message)s'
        self.__handler = logging.StreamHandler()
        logging.getLogger().addHandler(self.__handler)
        self.info()

    def debug(self):
        logging.getLogger().setLevel(logging.DEBUG)
        self.__handler.setFormatter(logging.Formatter(self.__format_debug))

    def info(self):
        logging.getLogger().setLevel(logging.INFO)
        self.__handler.setFormatter(logging.Formatter(self.__format_plain))

    def warning(self):
        logging.getLogger().setLevel(logging.WARNING)
        self.__handler.setFormatter(logging.Formatter(self.__format_plain))


LOGCONFIG = _LoggerConfig()
