import unittest
import os
from argparse import Namespace
from devopstemplate.config import ProjectConfig


class ProjectConfigTest(unittest.TestCase):

    def test_create(self):
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.projectname = 'test'
        args_ns.project_version = '0.1.0'
        args_ns.project_url = ''
        args_ns.project_description = ''
        args_ns.author_name = 'full name'
        args_ns.author_email = 'full.name@mail.com'
        args_ns.add_scripts_dir = True
        args_ns.add_docs_dir = False
        args_ns.no_gitignore_file = False
        args_ns.no_readme_file = False
        args_ns.no_sonar = False
        args_ns.overwrite_exists = False
        args_ns.skip_exists = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.version = False
        args_ns.dry_run = False
        args_ns.interactive = False

        params_ref = {'project_name': 'test',
                      'project_slug': 'test',
                      'project_version': '0.1.0',
                      'project_url': '',
                      'project_description': '',
                      'author_name': 'full name',
                      'author_email': 'full.name@mail.com',
                      'add_scripts_dir': True,
                      'add_docs_dir': False,
                      'no_gitignore_file': False,
                      'no_readme_file': False,
                      'no_sonar': False}

        config = ProjectConfig(args_ns)
        params = config.create()

        self.assertFalse(config.dry_run)
        self.assertFalse(config.skip_exists)
        self.assertFalse(config.overwrite_exists)
        self.assertEqual(config.project_dir, args_ns.project_dir)
        self.assertEqual(params, params_ref)

    def test_manage(self):
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.add_scripts_dir = True
        args_ns.add_docs_dir = False
        args_ns.add_gitignore_file = False
        args_ns.add_readme_file = False
        args_ns.add_sonar = False
        args_ns.overwrite_exists = False
        args_ns.skip_exists = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.version = False
        args_ns.dry_run = False

        project_name = os.path.dirname(args_ns.project_dir)
        project_slug = project_name.lower().replace(' ', '_').replace('-', '_')
        params_ref = {'add_scripts_dir': True,
                      'add_docs_dir': False,
                      'add_gitignore_file': False,
                      'add_readme_file': False,
                      'add_sonar': False,
                      'project_name': project_name,
                      'project_slug': project_slug,
                      'project_description': ''}

        config = ProjectConfig(args_ns)
        params = config.manage()

        self.assertFalse(config.dry_run)
        self.assertFalse(config.skip_exists)
        self.assertFalse(config.overwrite_exists)
        self.assertEqual(config.project_dir, args_ns.project_dir)
        self.assertEqual(params, params_ref)

    def test_cookiecutter(self):
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.project_name = 'test'
        args_ns.project_version = '0.1.0'
        args_ns.project_url = ''
        args_ns.project_description = ''
        args_ns.author_name = 'full name'
        args_ns.author_email = 'full.name@mail.com'
        args_ns.overwrite_exists = False
        args_ns.skip_exists = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.version = False
        args_ns.dry_run = False
        args_ns.interactive = False

        project_slug = ''.join(["{{ ",
                                "cookiecutter.project_name.lower()",
                                ".replace(' ', '_')",
                                ".replace('-', '_')",
                                " }}"])
        params_ref = {'project_name': 'test',
                      'project_slug': project_slug,
                      'project_version': '0.1.0',
                      'project_url': '',
                      'project_description': '',
                      'author_name': 'full name',
                      'author_email': 'full.name@mail.com'}

        config = ProjectConfig(args_ns)
        params = config.cookiecutter()

        self.assertFalse(config.dry_run)
        self.assertFalse(config.skip_exists)
        self.assertFalse(config.overwrite_exists)
        self.assertEqual(config.project_dir, args_ns.project_dir)
        self.assertEqual(params, params_ref)


if __name__ == "__main__":
    unittest.main()
