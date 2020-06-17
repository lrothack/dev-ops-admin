import os


class ProjectConfig():

    def __init__(self, args):
        # Generate dict from namespace attributes (save dict as a copy)
        self.__args_dict = dict(vars(args))
        self.project_dir = args.project_dir
        self.overwrite_exists = args.overwrite_exists
        self.skip_exists = args.skip_exists
        self.dry_run = args.dry_run

    def create(self):
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
        for key in key_list:
            value = params[key]
            key_disp = key.replace('_', '-')
            if isinstance(value, bool):
                value = 'y' if value else 'n'
                value_user = input(f'{key_disp} [ {value} ] : ')
                value_user = True if value_user == 'y' else False
            else:
                value_user = input(f'{key_disp} [ "{value}" ] : ')
                value_user = value if value_user == '' else value_user
            params[key] = value_user
        return params
