from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('devopstemplate/template/README.md', 'r') as fh:
    long_description_template = fh.read()

with open('devopstemplate/template.index', 'r') as fh:
    template_index = fh.read().splitlines()

# setup.py defines the Python package. The build process is triggered from
# Makefile. Adapt Makefile variable SETUPTOOLSFILES if build file dependencies
# change.
setup(name='devopstemplate',
      version='0.3.0',
      # Import package
      packages=['devopstemplate'],
      # Installation dependencies
      setup_requires=['setuptools >= 40.9.0',
                      'wheel'],
      # Package dependencies
      # install_requires=[],
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
          'devopstemplate': (['template.index'] +
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
                   'setting up a Python project based on a DevOps template'),
      long_description=long_description,
      long_description_content_type='text/markdown',
      keywords='devops sonarqube docker',
      url='https://github.com/lrothack/dev-ops-admin',
      license='MIT',
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.7'
                   'Programming Language :: Python :: 3.8'
                   'Environment :: Console',
                   ]
      )
