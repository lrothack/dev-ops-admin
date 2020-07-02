"""Command-line interface for creating and adminitrating template projects

Defines module functions for sub-commands
"""
import sys
import platform
import logging
import argparse
import subprocess
import shutil
import json
from jinja2 import Template
import devopstemplate
import devopstemplate.pkg as pkg
from devopstemplate.config import ProjectConfig
from devopstemplate.template import DevOpsTemplate


def git_user():
    """Obtain git user name and email from git config.

    The function expects that the command 'git' is found on the PATH.

    Returns:
        name: string with git user name, empty string if no 'git' command
        email: string with git user email, empty string if no 'git' command
    """
    name = ''
    email = ''
    if shutil.which('git'):
        name = subprocess.check_output(['git', 'config', 'user.name'],
                                       stderr=subprocess.STDOUT,
                                       encoding='utf-8')
        email = subprocess.check_output(['git', 'config', 'user.email'],
                                        stderr=subprocess.STDOUT,
                                        encoding='utf-8')
    return name.strip(), email.strip()


def create(args):
    """Wrapper for sub-command create

    Params:
        args: argparse.Namespace object with argument parser attributes
    """

    config = ProjectConfig(args)
    template = DevOpsTemplate(projectdirectory=config.project_dir,
                              overwrite_exists=config.overwrite_exists,
                              skip_exists=config.skip_exists,
                              dry_run=config.dry_run)

    params = config.create()
    template.create(projectconfig=params)


def manage(args):
    """Wrapper for sub-command manage

    Params:
        args: argparse.Namespace object with argument parser attributes
    """
    config = ProjectConfig(args)
    template = DevOpsTemplate(projectdirectory=config.project_dir,
                              overwrite_exists=config.overwrite_exists,
                              skip_exists=config.skip_exists,
                              dry_run=config.dry_run)

    params = config.manage()
    template.manage(projectconfig=params)


def cookiecutter(args):
    """Wrapper for sub-command manage

    Params:
        args: argparse.Namespace object with argument parser attributes
    """
    config = ProjectConfig(args)
    template = DevOpsTemplate(projectdirectory=config.project_dir,
                              overwrite_exists=config.overwrite_exists,
                              skip_exists=config.skip_exists,
                              dry_run=config.dry_run)

    params = config.cookiecutter()
    template.cookiecutter(projectconfig=params)


