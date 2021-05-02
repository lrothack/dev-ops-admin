"""Defines template creation and modification wrt user configurations.
"""

import os
import subprocess
import shutil
import json
from jinja2 import Template
import devopstemplate.pkg as pkg


class CommandsConfig():
    """Represents definitions of optional parameters for (sub-)commands
    create, manage, cookiecutter
    """

    # Static variable storing the command definitions
    __commands_dict = None

    def __init__(self):
        """Loads dictionary with command definitions, if not already present
        """
        if not CommandsConfig.__commands_dict:
            CommandsConfig.__commands_dict = self.__load_commands_dict()
        self.__commands_dict = CommandsConfig.__commands_dict

    def values(self, command, section):
        """Obtain a section for a command from the json configuration

        Params:
            command: String specifying the command (create, manage,
                cookiecutter)
            section: String specifying the configuration section (template,
                parameters, components)
        Returns: List of string xor dict objects containing the
            options/components of the configurations section, empty list if
            the section is not available
        """
        cmd_dict = self.__commands_dict[command]
        try:
            result_list = cmd_dict[section]
        except KeyError:
            result_list = []

        return result_list

    @staticmethod
    def __load_commands_dict():
        """Load commands definition from package resource

        Returns:
            commands_dict: Dictionary representing commands.json
        """
        # Load commands.json with definitions for command-line arguments
        # -> sub-commands, their arguments, defaults and help messages
        commands_fname = 'commands.json'
        commands_str = pkg.string(commands_fname)
        # Define context for substituting default values in the commands file
        # in order to be substituted with Jinja2
        # git user and email as default for author data
        name, email = CommandsConfig.git_user()
        context = {'git_name': name, 'git_email': email}
        commands_str = Template(commands_str).render(**context)
        commands_dict = json.loads(commands_str)
        return commands_dict

    @staticmethod
    def git_user():
        """Obtain git user name and email from git config.

        The function expects that the command 'git' is found on the PATH.

        Returns:
            name: String with git user name, empty string if no 'git' command
            email: String with git user email, empty string if no 'git' command
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


class ProjectConfig():
    """Generate config dictionaries for template actions:
    create, manage, cookiecutter

    Supports a CLI for asking configuration values from the user in interactive
    mode.
    """

    def __init__(self, args):
        """Initialize config with defaults that all template actions have in
        common

        Params:
            args: argparse.Namespace object with command-line arguments
        """
        # Generate dict from namespace attributes (save dict as a copy)
        self.__args_dict = dict(vars(args))
        self.project_dir = os.path.abspath(args.project_dir)
        self.overwrite_exists = args.overwrite_exists
        self.skip_exists = args.skip_exists
        self.dry_run = args.dry_run
        # load definition for (sub-)commands
        self.__cfg = CommandsConfig()

    def __param_dict(self, command):
        """Generate project configuration for creating an instance of the
        devops template. Defines the context for rendering Jinja2 templates.

        Supports interactive mode.

        Params:
            command: String specifying the command
        Returns:
            param_dict: Dictionary with configurations
        """
        param_def_list = self.__cfg.values(command, 'parameters')
        param_key_list = [p['name'].replace('-', '_') for p in param_def_list]
        # Define param dict for project context
        param_dict = {key: self.__args_dict[key] for key in param_key_list}
        # Overwrite default/specified values in interactive mode
        if ('interactive' in self.__args_dict and
                self.__args_dict['interactive']):
            param_dict = self.__input(param_key_list, param_dict)
        return param_dict

    def __comp_list(self, command):
        """Generate list of project components that will be installed according
        to template.json

        Supports interactive mode.

        Params:
            command: String specifying the command.
        Returns:
            comp_list: List of strings specifying template components
        """
        comp_def_list = self.__cfg.values(command, 'components')
        # Generate internal identifiers (keys) for component by their names
        comp_key_list = [c['name'].replace('-', '_') for c in comp_def_list]
        # comp_dict: dict of project component dicts
        # (keys: name, default, help, template)
        # 'default' defines how to interpret (positive or
        # negative) boolean component flags provided by the user,
        # i.e. for example, add-* or no-*
        # add-*, default: false -> do not add comp. by default, only with flag
        # no-*,  default: true  -> add comp. by default, do not add with flag
        # 'template' is a list of template identifier for installing component
        # files defined in template.json
        comp_dict = dict(zip(comp_key_list, comp_def_list))

        # Define comp_args dict for project component flags specified by user
        comp_args = {key: self.__args_dict[key] for key in comp_key_list}
        # Overwrite default/specified values in interactive mode
        if ('interactive' in self.__args_dict and
                self.__args_dict['interactive']):
            comp_args = self.__input(comp_key_list, comp_args)
        # Translate flags (pos and neg) to positive list of components
        # Initialize with default components for command
        # Create a copy since the list will be extended
        comp_list = list(self.__cfg.values(command, 'template'))
        for key in comp_key_list:
            # Whether to add the component by default (when no user flag has
            # been set)
            comp_default = comp_dict[key]['default']
            # Negate the default boolean value if a flag has been set for the
            # component by the user)
            comp_add = not comp_default if comp_args[key] else comp_default
            if comp_add:
                comp_list.extend(comp_dict[key]['template'])

        return comp_list

    def create(self):
        """Generate project configuration for action 'create'.

        Supports interactive mode.

        Returns:
            param_dict: Dictionary with configurations for creating an instance
                of the devops template.
            comp_list: List of template components that will be installed
                according to template.json
        """
        # Set default for package_name if not present
        project_name = os.path.basename(self.project_dir)
        # If package_name is not given as CLI argument
        if not self.__args_dict['package_name']:
            # Slugify project_name and use as default for package_name
            project_slug = project_name.replace(' ', '_').replace('-', '_')
            project_slug = project_slug.lower()
            self.__args_dict['package_name'] = project_slug

        # Parameters
        param_dict = self.__param_dict(command='create')
        # Set project name
        param_dict['project_name'] = project_name
        # Define project package name: slugify given package_name
        # Default package_name is defined above or given as CLI arg
        # and can be overwritten in interactive mode in __param_dict func
        # --> define project_slug based on package_name in param_dict var
        project_slug = param_dict['package_name']
        project_slug = project_slug.replace(' ', '_').replace('-', '_')
        param_dict['project_slug'] = project_slug.lower()

        # Components
        comp_list = self.__comp_list(command='create')

        return param_dict, comp_list

    def manage(self):
        """Generate project configuration for action 'manage'.

        Returns:
            param_dict: Dictionary with configurations for modifying an
                instance of the devops template.
            comp_list: List of template components that will be added to the
                template instance according to template.json
        """
        # Parameters
        param_dict = {'project_name': os.path.basename(self.project_dir)}

        # Components
        comp_list = self.__comp_list(command='manage')

        return param_dict, comp_list

    def cookiecutter(self):
        """Generate project configuration for action 'cookiecutter'.

        Returns:
            param_dict: Dictionary with configurations for creating a
                cookiecutter template from the devops template.
            comp_list: List of components that will be added to the
                cookiecutter template according to template.json
        """
        # Parameters
        param_dict = self.__param_dict(command='cookiecutter')
        # Set standard cookiecutter definition for project_slug
        project_slug = ''.join(["{{ ",
                                "cookiecutter.project_name.lower()",
                                ".replace(' ', '_')",
                                ".replace('-', '_')",
                                " }}"])
        param_dict['project_slug'] = project_slug

        # Components
        comp_list = self.__comp_list(command='cookiecutter')

        return param_dict, comp_list

    @staticmethod
    def __input(key_list, params):
        """Query the user for a list of configuration options over the
        command-line. Supports boolean options: User input [y]es and [n]o.
        Default values can be confirmed with 'enter'.

        Params:
            key_list: List of strings with configurations options/keys.
            params: Dictionary the contains mappings from configuration options
                to default values.
        Returns:
            params: Dictionary the contains mappings from configuration options
                to values that have be update/confirmed by the user.

        """
        for key in key_list:
            value = params[key]
            key_disp = key.replace('_', '-')
            if isinstance(value, bool):
                # Convert boolean value to string
                value = 'y' if value else 'n'
                value_user = input(f'{key_disp} [ {value} ] : ')
                # Convert string value_user to boolean
                value_user = value_user == 'y'
            else:
                value_user = input(f'{key_disp} [ "{value}" ] : ')
                # Keep initial value if user just presses enter
                # use the user input otherwise
                value_user = value if value_user == '' else value_user
            params[key] = value_user
        return params
