"""Defines template creation and modification wrt user configurations."""

import argparse
import json
import os
import shutil
import subprocess
from typing import Any, cast

from jinja2 import Template

from devopstemplate import pkg

ARGUMENTS_INTERACTIVE_KEY = "interactive"
ARGUMENTS_PACKAGE_NAME_KEY = "package_name"
ARGUMENTS_PROJECT_DIR_KEY = "project_dir"
ARGUMENTS_PROJECT_NAME_KEY = "project_name"
ARGUMENTS_PROJECT_SLUG_KEY = "project_slug"
ARGUMENTS_YES_KEY = "y"
ARGUMENTS_NO_KEY = "n"
COOKIECUTTER_FNAME = "cookiecutter.json"
COMMANDS_FNAME = "commands.json"
COMMANDS_CREATE_KEY = "create"
COMMANDS_COOKIECUTTER_KEY = "cookiecutter"
COMMANDS_MANAGE_KEY = "manage"
COMMANDS_COMPONENTS_KEY = "components"
COMMANDS_PARAMETERS_KEY = "parameters"
COMMANDS_PARAMETERS_NAME_KEY = "name"
COMMANDS_PARAMETERS_DEFAULT_KEY = "default"
COMMANDS_PARAMETERS_TEMPLATE_KEY = "template"
COMMANDS_PARAMETERS_HELP_KEY = "help"
GIT_NAME_KEY = "git_name"
GIT_EMAIL_KEY = "git_email"
TEMPLATES_FNAME = "template.json"


class CommandsConfig:
    """Represents definitions of optional parameters for (sub-)commands
    create, manage, cookiecutter
    """

    # Static variable storing the command definitions
    __commands_dict: dict[str, Any] = {}

    def __init__(self) -> None:
        """Loads dictionary with command definitions, if not already present"""
        if not CommandsConfig.__commands_dict:
            CommandsConfig.__commands_dict = self.__load_commands_dict()
        self.__commands_dict = CommandsConfig.__commands_dict

    def __values(self, command: str, section: str) -> list[Any]:
        cmd_dict = self.__commands_dict[command]
        try:
            result_list = cmd_dict[section]
        except KeyError:
            result_list = []
        if not isinstance(result_list, list):
            raise TypeError(
                f"Section '{section}' for command '{command}' " "must contain a list"
            )

        return result_list

    def values_str(self, command: str, section: str) -> list[str]:
        """Obtain a section for a command from the json configuration

        Params:
            command: String specifying the command (create, manage,
                cookiecutter)
            section: String specifying the configuration section (template,
                parameters, components)
        Returns: List of strings containing the
            components of the configurations section, empty list if
            the section is not available
        """
        result_list = self.__values(command, section)

        if any(not isinstance(item, str) for item in result_list):
            raise TypeError(
                f"Section '{section}' for command '{command}' "
                "must contain a list of strings"
            )

        return result_list

    def values_dict(self, command: str, section: str) -> list[dict[str, Any]]:
        """Obtain a section for a command from the json configuration

        Params:
            command: String specifying the command (create, manage,
                cookiecutter)
            section: String specifying the configuration section (template,
                parameters, components)
        Returns: Dict objects containing the
            options/components of the configurations section, empty list if
            the section is not available
        """
        result_list = self.__values(command, section)
        if any(not isinstance(item, dict) for item in result_list):
            raise TypeError(
                f"Section '{section}' for command '{command}' "
                "must contain a list of dictionaries"
            )

        return result_list

    @staticmethod
    def __load_commands_dict() -> dict[str, Any]:
        """Load commands definition from package resource

        Returns:
            commands_dict: Dictionary representing commands.json
        """
        # Load commands.json with definitions for command-line arguments
        # -> sub-commands, their arguments, defaults and help messages
        commands_str = pkg.string(COMMANDS_FNAME)
        # Define context for substituting default values in the commands file
        # in order to be substituted with Jinja2
        # git user and email as default for author data
        name, email = CommandsConfig.git_user()
        context = {GIT_NAME_KEY: name, GIT_EMAIL_KEY: email}
        commands_str = Template(commands_str).render(**context)
        commands_dict = json.loads(commands_str)
        if not isinstance(commands_dict, dict) and any(
            not isinstance(k, str) for k in commands_dict
        ):
            raise TypeError(
                "commands.json must contain a dictionary of string keys / commands"
            )
        return cast(dict[str, Any], commands_dict)

    @staticmethod
    def git_user() -> tuple[str, str]:
        """Obtain git user name and email from git config.

        The function expects that the command 'git' is found on the PATH.

        Returns:
            name: String with git user name, empty string if no 'git' command
            email: String with git user email, empty string if no 'git' command
        """
        name = ""
        email = ""
        if shutil.which("git"):
            name = subprocess.check_output(
                ["git", "config", "user.name"],
                stderr=subprocess.STDOUT,
                encoding="utf-8",
            )
            email = subprocess.check_output(
                ["git", "config", "user.email"],
                stderr=subprocess.STDOUT,
                encoding="utf-8",
            )
        return name.strip(), email.strip()


