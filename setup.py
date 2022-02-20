"""Setup.py configuration file
"""
import os
import re
import itertools
import json
from setuptools import setup


def parse_version():
    """Parse version number from __init__.py in top-level import package

    It is assumed that the version is defined as a string and the '=' sign
    is surrounded by at most one whitespace character to the left and to the
    right.

    Returns:
        version string
    Raises:
        ValueError if the parser could not match the version definition
    """
    init_fpath = os.path.join('devopstemplate', '__init__.py')
    with open(init_fpath, 'r', encoding='utf-8') as handle:
        init_contents = handle.read()
        ver_re = r"^__version__ ?= ?['\"]([^'\"]*)['\"]"
        match = re.search(ver_re, init_contents, re.M)
        if match:
            version = match.group(1)
            return version
        raise ValueError('Could not parse version string')


def parse_template_index():
    """Load json that defines template structure
    """
    with open('devopstemplate/template.json', 'r', encoding='utf-8') as handle:
        template_dict = json.load(handle)
        template_index = list(itertools.chain(*template_dict.values()))
    return template_index


def read_file(filepath):
    """Read file as text

    Params:
        filename: relative/absolute path to the file
    Returns:
        contents as str
    """
    with open(filepath, 'r', encoding='utf-8') as handle:
        return handle.read()


# Parse version
VERSION = parse_version()
# Read list of template files that will be packaged for installation with the
# devopstemplate tool
TEMPLATE_INDEX = parse_template_index()

# Read Readme that will be used as long package description
DESCRIPTION_LONG = read_file('README.md')

# Read list of Python package dependencies
INSTALL_REQUIRES = read_file('requirements.txt').splitlines()

# setup.py defines the Python package. The build process is triggered from
# Makefile. Adapt Makefile variable SETUPTOOLSFILES if build file dependencies
# change.
setup(name='devopstemplate',
      version=VERSION,
      python_requires='>= 3.6',
      # Import package
      packages=['devopstemplate'],
      # Package dependencies
      install_requires=INSTALL_REQUIRES,
      # Defines dev environment containing development dependencies
      # (for linting, testing, etc.)
      extras_require={'dev': ['pip >= 20.1.1',
                              'wheel',
                              'pytest',
                              'coverage',
                              'bandit',
                              'pylint',
                              'autopep8',
                              'flake8']
                      },
      entry_points={'console_scripts':
                    ['devopstemplate=devopstemplate.main:main']
                    },
      package_data={
          # Include data files in devopstemplate package
          # the file template.index specifies file paths relative to
          # devopstemplate/template directory
          'devopstemplate': (['template.json', 'commands.json'] +
                             [f'template/{fpath}'
                              for fpath in TEMPLATE_INDEX]),
      },
      # Generally do not assume that the package can safely be run as a zip
      # archive
      zip_safe=False,
      # Metadata to display on PyPI
      author='Leonard Rothacker',
      author_email='leonard.rothacker@googlemail.com',
      description=('This package provides a command-line interface for ' +
                   'setting up a Python project based on a dev-ops template'),
      long_description=DESCRIPTION_LONG,
      long_description_content_type='text/markdown',
      keywords='devops template sonarqube docker code-analysis',
      url='https://github.com/lrothack/dev-ops-admin',
      license='MIT',
      platforms=['any'],
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                   'Environment :: Console',
                   ]
      )
