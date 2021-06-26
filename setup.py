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
    with open(init_fpath, 'r') as fh:
        init_contents = fh.read()
        ver_re = r"^__version__ ?= ?['\"]([^'\"]*)['\"]"
        match = re.search(ver_re, init_contents, re.M)
        if match:
            version = match.group(1)
            return version
        else:
            raise ValueError('Could not parse version string')


def parse_template_index():
    with open('devopstemplate/template.json', 'r') as fh:
        template_dict = json.load(fh)
        template_index = list(itertools.chain(*template_dict.values()))
    return template_index


# Parse version
version = parse_version()
# Read list of template files that will be packaged for installation with the
# devopstemplate tool
template_index = parse_template_index()

# Read Readme that will be used as long package description
with open('README.md', 'r') as fh:
    long_description = fh.read()

# Read list of Python package dependencies
with open('requirements.txt', 'r') as fh:
    install_requires = fh.read().splitlines()

# setup.py defines the Python package. The build process is triggered from
# Makefile. Adapt Makefile variable SETUPTOOLSFILES if build file dependencies
# change.
setup(name='devopstemplate',
      version=version,
      python_requires='>= 3.6',
      # Import package
      packages=['devopstemplate'],
      # Installation dependencies
      setup_requires=['setuptools >= 40.9.0',
                      'wheel'],
      # Package dependencies
      install_requires=install_requires,
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
                              for fpath in template_index]),
      },
      # Generally do not assume that the package can safely be run as a zip
      # archive
      zip_safe=False,
      # Metadata to display on PyPI
      author='Leonard Rothacker',
      author_email='leonard.rothacker@googlemail.com',
      description=('This package provides a command-line interface for ' +
                   'setting up a Python project based on a dev-ops template'),
      long_description=long_description,
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