def arg_command_group(parser, group_name, group_argument_list):
    """Add a group of optional arguments to the parser.

    Params:
        parser: argparse.ArgumentParser where the argument group will be added.
        group_name: string with the name of the argument group.
        group_argument_list: list of dict objects where each dict specifies an
            argument.
    Returns:
        group: the argument group object that has been created for the parser.
    Raises:
        ValueError: if the group_argument_list is empty
    """
    if not group_argument_list:
        raise ValueError('Invalid group_argument_list')

    # Add argument group
    group = parser.add_argument_group(group_name)

    # Add arguments
    for arg_dict in group_argument_list:
        arg_name = arg_dict['name']
        arg_name = f'--{arg_name}'
        arg_help = arg_dict['help']
        arg_value = arg_dict['default']
        if isinstance(arg_value, bool) and arg_value:
            group.add_argument(arg_name, action='store_false', help=arg_help)
        elif isinstance(arg_value, bool) and not arg_value:
            group.add_argument(arg_name, action='store_true', help=arg_help)
        else:
            group.add_argument(arg_name, default=arg_value, help=arg_help)

    return group


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
    logger = logging.getLogger('main.parse_args')

    # Load commands.json that contains definitions for command-line arguments
    # -> sub-commands, their arguments, defaults and help messages
    commands_fname = 'commands.json'
    commands_str = pkg.string(commands_fname)
    # Define context for substituting default values in the commands file in
    # order to be substituted with Jinja2
    # git user and email as default for author data
    name, email = git_user()
    context = {'git_name': name, 'git_email': email}
    commands_dict = json.loads(Template(commands_str).render(**context))

    descr = ''.join(['Create and manage dev-ops template projects. ',
                     'The project name is the name of the project directory. ',
                     'The package name is a slug of the project name.'])
    parser = argparse.ArgumentParser(description=descr)
    # top-level arguments (optional)
    parser.add_argument('--project-dir', default='.',
                        help='Project directory, default: current directory')
    parser.add_argument('--skip-exists', action='store_true',
                        help=('Skip copying files if they already '
                              'exist in the project directory'))
    parser.add_argument('--overwrite-exists', action='store_true',
                        help=('Overwrite files if they already '
                              'exist in the project directory'))
    parser.add_argument('--quiet', action='store_true',
                        help='Print only warning/error messages')
    parser.add_argument('--verbose', action='store_true',
                        help='Print debug messages')
    parser.add_argument('--dry-run', action='store_true',
                        help='Pretend to perform actions')
    parser.add_argument('--version', action='store_true',
                        help='Print version')
    # Default for printing help message if no command is provided
    # attribute 'func' is set to a lambda function
    # --> if attribute func keeps the lambda function until the entire parser
    # has been evaluated: call print_help() and show the help message
    parser.set_defaults(func=lambda _: parser.print_help())
    # Subparser commands for project creation and management
    subparsers = parser.add_subparsers(help='Commands')

    create_commands_dict = commands_dict['create']
    create_parser = subparsers.add_parser('create',
                                          help=('Create a new project based '
                                                'on the dev-ops template'))
    create_parser.add_argument('-i', '--interactive', action='store_true',
                               help=('Configure project parameters/components'
                                     ' interactively'))

    arg_command_group(create_parser, 'project parameters',
                      group_argument_list=create_commands_dict['parameters'])
    arg_command_group(create_parser, 'project components',
                      group_argument_list=create_commands_dict['components'])
    # If the create subparser has been activated by the 'create' command,
    # override the func attribute with a pointer to the 'create' function
    # (defined above) --> overrides default defined for the main parser.
    create_parser.set_defaults(func=create)

    manage_commands_dict = commands_dict['manage']
    manage_parser = subparsers.add_parser('manage',
                                          help=('Add individual components of '
                                                'the dev-ops template'))
    arg_command_group(manage_parser, 'project components',
                      group_argument_list=manage_commands_dict['components'])
    # If the manage subparser has been activated by the 'manage' command,
    # override the func attribute with a pointer to the 'manage' function
    # (defined above) --> overrides default defined for the main parser.
    manage_parser.set_defaults(func=manage)

    cc_commands_dict = commands_dict['cookiecutter']
    cc_parser = subparsers.add_parser('cookiecutter',
                                      help=('Create a cookiecutter'
                                            ' template'))
    cc_parser.add_argument('-i', '--interactive', action='store_true',
                           help=('Configure project parameters/components'
                                 ' interactively'))
    arg_command_group(cc_parser, 'project parameters',
                      group_argument_list=cc_commands_dict['parameters'])
    # If the cookiecutter subparser has been activated by the 'cookiecutter'
    # command, override the func attribute with a pointer to the 'cookiecutter'
    # function (defined above) --> overrides default for the main parser.
    cc_parser.set_defaults(func=cookiecutter)
    args_ns = parser.parse_args(args=args_list)

    # If version flag is set: print version and quit
    if args_ns.version:
        logger.info('devopstemplate v%s', devopstemplate.__version__)
        return

    # Set log level according to command-line flags
    if args_ns.verbose:
        devopstemplate.LOGCONFIG.debug()
        logger.debug('%s:: %s', platform.node(), ' '.join(sys.argv))
        logger.debug('devopstemplate v%s\n', devopstemplate.__version__)
    elif args_ns.quiet:
        devopstemplate.LOGCONFIG.warning()

    logger.debug('Command-line args: %s', args_list)
    args_dict = vars(args_ns)
    logger.debug('Options:\n%s', ', '.join(f'{key} : {val}'
                                           for key, val in args_dict.items()))
    args_ns.func(args_ns)


def main():
    """Entrypoint for starting the command-line interface.
    Control-flow continues depending on user arguments.

    Passes all command-line flags sys.argv[1:] to argparse
    (implemented in parse_args)
    """
    parse_args(sys.argv[1:])


if __name__ == "__main__":
    main()