class ProjectConfig:
    """Generate config dictionaries for template actions:
    create, manage, cookiecutter

    Supports a CLI for asking configuration values from the user in interactive
    mode.
    """

    def __init__(self, args: argparse.Namespace) -> None:
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

    def __param_dict(self, command: str) -> dict[str, Any]:
        """Generate project configuration for creating an instance of the
        devops template. Defines the context for rendering Jinja2 templates.

        Supports interactive mode.

        Params:
            command: String specifying the command
        Returns:
            param_dict: Dictionary with configurations
        """
        param_def_list = self.__cfg.values_dict(command, COMMANDS_PARAMETERS_KEY)
        param_key_list = [
            p[COMMANDS_PARAMETERS_NAME_KEY].replace("-", "_") for p in param_def_list
        ]
        # Define param dict for project context
        param_dict = {key: self.__args_dict[key] for key in param_key_list}
        # Overwrite default/specified values in interactive mode
        if (
            ARGUMENTS_INTERACTIVE_KEY in self.__args_dict
            and self.__args_dict[ARGUMENTS_INTERACTIVE_KEY]
        ):
            param_dict = self.__input(param_key_list, param_dict)
        return param_dict

    def __comp_list(self, command: str) -> list[str]:
        """Generate list of project components that will be installed according
        to template.json

        Supports interactive mode.

        Params:
            command: String specifying the command.
        Returns:
            comp_list: List of strings specifying template components
        """
        comp_def_list = self.__cfg.values_dict(command, COMMANDS_COMPONENTS_KEY)
        # Generate internal identifiers (keys) for component by their names
        comp_key_list = [
            c[COMMANDS_PARAMETERS_NAME_KEY].replace("-", "_") for c in comp_def_list
        ]
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
        if (
            ARGUMENTS_INTERACTIVE_KEY in self.__args_dict
            and self.__args_dict[ARGUMENTS_INTERACTIVE_KEY]
        ):
            comp_args = self.__input(comp_key_list, comp_args)
        # Translate flags (pos and neg) to positive list of components
        # Initialize with default components for command
        # Create a copy since the list will be extended
        comp_list = list(
            self.__cfg.values_str(command, COMMANDS_PARAMETERS_TEMPLATE_KEY)
        )
        for key in comp_key_list:
            # Whether to add the component by default (when no user flag has
            # been set)
            comp_default = comp_dict[key][COMMANDS_PARAMETERS_DEFAULT_KEY]
            # Negate the default boolean value if a flag has been set for the
            # component by the user)
            comp_add = not comp_default if comp_args[key] else comp_default
            if comp_add:
                comp_list.extend(comp_dict[key][COMMANDS_PARAMETERS_TEMPLATE_KEY])

        return comp_list

    def create(self) -> tuple[dict[str, Any], list[str]]:
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
        if not self.__args_dict[ARGUMENTS_PACKAGE_NAME_KEY]:
            # Slugify project_name and use as default for package_name
            project_slug = project_name.replace(" ", "_").replace("-", "_")
            project_slug = project_slug.lower()
            self.__args_dict[ARGUMENTS_PACKAGE_NAME_KEY] = project_slug

        # Parameters
        param_dict = self.__param_dict(command=COMMANDS_CREATE_KEY)
        # Set project name
        param_dict[ARGUMENTS_PROJECT_NAME_KEY] = project_name
        # Define project package name: slugify given package_name
        # Default package_name is defined above or given as CLI arg
        # and can be overwritten in interactive mode in __param_dict func
        # --> define project_slug based on package_name in param_dict var
        project_slug = param_dict[ARGUMENTS_PACKAGE_NAME_KEY]
        project_slug = project_slug.replace(" ", "_").replace("-", "_")
        param_dict[ARGUMENTS_PROJECT_SLUG_KEY] = project_slug.lower()

        # Components
        comp_list = self.__comp_list(command=COMMANDS_CREATE_KEY)

        return param_dict, comp_list

    def manage(self) -> tuple[dict[str, Any], list[str]]:
        """Generate project configuration for action 'manage'.

        Returns:
            param_dict: Dictionary with configurations for modifying an
                instance of the devops template.
            comp_list: List of template components that will be added to the
                template instance according to template.json
        """
        # Parameters
        param_dict = {ARGUMENTS_PROJECT_NAME_KEY: os.path.basename(self.project_dir)}

        # Components
        comp_list = self.__comp_list(command=COMMANDS_MANAGE_KEY)

        return param_dict, comp_list

    def cookiecutter(self) -> tuple[dict[str, Any], list[str]]:
        """Generate project configuration for action 'cookiecutter'.

        Returns:
            param_dict: Dictionary with configurations for creating a
                cookiecutter template from the devops template.
            comp_list: List of components that will be added to the
                cookiecutter template according to template.json
        """
        # Parameters
        param_dict = self.__param_dict(command=COMMANDS_COOKIECUTTER_KEY)
        # Set standard cookiecutter definition for project_slug
        project_slug = "".join(
            [
                "{{ ",
                f"cookiecutter.{ARGUMENTS_PROJECT_NAME_KEY}.lower()",
                ".replace(' ', '_')",
                ".replace('-', '_')",
                " }}",
            ]
        )
        param_dict[ARGUMENTS_PROJECT_SLUG_KEY] = project_slug

        # Components
        comp_list = self.__comp_list(command=COMMANDS_COOKIECUTTER_KEY)

        return param_dict, comp_list

    @staticmethod
    def __input(key_list: list[str], params: dict[str, Any]) -> dict[str, Any]:
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
            value_default = params[key]
            key_disp = key.replace("_", "-")
            if isinstance(value_default, bool):
                # Convert boolean value to string
                value_default = ARGUMENTS_YES_KEY if value_default else ARGUMENTS_NO_KEY
                value_user = input(f"{key_disp} [ {value_default} ] : ")
                # Convert string value_user to boolean
                params[key] = value_user == ARGUMENTS_YES_KEY
            else:
                value_user = input(f'{key_disp} [ "{value_default}" ] : ')
                # Keep initial value if user just presses enter
                # use the user input otherwise
                params[key] = value_default if value_user == "" else value_user
        return params
