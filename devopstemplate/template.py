import os
import logging

import devopstemplate
import devopstemplate.pkg as pkg


class DevOpsTemplate():

    def __init__(self, projectdirectory='.'):
        logger = logging.getLogger('DevOpsTemplate.__init__')
        if not os.path.exists(projectdirectory):
            logger.info('creating project directory: %s', projectdirectory)
            os.makedirs(projectdirectory)
        self.__projectdir = projectdirectory
        template_index = pkg.string('template.index')
        template_index_list = template_index.splitlines()
        logger.debug(template_index_list)

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
