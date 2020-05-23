import sys
import platform
import logging
import argparse


def main():
    logger = logging.getLogger(__name__+':main')
    logger.info('%s:: %s\n', platform.node(), ' '.join(sys.argv))
    descr = ''.join(('This is a sample project for trying out DevOps in ',
                     'Python. The app adds two numbers and the result is off ',
                     'by one. (Intended for experimenting with a failing ',
                     'unit test.)'))
    parser = argparse.ArgumentParser(description=descr)

    subparsers = parser.add_subparsers(help='Commands')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('projectname', required=True,
                               help=('Name of the Python package / '
                                     'top-level import directory'))
    create_parser.add_argument('--no-gitignore', action='store_true',
                               help='Do not add .gitignore file')
    create_parser.add_argument('--no-readme', action='store_true',
                               help='Do not add README.md file')
    create_parser.add_argument('--no-scripts', action='store_true',
                               help='Do not add scripts directory')
    create_parser.add_argument('--no-docs', action='store_true',
                               help='Do not add docs directory')
    create_parser.add_argument('--no-sonar', action='store_true',
                               help='Do not add SonarQube support')
    create_parser.add_argument('--no-docker', action='store_true',
                               help='Do not add Docker support')

    manage_parser = subparsers.add_parser('manage',
                                          help=('Add individual components of '
                                                'the DevOps template'))
    manage_parser.add_argument('--add-gitignore', action='store_true',
                               help='Add .gitignore file')
    manage_parser.add_argument('--add-readme', action='store_true',
                               help='Add README.md file')
    manage_parser.add_argument('--add-scripts', action='store_true',
                               help='Add scripts directory')
    manage_parser.add_argument('--add-docs', action='store_true',
                               help='Add docs directory')
    manage_parser.add_argument('--add-sonar', action='store_true',
                               help='Add SonarQube support')
    manage_parser.add_argument('--add-docker', action='store_true',
                               help='Add Docker support')
    result = parser.parse_args()


if __name__ == "__main__":
    main()
