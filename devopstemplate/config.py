"""Defines template creation and modification wrt user configurations.
"""

import os


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
        self.project_dir = args.project_dir
        self.overwrite_exists = args.overwrite_exists
        self.skip_exists = args.skip_exists
        self.dry_run = args.dry_run

    def create(self):
        """Generate project configuration for action 'create'.

        Supports interactive mode.

        Returns:
            params: Dictionary with configurations for creating an instance
                of the devops template.
        """
        key_list = ['project_version',
                    'project_url',
                    'project_description',
                    'author_name',
                    'author_email',
                    'add_scripts_dir',
                    'add_docs_dir',
                    'no_gitignore_file',
                    'no_readme_file',
                    'no_sonar']
        # Define configurate dict for creating project
        params = {key: self.__args_dict[key] for key in key_list}
        # Set project name
        params['project_name'] = self.__args_dict['projectname']
        # Define project package name
        project_slug = self.__args_dict['projectname']
        project_slug = project_slug.replace(' ', '_').replace('-', '_')
        params['project_slug'] = project_slug.lower()
        if self.__args_dict['interactive']:
            params = self.__input(key_list, params)
        return params

    def manage(self):
        """Generate project configuration for action 'manage'.

        Returns:
            params: Dictionary with configurations for modifying an instance
                of the devops template.
        """
        key_list = ['add_scripts_dir',
                    'add_docs_dir',
                    'add_gitignore_file',
                    'add_readme_file',
                    'add_sonar']
        # Define configurate dict for creating project
        params = {key: self.__args_dict[key] for key in key_list}
        # Set project name
        params['project_name'] = os.path.dirname(self.project_dir)
        # Define project package name
        project_slug = params['project_name']
        project_slug = project_slug.replace(' ', '_').replace('-', '_')
        params['project_slug'] = project_slug.lower()
        params['project_description'] = ''
        return params

    def cookiecutter(self):
        """Generate project configuration for action 'cookiecutter'.

        Returns:
            params: Dictionary with configurations for creating a cookiecutter
                template from the devops template.
        """
        key_list = ['project_name',
                    'project_version',
                    'project_url',
                    'project_description',
                    'author_name',
                    'author_email']
        # Define configurate dict for creating project
        params = {key: self.__args_dict[key] for key in key_list}
        if self.__args_dict['interactive']:
            params = self.__input(key_list, params)
        # Set standard cookiecutter definition for project_slug
        params['project_slug'] = ''.join(["{{ ",
                                          "cookiecutter.project_name.lower()",
                                          ".replace(' ', '_')",
                                          ".replace('-', '_')",
                                          " }}"])
        return params

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
