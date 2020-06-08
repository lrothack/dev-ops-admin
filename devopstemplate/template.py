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

        # Create source directory (if not present)
        self.__mkdir(projectname)

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
            os.makedirs(project_dpath)

    def __copy(self, pkg_fname, project_fname):
        """Copy file-like objects according to overwrite and skip class members

        Params:
            pkg_fname: String specifying the file in the distribution package
            project_fname: String specifying the target file in the project
        Raises:
            FileNotFoundError: If pkg_fname is not available
            FileExistsError: If project_fname already exists in the project
                and skip-exists=False, overwrite-exists=False
        """
        logger = logging.getLogger('DevOpsTemplate.__copy')
        if not pkg.exists(pkg_fname):
            raise FileNotFoundError(f'File {pkg_fname} not available in '
                                    'distribution package')
        project_fpath = os.path.join(self.__projectdir, project_fname)
        if os.path.exists(project_fpath) and self.__skip:
            logger.warning('File %s exists, skipping', project_fpath)
            return
        if os.path.exists(project_fpath) and not self.__overwrite:
            raise FileExistsError(f'File {project_fpath} already exists, exit.'
                                  ' (use --skip-exists or --overwrite-exists'
                                  ' to control behavior)')
        with pkg.stream(pkg_fname) as pkg_fh:
            with open(project_fpath, 'wb') as project_fh:
                shutil.copyfileobj(pkg_fh, project_fh)
        logger.debug('template:%s  ->  project:%s', pkg_fname, project_fpath)

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
