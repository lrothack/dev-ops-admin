import unittest
import os
from argparse import Namespace
from devopstemplate.config import ProjectConfig


class ProjectConfigTest(unittest.TestCase):

    def test_create(self):
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.package_name = 'test-Project'
        args_ns.project_version = '0.1.0'
        args_ns.project_url = ''
        args_ns.project_description = ''
        args_ns.author_name = 'full name'
        args_ns.author_email = 'full.name@mail.com'
        args_ns.no_gitignore_file = False
        args_ns.no_sonar = False
        args_ns.overwrite_exists = False
        args_ns.skip_exists = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.version = False
        args_ns.dry_run = False
        args_ns.interactive = False

        params_ref = {'project_name': os.path.basename(os.getcwd()),
                      'package_name': 'test-Project',
                      'project_slug': 'test_project',
                      'project_version': '0.1.0',
                      'project_url': '',
                      'project_description': '',
                      'author_name': 'full name',
                      'author_email': 'full.name@mail.com'}
        comps_ref = ['src',
                     'tests',
                     'make',
                     'setuptools',
                     'readme',
                     'docker',
                     'git',
                     'sonar']

        config = ProjectConfig(args_ns)
        param_dict, comp_list = config.create()

        self.assertFalse(config.dry_run)
        self.assertFalse(config.skip_exists)
        self.assertFalse(config.overwrite_exists)
        self.assertEqual(config.project_dir, os.getcwd())
        self.assertEqual(param_dict, params_ref)
        self.assertEqual(comp_list, comps_ref)

        # Test with --no-sonar flag
        args_ns.no_sonar = True
        config = ProjectConfig(args_ns)
        param_dict, comp_list = config.create()
        self.assertEqual(param_dict, params_ref)
        self.assertEqual(comp_list, comps_ref[:-1])

        # Test without package_name
        args_ns.no_sonar = False
        args_ns.package_name = None
        config = ProjectConfig(args_ns)
        param_dict, comp_list = config.create()
        project_name = os.path.basename(os.getcwd())
        project_slug = project_name.replace(' ', '_').replace('-', '_')
        project_slug = project_slug.lower()
        params_ref['package_name'] = project_slug
        params_ref['project_slug'] = project_slug
        self.assertEqual(param_dict, params_ref)
        self.assertEqual(comp_list, comps_ref)

    def test_manage(self):
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.add_gitignore_file = True
        args_ns.add_sonar = True
        args_ns.overwrite_exists = False
        args_ns.skip_exists = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.version = False
        args_ns.dry_run = False

        params_ref = {'project_name': os.path.basename(os.getcwd())}
        comps_ref = ['git',
                     'sonar']

        config = ProjectConfig(args_ns)
        param_dict, comp_list = config.manage()

        self.assertFalse(config.dry_run)
        self.assertFalse(config.skip_exists)
        self.assertFalse(config.overwrite_exists)
        self.assertEqual(config.project_dir, os.getcwd())
        self.assertEqual(param_dict, params_ref)
        self.assertEqual(comp_list, comps_ref)

        # Test without --add-sonar flag
        args_ns.add_sonar = False
        config = ProjectConfig(args_ns)
        param_dict, comp_list = config.manage()
        self.assertEqual(param_dict, params_ref)
        self.assertEqual(comp_list, comps_ref[:-1])

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
        comps_ref = ['src',
                     'tests',
                     'make',
                     'setuptools',
                     'git',
                     'readme',
                     'docker',
                     'sonar']

        config = ProjectConfig(args_ns)
        param_dict, comp_list = config.cookiecutter()

        self.assertFalse(config.dry_run)
        self.assertFalse(config.skip_exists)
        self.assertFalse(config.overwrite_exists)
        self.assertEqual(config.project_dir,
                         os.path.abspath(args_ns.project_dir))
        self.assertEqual(param_dict, params_ref)
        self.assertEqual(comp_list, comps_ref)


if __name__ == "__main__":
    unittest.main()
