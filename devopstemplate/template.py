"""Create new projects from template and administer existing projects
    - defines which files will be installed for specific user requests
    - defines how files will be installed according to user requests
"""
import os
import shutil
import logging
import json
from jinja2 import Environment, PackageLoader, select_autoescape
from jinja2 import Template
# import devopstemplate
import devopstemplate.pkg as pkg


class DevOpsTemplate():

    def __init__(self, projectdirectory='.',
                 overwrite_exists=False, skip_exists=False, dry_run=False):
        # logger = logging.getLogger('DevOpsTemplate.__init__')
        self.__projectdir = projectdirectory
        self.__overwrite = overwrite_exists
        self.__skip = skip_exists
        self.__dry_run = dry_run
        with pkg.stream('template.json') as fh:
            self.__template_dict = json.load(fh)
        self.__template_dname = 'template'
        self.__env = Environment(loader=PackageLoader(__name__,
                                                      self.__template_dname),
                                 autoescape=select_autoescape(default=True))
        # Create project base directory if not present
        self.__mkdir(projectdirectory)

    def create(self, projectconfig):
        logger = logging.getLogger('DevOpsTemplate.create')
        logger.info('Create project from template')
        logger.info('Project name: %s', projectconfig['project_name'])
        logger.debug('  scripts directory: %s',
                     projectconfig['add_scripts_dir'])
        logger.debug('  docs directory:    %s',
                     projectconfig['add_docs_dir'])
        logger.debug('  .gitignore file:   %s',
                     not projectconfig['no_gitignore_file'])
        logger.debug('  README.md file:    %s',
                     not projectconfig['no_readme_file'])
        logger.debug('  SonarQube support: %s',
                     not projectconfig['no_sonar'])
        logger.debug('  Docker support:    %s',
                     not projectconfig['no_docker'])

        # Install 'common' files
        common_file_list = self.__template_dict['common']
        for template_fpath in common_file_list:
            project_fpath = Template(template_fpath).render(**projectconfig)
            self.__render(template_fpath, project_fpath)

    def manage(self, add_gitignore, add_readme, add_scripts,
               add_docs, add_sonar, add_docker):
        pass

    def __mkdir(self, project_dname):
        """Create a directory within the project if not present

        Params:
            project_dname: String specifying the name of the directory
        """
        logger = logging.getLogger('DevOpsTemplate.__mkdir')
        project_dpath = os.path.join(self.__projectdir, project_dname)
        if not os.path.exists(project_dpath):
            logger.info('creating directory: %s', project_dpath)
            if not self.__dry_run:
                os.makedirs(project_dpath)
        else:
            logger.debug('directory %s exists', project_dpath)

    def __render(self, pkg_fname, project_fname, context):
        """Render template to project according to overwrite/skip class members
        The source file will be used as a Jinja2 template and rendered before
        the rendering result will be written to the target file.

        Params:
            pkg_fname: String specifying the file in the distribution package
            project_fname: String specifying the target file in the project
            context: Dictionary with the context for rendering Jinja2 templates
        Raises:
            FileNotFoundError: If pkg_fname is not available
            FileExistsError: If project_fname already exists in the project
                and skip-exists=False, overwrite-exists=False
        """
        logger = logging.getLogger('DevOpsTemplate.__render')
        pkg_fpath = os.path.join(self.__template_dname, pkg_fname)
        if not pkg.exists(pkg_fpath):
            raise FileNotFoundError(f'File {pkg_fpath} not available in '
                                    'distribution package')
        project_fpath = os.path.join(self.__projectdir, project_fname)
        if os.path.exists(project_fpath) and self.__skip:
            logger.warning('File %s exists, skipping', project_fpath)
            return
        if os.path.exists(project_fpath) and not self.__overwrite:
            raise FileExistsError(f'File {project_fpath} already exists, exit.'
                                  ' (use --skip-exists or --overwrite-exists'
                                  ' to control behavior)')
        if not self.__dry_run:
            # Create parent directories if not present
            parent_dname = os.path.dirname(project_fpath)
            if not os.path.exists(parent_dname):
                os.makedirs(parent_dname)
            # Copy file in binary mode
            # with pkg.stream(pkg_fname) as pkg_fh:
            #     with open(project_fpath, 'wb') as project_fh:
            #         shutil.copyfileobj(pkg_fh, project_fh)
            template = self.__env.get_template(pkg_fname)
            with open(project_fpath, 'w') as project_fh:
                template.stream(**context).dump(project_fh)
        logger.debug('template:%s  ->  project:%s', pkg_fname, project_fpath)

    def __render_file(self):
        pass

    def __render_string(self, contents):
        return Template(contents)

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
