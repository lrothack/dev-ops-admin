"""Create new projects from template and administer existing projects
- defines which files will be installed for specific user requests
- defines how files will be installed according to user requests
"""
import os
import shutil
import logging

import devopstemplate
import devopstemplate.pkg as pkg


class DevOpsTemplate():

    def __init__(self, projectdirectory='.',
                 overwrite_exists=False, skip_exists=False):
        logger = logging.getLogger('DevOpsTemplate.__init__')
        if not os.path.exists(projectdirectory):
            logger.info('creating project directory: %s', projectdirectory)
            os.makedirs(projectdirectory)
        self.__projectdir = projectdirectory
        self.__overwrite = overwrite_exists
        self.__skip = skip_exists
        template_index_list = pkg.string_list('template.index')
        logger.debug('template index:\n%s', '\n'.join(template_index_list))

    def create(self, projectname, add_scripts, add_docs,
               no_gitignore, no_readme, no_sonar, no_docker):
        logger = logging.getLogger('DevOpsTemplate.create')
        logger.info('Create project from template %s',
                    devopstemplate.__version__)
        logger.info('Project name: %s', projectname)
        logger.info('  scripts directory: %s', add_scripts)
        logger.info('  docs directory:    %s', add_docs)
        logger.info('  .gitignore file:   %s', not no_gitignore)
        logger.info('  README.md file:    %s', not no_readme)
        logger.info('  SonarQube support: %s', not no_sonar)
        logger.info('  Docker support:    %s', not no_docker)

    def manage(self, add_gitignore, add_readme, add_scripts,
               add_docs, add_sonar, add_docker):
        pass

    def __copy(self, pkg_fname, project_fname):
        """Copy file-like objects according to overwrite and skip class members

        Params:
            pkg_fname: String specifying the file in the distribution package
            project_fname: String specifying the target file in the project
        """
        logger = logging.getLogger(f'{__name__}:__copy')
        if not pkg.exists(pkg_fname):
            raise FileNotFoundError(f'File {pkg_fname} not available in '
                                    'distribution package')
        if os.path.exists(project_fname) and self.__skip:
            logger.warning('File %s exists, skipping', project_fname)
            return
        if os.path.exists(project_fname) and not self.__overwrite:
            raise FileExistsError(f'File {project_fname} already exists, exit.'
                                  ' (use --skip-exists or --overwrite-exists'
                                  ' to control behavior)')
        with pkg.stream(pkg_fname) as pkg_fh:
            with open(project_fname, 'wb') as project_fh:
                shutil.copyfileobj(pkg_fh, project_fh)
        logger.debug('template:%s  ->  project:%s', pkg_fname, project_fname)

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
