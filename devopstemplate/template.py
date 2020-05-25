import os
import sys
import platform
import logging
import argparse

import devopstemplate.pkg as pkg


class DevOpsTemplate():

    def __init__(self, project_dir='.'):
        logger = logging.getLogger('devopstemplate')
        if not os.path.exists(project_dir):
            logger.info(f'creating directory: {project_dir}')
            os.makedirs(project_dir)
        self.__project_dir = project_dir
        template_index = pkg.string('template.index')
        template_index_list = template_index.splitlines()
        logger.info(template_index_list)

    def create(self, projectname,
               no_gitignore, no_readme, no_scripts,
               no_docs, no_sonar, no_docker):
        pass

    def manage(self, add_gitignore, add_readme, add_scripts,
               add_docs, add_sonar, add_docker):
        pass

    def __add_common(self, projectname):
        pass

    def __add_gitignore(self):
        pass

    def __add_readme(self):
        pass

    def __add_scripts(self):
        pass

    def __add_docs(self):
        pass

    def __add_sonar(self):
        pass

    def __add_docker(self):
        pass


def parse_args(args):
    logger = logging.getLogger(f'{__name__}:parse_args')
    descr = ''.join(['Create and manage DevOps template projects'])
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('--project-dir', default='.',
                        help='Project directory, default: current directory')
    subparsers = parser.add_subparsers(help='Commands')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('projectname',
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
    return result


def process_args(args):
    result = parse_args(args)


def main():
    logger = logging.getLogger(f'{__name__}:main')
    logger.info('%s:: %s\n', platform.node(), ' '.join(sys.argv))
    process_args(sys.argv[1:])


if __name__ == "__main__":
    main()
