"""Command-line interface for creating and adminitrating template projects

Defines module functions for sub-commands
"""
import sys
import platform
import logging
import argparse

import devopstemplate
from devopstemplate.template import DevOpsTemplate


def create(args):
    """Wrapper for sub-command create

    Params:
        args: argparse.Namespace object with argument parser attributes
    """
    template = DevOpsTemplate(projectdirectory=args.project_dir,
                              overwrite_exists=args.overwrite_exists,
                              skip_exists=args.skip_exists)
    template.create(projectname=args.projectname,
                    add_scripts=args.add_scripts_dir,
                    add_docs=args.add_docs_dir,
                    no_gitignore=args.no_gitignore_file,
                    no_readme=args.no_readme_file,
                    no_sonar=args.no_sonar,
                    no_docker=args.no_docker)


def manage(args):
    """Wrapper for sub-command manage

    Params:
        args: argparse.Namespace object with argument parser attributes
    """
    print('manage:')
    print(str(args))


def parse_args(args_list):
    """Parse command-line arguments and call a function for processing user
    request.

    The parser defines (sub) commands which are processed with the 'func'
    attribute function obtained from the parsing result, i.e., Namespace object
    ( Namespace=parser.parse_args(args) ).
    Each command sets its function to the func attribute with set_defaults.
    After all command-line flags have been processed, the function associated
    with func is executed.

    Params:
        args_list: list of strings with command-line flags (sys.argv[1:])
    """
    logger = logging.getLogger('template:parse_args')
    descr = ''.join(['Create and manage DevOps template projects ',
                     f'(version {devopstemplate.__version__})'])
    parser = argparse.ArgumentParser(description=descr)
    # top-level arguments (optional)
    parser.add_argument('--project-dir', default='.',
                        help='Project directory, default: current directory')
    parser.add_argument('--skip-exists', action='store_true',
                        help=('Skip copying files if they already '
                              'exist in the project directory '
                              'without failing'))
    parser.add_argument('--overwrite-exists', action='store_true',
                        help=('Overwrite files if they already '
                              'exist in the project directory '
                              'without failing'))
    parser.add_argument('--quiet', action='store_true',
                        help='Only print warning/error messages')
    parser.add_argument('--verbose', action='store_true',
                        help='Print debug messages')
    # Default for printing help message if no command is provided
    # attribute 'func' is set to a lambda function
    # --> if attribute func keeps the lambda function until the entire parser
    # has been evaluated: call print_help() and show the help message
    parser.set_defaults(func=lambda _: parser.print_help())
    # Subparser commands for project creation and management
    subparsers = parser.add_subparsers(help='Commands')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('projectname',
                               help=('Name of the Python package / '
                                     'top-level import directory'))
    create_parser.add_argument('--add-scripts-dir', action='store_true',
                               help='Add scripts directory')
    create_parser.add_argument('--add-docs-dir', action='store_true',
                               help='Add docs directory')
    create_parser.add_argument('--no-gitignore-file', action='store_true',
                               help='Do not add .gitignore file')
    create_parser.add_argument('--no-readme-file', action='store_true',
                               help='Do not add README.md file')
    create_parser.add_argument('--no-sonar', action='store_true',
                               help='Do not add SonarQube support')
    create_parser.add_argument('--no-docker', action='store_true',
                               help='Do not add Docker support')
    # If the create subparser has been activated by the 'create' command,
    # override the func attribute with a pointer to the 'create' function
    # (defined above) --> overrides default defined for the main parser.
    create_parser.set_defaults(func=create)

    manage_parser = subparsers.add_parser('manage',
                                          help=('Add individual components of '
                                                'the DevOps template'))
    manage_parser.add_argument('--add-scripts-dir', action='store_true',
                               help='Add scripts directory')
    manage_parser.add_argument('--add-docs-dir', action='store_true',
                               help='Add docs directory')
    manage_parser.add_argument('--add-gitignore-file', action='store_true',
                               help='Add .gitignore file')
    manage_parser.add_argument('--add-readme-file', action='store_true',
                               help='Add README.md file')
    manage_parser.add_argument('--add-sonar', action='store_true',
                               help='Add SonarQube support')
    manage_parser.add_argument('--add-docker', action='store_true',
                               help='Add Docker support')
    # If the manage subparser has been activated by the 'manage' command,
    # override the func attribute with a pointer to the 'manage' function
    # (defined above) --> overrides default defined for the main parser.
    manage_parser.set_defaults(func=manage)

    args_ns = parser.parse_args(args=args_list)

    # Set log level according to command-line flags
    if args_ns.verbose:
        devopstemplate.LOGCONFIG.debug()
    elif args_ns.quiet:
        devopstemplate.LOGCONFIG.warning()

    logger.debug('Command-line args: %s', args_list)
    args_dict = vars(args_ns)
    logger.debug('Options:\n%s', '\n'.join(f'{key} : {val}'
                                           for key, val in args_dict.items()))
    args_ns.func(args_ns)


def main():
    logger = logging.getLogger(f'{__name__}:main')
    logger.info('%s:: %s\n', platform.node(), ' '.join(sys.argv))
    parse_args(sys.argv[1:])


if __name__ == "__main__":
    main()
